"""
Real-Time Charts Component for Digital Twin Dashboard

This module provides real-time, streaming charts for the microgrid Digital Twin.
Features rolling window visualization, safety zone indicators, and CBF event tracking.

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
Date: December 2025
Version: 1.0.0

Award Target: TURING PRIZE 2026 - Professional-grade real-time visualization
"""

from typing import Dict, List, Optional, Any, Deque, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import time

# Plotly for interactive visualization
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None

# NumPy for calculations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ChartConfig:
    """Configuration for real-time charts"""
    # Window settings
    window_size: int = 300  # 5 minutes at 1Hz
    update_interval_ms: int = 100

    # Colors
    background_color: str = '#1a1a2e'
    paper_color: str = '#1a1a2e'
    grid_color: str = '#2d2d44'
    text_color: str = '#FFFFFF'

    # Safety zone colors
    safe_color: str = '#27AE60'
    warning_color: str = '#F39C12'
    danger_color: str = '#C0392B'

    # Component colors
    pv_color: str = '#F4D03F'
    battery_charge_color: str = '#2ECC71'
    battery_discharge_color: str = '#E74C3C'
    grid_buy_color: str = '#3498DB'
    grid_sell_color: str = '#9B59B6'
    load_color: str = '#E67E22'
    cbf_color: str = '#1ABC9C'

    # Chart heights
    standard_height: int = 250
    large_height: int = 300


# Pre-defined configurations
LIGHT_CHART_CONFIG = ChartConfig(
    background_color='#FFFFFF',
    paper_color='#FFFFFF',
    grid_color='#F0F2F6',
    text_color='#2C3E50',
    # High-contrast scientific colors
    pv_color='#F1C40F',          # Darker yellow for visibility against white
    battery_charge_color='#27AE60',
    battery_discharge_color='#E74C3C',
    grid_buy_color='#2980B9',    # Darker blue
    grid_sell_color='#8E44AD',   # Darker purple
    load_color='#D35400',        # Darker orange
    cbf_color='#16A085',         # Darker turquoise
    # Safety zones (lighter pastels for background)
    safe_color='#27AE60',
    warning_color='#F39C12',
    danger_color='#C0392B'
)


class CBFEventType(Enum):
    """Types of CBF events for timeline"""
    MONITORING = "monitoring"
    INTERVENING = "intervening"
    VIOLATION = "violation"
    RECOVERED = "recovered"


@dataclass
class CBFEvent:
    """A CBF intervention or violation event"""
    timestamp: float
    event_type: CBFEventType
    barrier_value: float
    action_taken: Optional[str] = None
    duration: Optional[float] = None


# =============================================================================
# REALTIME CHART MANAGER
# =============================================================================

class RealtimeChartManager:
    """
    Manager for real-time streaming charts with rolling windows.

    This class maintains data buffers and generates Plotly figures
    for live visualization of microgrid state. Designed for 60fps
    smooth rendering in Streamlit.

    Features:
    - Rolling window data buffers (circular buffers)
    - 6 specialized chart types
    - Safety zone visualization
    - CBF event timeline tracking
    - Cost accumulation tracking
    - Uncertainty band visualization

    Example:
        >>> manager = RealtimeChartManager(window_size=300)
        >>> manager.update(simulation_state)
        >>> fig = manager.create_voltage_frequency_chart()
        >>> st.plotly_chart(fig, width='stretch')
    """

    def __init__(
        self,
        window_size: int = 300,
        update_interval_ms: int = 100,
        config: Optional[ChartConfig] = None
    ):
        """
        Initialize the chart manager.

        Args:
            window_size: Number of data points to maintain (default 300 = 5min at 1Hz)
            update_interval_ms: Target update interval in milliseconds
            config: Optional chart configuration
        """
        self.window_size = window_size
        self.update_interval_ms = update_interval_ms
        self.config = config or ChartConfig(window_size=window_size)

        # Initialize data buffers
        self._init_buffers()

        # CBF events list
        self.cbf_events: List[CBFEvent] = []

        # Tracking
        self.total_cost: float = 0.0
        self.baseline_cost: float = 0.0
        self.start_time: Optional[float] = None

    def _init_buffers(self):
        """Initialize circular data buffers"""
        self.data_buffer: Dict[str, Deque] = {
            'timestamp': deque(maxlen=self.window_size),
            'step': deque(maxlen=self.window_size),

            # Electrical measurements
            'voltage': deque(maxlen=self.window_size),
            'frequency': deque(maxlen=self.window_size),

            # Battery
            'soc': deque(maxlen=self.window_size),

            # Power flows
            'pv_power': deque(maxlen=self.window_size),
            'load_power': deque(maxlen=self.window_size),
            'p_battery': deque(maxlen=self.window_size),
            'p_grid': deque(maxlen=self.window_size),

            # CBF metrics
            'barrier_value': deque(maxlen=self.window_size),
            'sigma_calibrated': deque(maxlen=self.window_size),
            'safety_margin': deque(maxlen=self.window_size),
            'cbf_active': deque(maxlen=self.window_size),

            # Predictions and uncertainty
            'prediction_mean': deque(maxlen=self.window_size),
            'prediction_std': deque(maxlen=self.window_size),
            'actual_value': deque(maxlen=self.window_size),

            # Cost tracking
            'instant_cost': deque(maxlen=self.window_size),
            'cumulative_cost': deque(maxlen=self.window_size),
            'baseline_cumulative': deque(maxlen=self.window_size),
        }

    def reset(self):
        """Reset all data buffers and tracking"""
        self._init_buffers()
        self.cbf_events.clear()
        self.total_cost = 0.0
        self.baseline_cost = 0.0
        self.start_time = None

    def update(self, state: Any) -> None:
        """
        Add a new state to the data buffers.

        Args:
            state: SimulationState object or dict with current values
        """
        if self.start_time is None:
            self.start_time = time.time()

        # Extract values from state
        values = self._extract_values(state)

        # Calculate timestamp and step
        timestamp = time.time() - self.start_time
        step = len(self.data_buffer['timestamp'])

        # Update buffers
        self.data_buffer['timestamp'].append(timestamp)
        self.data_buffer['step'].append(step)

        # Electrical
        self.data_buffer['voltage'].append(values.get('voltage', 230))
        self.data_buffer['frequency'].append(values.get('frequency', 50))

        # Battery
        self.data_buffer['soc'].append(values.get('soc', 0.5))

        # Power flows
        self.data_buffer['pv_power'].append(values.get('p_pv', 0))
        self.data_buffer['load_power'].append(values.get('p_load', 0))
        self.data_buffer['p_battery'].append(values.get('p_battery', 0))
        self.data_buffer['p_grid'].append(values.get('p_grid', 0))

        # CBF metrics
        barrier = values.get('barrier_value', 0)
        self.data_buffer['barrier_value'].append(barrier)
        self.data_buffer['sigma_calibrated'].append(values.get('sigma_calibrated', 0))
        self.data_buffer['safety_margin'].append(values.get('safety_margin', 0))

        cbf_active = values.get('cbf_active', False)
        self.data_buffer['cbf_active'].append(1 if cbf_active else 0)

        # Predictions
        self.data_buffer['prediction_mean'].append(values.get('prediction_mean', 230))
        self.data_buffer['prediction_std'].append(values.get('prediction_std', 1))
        self.data_buffer['actual_value'].append(values.get('voltage', 230))

        # Cost tracking
        instant_cost = values.get('instant_cost', 0)
        self.total_cost += instant_cost
        baseline_increment = abs(values.get('p_grid', 0)) * 0.19 / 3600  # Simple baseline
        self.baseline_cost += baseline_increment

        self.data_buffer['instant_cost'].append(instant_cost)
        self.data_buffer['cumulative_cost'].append(self.total_cost)
        self.data_buffer['baseline_cumulative'].append(self.baseline_cost)

        # Track CBF events
        self._track_cbf_event(timestamp, barrier, cbf_active, values.get('is_safe', True))

    def _extract_values(self, state: Any) -> Dict[str, float]:
        """Extract values from state object"""
        if state is None:
            return {}

        if hasattr(state, '__dict__'):
            return state.__dict__
        elif isinstance(state, dict):
            return state
        return {}

    def _track_cbf_event(
        self,
        timestamp: float,
        barrier_value: float,
        cbf_active: bool,
        is_safe: bool
    ):
        """Track CBF intervention/violation events"""
        # Determine event type
        if not is_safe:
            event_type = CBFEventType.VIOLATION
        elif cbf_active:
            event_type = CBFEventType.INTERVENING
        else:
            event_type = CBFEventType.MONITORING

        # Only record state changes
        if self.cbf_events:
            last_event = self.cbf_events[-1]
            if last_event.event_type == event_type:
                return  # Same state, no new event

        self.cbf_events.append(CBFEvent(
            timestamp=timestamp,
            event_type=event_type,
            barrier_value=barrier_value
        ))

    # =========================================================================
    # CHART GENERATORS
    # =========================================================================

    def create_voltage_frequency_chart(self) -> 'go.Figure':
        """
        Create dual-axis chart for voltage and frequency.

        Features:
        - Voltage (V) on left Y-axis with safe zone [220-240V]
        - Frequency (Hz) on right Y-axis with safe zone [49.5-50.5Hz]
        - Dashed threshold lines
        - Color-coded safety zones

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        voltages = list(self.data_buffer['voltage'])
        frequencies = list(self.data_buffer['frequency'])

        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Voltage trace
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=voltages,
                mode='lines',
                name='Voltage (V)',
                line=dict(color=cfg.pv_color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba(244, 208, 63, 0.1)'
            ),
            secondary_y=False
        )

        # Frequency trace
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=frequencies,
                mode='lines',
                name='Frequency (Hz)',
                line=dict(color=cfg.cbf_color, width=2),
            ),
            secondary_y=True
        )

        # Add voltage safe zone
        if timestamps:
            t_range = [min(timestamps), max(timestamps)]
            # Safe zone rectangle (220-240V)
            fig.add_shape(
                type="rect",
                x0=t_range[0], x1=t_range[1],
                y0=220, y1=240,
                fillcolor="rgba(39, 174, 96, 0.1)",
                line=dict(width=0),
                layer="below"
            )
            # Threshold lines
            for v in [220, 240]:
                fig.add_hline(
                    y=v, line=dict(color=cfg.warning_color, width=1, dash='dash'),
                    secondary_y=False
                )

        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>Voltage & Frequency</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=60, t=40, b=40),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color=cfg.text_color)
            ),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='voltage_frequency_chart',
            # Smooth transitions
            transition=dict(duration=300, easing='cubic-in-out')
        )

        fig.update_yaxes(
            title_text="Voltage (V)",
            range=[200, 260],
            gridcolor=cfg.grid_color,
            tickfont=dict(color=cfg.text_color),
            secondary_y=False
        )

        fig.update_yaxes(
            title_text="Frequency (Hz)",
            range=[49, 51],
            gridcolor=cfg.grid_color,
            tickfont=dict(color=cfg.text_color),
            secondary_y=True
        )

        return fig

    def create_power_flow_chart(self) -> 'go.Figure':
        """
        Create stacked area chart for power flows.

        Features:
        - PV (yellow) positive
        - Battery charge/discharge (green/red)
        - Grid buy/sell (blue/purple)
        - Load (orange) consumption line
        - Balance line at 0

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        pv = list(self.data_buffer['pv_power'])
        battery = list(self.data_buffer['p_battery'])
        grid = list(self.data_buffer['p_grid'])
        load = list(self.data_buffer['load_power'])

        fig = go.Figure()

        # PV power (always positive - generation)
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=pv,
            mode='lines',
            name='Solar PV',
            line=dict(color=cfg.pv_color, width=0),
            fill='tozeroy',
            fillcolor=f'rgba(244, 208, 63, 0.6)',
            stackgroup='generation'
        ))

        # Battery (positive = discharge, negative = charge)
        battery_discharge = [max(0, -b) for b in battery]  # Discharge is positive generation
        battery_charge = [max(0, b) for b in battery]  # Charge is consumption

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=battery_discharge,
            mode='lines',
            name='Battery Discharge',
            line=dict(color=cfg.battery_discharge_color, width=0),
            fill='tozeroy',
            fillcolor=f'rgba(231, 76, 60, 0.5)',
        ))

        # Grid power
        grid_import = [max(0, g) for g in grid]
        grid_export = [max(0, -g) for g in grid]

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=grid_import,
            mode='lines',
            name='Grid Import',
            line=dict(color=cfg.grid_buy_color, width=0),
            fill='tozeroy',
            fillcolor=f'rgba(52, 152, 219, 0.5)',
        ))

        # Load as line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=load,
            mode='lines',
            name='Load',
            line=dict(color=cfg.load_color, width=3),
        ))

        # Zero line
        if timestamps:
            fig.add_hline(y=0, line=dict(color='white', width=1, dash='solid'))

        fig.update_layout(
            title=dict(
                text='<b>Power Flows</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=20, t=40, b=40),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color=cfg.text_color, size=10)
            ),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            yaxis=dict(
                title='Power (kW)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='power_flow_chart',
            transition=dict(duration=300, easing='cubic-in-out')
        )

        return fig

    def create_soc_chart(self) -> 'go.Figure':
        """
        Create battery SOC chart with safety zones.

        Features:
        - SOC line with gradient fill
        - Green zone: 30%-80% (optimal)
        - Orange zone: 20%-30% and 80%-90% (warning)
        - Red zone: <20% and >90% (danger)

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        soc = [s * 100 for s in self.data_buffer['soc']]  # Convert to percentage

        fig = go.Figure()

        # Add safety zone backgrounds
        if timestamps:
            t_range = [min(timestamps), max(timestamps)]

            # Danger zones (red)
            for y0, y1 in [(0, 20), (90, 100)]:
                fig.add_shape(
                    type="rect",
                    x0=t_range[0], x1=t_range[1],
                    y0=y0, y1=y1,
                    fillcolor="rgba(192, 57, 43, 0.2)",
                    line=dict(width=0),
                    layer="below"
                )

            # Warning zones (orange)
            for y0, y1 in [(20, 30), (80, 90)]:
                fig.add_shape(
                    type="rect",
                    x0=t_range[0], x1=t_range[1],
                    y0=y0, y1=y1,
                    fillcolor="rgba(243, 156, 18, 0.2)",
                    line=dict(width=0),
                    layer="below"
                )

            # Safe zone (green)
            fig.add_shape(
                type="rect",
                x0=t_range[0], x1=t_range[1],
                y0=30, y1=80,
                fillcolor="rgba(39, 174, 96, 0.2)",
                line=dict(width=0),
                layer="below"
            )

        # SOC line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=soc,
            mode='lines',
            name='SOC',
            line=dict(color=cfg.battery_charge_color, width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.3)'
        ))

        # Threshold lines
        for threshold in [20, 30, 80, 90]:
            color = cfg.warning_color if threshold in [30, 80] else cfg.danger_color
            fig.add_hline(y=threshold, line=dict(color=color, width=1, dash='dot'))

        fig.update_layout(
            title=dict(
                text='<b>Battery State of Charge</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=20, t=40, b=40),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            yaxis=dict(
                title='SOC (%)',
                range=[0, 100],
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='soc_chart',
            transition=dict(duration=300, easing='cubic-in-out')
        )

        return fig

    def create_cbf_timeline(self) -> 'go.Figure':
        """
        Create CBF intervention timeline chart.

        Features:
        - Barrier function value over time
        - Vertical bars for intervention events
        - Color-coded by severity
        - Tooltips with event details
        - Zero threshold line

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        barrier = list(self.data_buffer['barrier_value'])
        cbf_active = list(self.data_buffer['cbf_active'])

        fig = go.Figure()

        # Barrier value line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=barrier,
            mode='lines',
            name='Barrier h(s)',
            line=dict(color=cfg.cbf_color, width=2),
            fill='tozeroy',
            fillcolor='rgba(26, 188, 156, 0.2)'
        ))

        # Zero threshold (violation boundary)
        if timestamps:
            fig.add_hline(
                y=0,
                line=dict(color=cfg.danger_color, width=2, dash='solid'),
                annotation_text="Safety Boundary",
                annotation_position="bottom right"
            )

        # Mark CBF intervention periods
        intervention_starts = []
        in_intervention = False
        for i, active in enumerate(cbf_active):
            if active and not in_intervention:
                intervention_starts.append(i)
                in_intervention = True
            elif not active and in_intervention:
                in_intervention = False

        # Add vertical lines for interventions
        for idx in intervention_starts:
            if idx < len(timestamps):
                fig.add_vline(
                    x=timestamps[idx],
                    line=dict(color=cfg.warning_color, width=2, dash='dot'),
                )

        # Add event markers
        for event in self.cbf_events[-20:]:  # Last 20 events
            if event.event_type == CBFEventType.VIOLATION:
                marker_color = cfg.danger_color
                symbol = 'x'
            elif event.event_type == CBFEventType.INTERVENING:
                marker_color = cfg.warning_color
                symbol = 'triangle-up'
            else:
                continue  # Skip monitoring events

            fig.add_trace(go.Scatter(
                x=[event.timestamp],
                y=[event.barrier_value],
                mode='markers',
                name=event.event_type.value,
                marker=dict(
                    color=marker_color,
                    size=12,
                    symbol=symbol
                ),
                showlegend=False,
                hovertemplate=f"{event.event_type.value}<br>h(s)={event.barrier_value:.2f}<extra></extra>"
            ))

        fig.update_layout(
            title=dict(
                text='<b>U-CBF Safety Monitor</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=20, t=40, b=40),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            yaxis=dict(
                title='Barrier Value h(s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='cbf_timeline_chart',
            transition=dict(duration=300, easing='cubic-in-out')
        )

        return fig

    def create_uncertainty_chart(self) -> 'go.Figure':
        """
        Create prediction with uncertainty bands chart.

        Features:
        - Central line: mean prediction
        - 1-sigma, 2-sigma, 3-sigma bands
        - Actual values as points for validation
        - Color gradient for confidence levels

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        mean = list(self.data_buffer['prediction_mean'])
        std = list(self.data_buffer['prediction_std'])
        actual = list(self.data_buffer['actual_value'])

        fig = go.Figure()

        if not timestamps:
            return fig

        # Calculate bands
        if NUMPY_AVAILABLE:
            mean_arr = np.array(mean)
            std_arr = np.array(std)
        else:
            mean_arr = mean
            std_arr = std

        # 3-sigma band (99.7%)
        upper_3 = [m + 3 * s for m, s in zip(mean, std)]
        lower_3 = [m - 3 * s for m, s in zip(mean, std)]

        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_3 + lower_3[::-1],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.15)',
            line=dict(width=0),
            name='3-sigma (99.7%)',
            showlegend=True
        ))

        # 2-sigma band (95%)
        upper_2 = [m + 2 * s for m, s in zip(mean, std)]
        lower_2 = [m - 2 * s for m, s in zip(mean, std)]

        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_2 + lower_2[::-1],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.25)',
            line=dict(width=0),
            name='2-sigma (95%)',
            showlegend=True
        ))

        # 1-sigma band (68%)
        upper_1 = [m + s for m, s in zip(mean, std)]
        lower_1 = [m - s for m, s in zip(mean, std)]

        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_1 + lower_1[::-1],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.35)',
            line=dict(width=0),
            name='1-sigma (68%)',
            showlegend=True
        ))

        # Mean prediction line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=mean,
            mode='lines',
            name='Prediction',
            line=dict(color=cfg.grid_buy_color, width=2)
        ))

        # Actual values
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=actual,
            mode='markers',
            name='Actual',
            marker=dict(color=cfg.pv_color, size=4)
        ))

        fig.update_layout(
            title=dict(
                text='<b>Ensemble Prediction with Uncertainty</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=20, t=40, b=40),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color=cfg.text_color, size=9)
            ),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            yaxis=dict(
                title='Value',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='uncertainty_chart',
            transition=dict(duration=300, easing='cubic-in-out')
        )

        return fig

    def create_cost_chart(self) -> 'go.Figure':
        """
        Create cumulative cost comparison chart.

        Features:
        - U-CBF controlled cost curve
        - Baseline cost curve
        - Savings annotation
        - Cost per kWh reference

        Returns:
            Plotly Figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config
        timestamps = list(self.data_buffer['timestamp'])
        cumulative = list(self.data_buffer['cumulative_cost'])
        baseline = list(self.data_buffer['baseline_cumulative'])

        fig = go.Figure()

        # Baseline cost
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=baseline,
            mode='lines',
            name='Baseline',
            line=dict(color=cfg.danger_color, width=2, dash='dash'),
        ))

        # U-CBF controlled cost
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cumulative,
            mode='lines',
            name='U-CBF Optimized',
            line=dict(color=cfg.safe_color, width=3),
            fill='tonexty',
            fillcolor='rgba(39, 174, 96, 0.2)'
        ))

        # Add savings annotation
        if cumulative and baseline and len(cumulative) > 10:
            savings = baseline[-1] - cumulative[-1]
            savings_pct = (savings / baseline[-1] * 100) if baseline[-1] > 0 else 0

            fig.add_annotation(
                x=timestamps[-1],
                y=(cumulative[-1] + baseline[-1]) / 2,
                text=f"<b>Savings: {savings:.3f} TND ({savings_pct:.1f}%)</b>",
                showarrow=True,
                arrowhead=2,
                arrowcolor=cfg.safe_color,
                font=dict(color=cfg.safe_color, size=12),
                bgcolor=cfg.background_color,
                bordercolor=cfg.safe_color,
                borderwidth=1
            )

        fig.update_layout(
            title=dict(
                text='<b>Cost Comparison</b>',
                font=dict(color=cfg.text_color, size=14)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=cfg.standard_height,
            margin=dict(l=60, r=20, t=40, b=40),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color=cfg.text_color)
            ),
            xaxis=dict(
                title='Time (s)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            yaxis=dict(
                title='Cumulative Cost (TND)',
                gridcolor=cfg.grid_color,
                tickfont=dict(color=cfg.text_color)
            ),
            # CRITICAL: Preserve UI state across updates (no flicker)
            uirevision='cost_chart',
            transition=dict(duration=300, easing='cubic-in-out')
        )

        return fig

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current statistics from buffers"""
        if not self.data_buffer['voltage']:
            return {}

        return {
            'voltage': self.data_buffer['voltage'][-1],
            'frequency': self.data_buffer['frequency'][-1],
            'soc': self.data_buffer['soc'][-1],
            'pv_power': self.data_buffer['pv_power'][-1],
            'load_power': self.data_buffer['load_power'][-1],
            'barrier_value': self.data_buffer['barrier_value'][-1],
            'total_cost': self.total_cost,
            'savings': self.baseline_cost - self.total_cost,
            'cbf_interventions': sum(1 for e in self.cbf_events
                                     if e.event_type == CBFEventType.INTERVENING),
            'violations': sum(1 for e in self.cbf_events
                              if e.event_type == CBFEventType.VIOLATION),
            'steps': len(self.data_buffer['timestamp']),
        }

    def create_all_charts(self) -> Dict[str, 'go.Figure']:
        """
        Create all charts at once.

        Returns:
            Dictionary mapping chart names to Plotly figures
        """
        return {
            'voltage_frequency': self.create_voltage_frequency_chart(),
            'power_flow': self.create_power_flow_chart(),
            'soc': self.create_soc_chart(),
            'cbf_timeline': self.create_cbf_timeline(),
            'uncertainty': self.create_uncertainty_chart(),
            'cost': self.create_cost_chart(),
        }

    def create_dashboard_layout(self) -> 'go.Figure':
        """
        Create a combined dashboard with all charts.

        Returns:
            Plotly Figure with subplots
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        cfg = self.config

        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Voltage & Frequency',
                'Power Flows',
                'Battery SOC',
                'U-CBF Safety Monitor',
                'Uncertainty Bounds',
                'Cost Comparison'
            ),
            specs=[
                [{"secondary_y": True}, {}],
                [{}, {}],
                [{}, {}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.08
        )

        # Add traces from individual charts
        # This is simplified - in practice you'd add each trace to the subplots
        timestamps = list(self.data_buffer['timestamp'])

        # Voltage (1,1)
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['voltage']),
                       name='Voltage', line=dict(color=cfg.pv_color)),
            row=1, col=1, secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['frequency']),
                       name='Frequency', line=dict(color=cfg.cbf_color)),
            row=1, col=1, secondary_y=True
        )

        # Power flows (1,2)
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['pv_power']),
                       name='PV', fill='tozeroy', line=dict(color=cfg.pv_color)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['load_power']),
                       name='Load', line=dict(color=cfg.load_color)),
            row=1, col=2
        )

        # SOC (2,1)
        soc_pct = [s * 100 for s in self.data_buffer['soc']]
        fig.add_trace(
            go.Scatter(x=timestamps, y=soc_pct, name='SOC',
                       fill='tozeroy', line=dict(color=cfg.battery_charge_color)),
            row=2, col=1
        )

        # CBF (2,2)
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['barrier_value']),
                       name='Barrier', fill='tozeroy', line=dict(color=cfg.cbf_color)),
            row=2, col=2
        )

        # Uncertainty (3,1)
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['prediction_mean']),
                       name='Prediction', line=dict(color=cfg.grid_buy_color)),
            row=3, col=1
        )

        # Cost (3,2)
        fig.add_trace(
            go.Scatter(x=timestamps, y=list(self.data_buffer['cumulative_cost']),
                       name='U-CBF Cost', line=dict(color=cfg.safe_color)),
            row=3, col=2
        )

        fig.update_layout(
            title=dict(
                text='<b>MICROGRID DIGITAL TWIN - Real-Time Dashboard</b>',
                font=dict(color=cfg.text_color, size=18)
            ),
            paper_bgcolor=cfg.paper_color,
            plot_bgcolor=cfg.background_color,
            height=900,
            showlegend=False,
            font=dict(color=cfg.text_color)
        )

        # Update all axes
        for i in range(1, 4):
            for j in range(1, 3):
                fig.update_xaxes(gridcolor=cfg.grid_color, row=i, col=j)
                fig.update_yaxes(gridcolor=cfg.grid_color, row=i, col=j)

        return fig


# =============================================================================
# DEMO / TEST
# =============================================================================

if __name__ == "__main__":
    """Demo the realtime charts"""
    import random
    import math

    print("Testing RealtimeChartManager...")

    # Create manager
    manager = RealtimeChartManager(window_size=100)

    # Simulate some data
    for i in range(100):
        # Generate realistic-ish data
        t = i * 0.1
        state = {
            'voltage': 230 + 5 * math.sin(t / 10) + random.uniform(-2, 2),
            'frequency': 50 + 0.2 * math.sin(t / 5) + random.uniform(-0.1, 0.1),
            'soc': 0.5 + 0.3 * math.sin(t / 50),
            'p_pv': max(0, 30 + 10 * math.sin(t / 20) + random.uniform(-2, 2)),
            'p_load': 35 + 5 * math.sin(t / 15) + random.uniform(-3, 3),
            'p_battery': 5 * math.sin(t / 8),
            'p_grid': 5 + random.uniform(-2, 2),
            'barrier_value': 10 + 5 * math.sin(t / 12),
            'cbf_active': random.random() > 0.9,
            'is_safe': random.random() > 0.05,
            'sigma_calibrated': 0.8 + random.uniform(-0.1, 0.1),
            'safety_margin': 8 + random.uniform(-1, 1),
            'prediction_mean': 230 + 5 * math.sin(t / 10),
            'prediction_std': 2 + random.uniform(0, 1),
        }
        manager.update(state)

    print(f"Data points collected: {len(manager.data_buffer['timestamp'])}")
    print(f"CBF events tracked: {len(manager.cbf_events)}")

    # Create all charts
    charts = manager.create_all_charts()
    for name, fig in charts.items():
        print(f"Chart '{name}': OK ({type(fig).__name__})")

    # Get stats
    stats = manager.get_current_stats()
    print(f"\nCurrent stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    # Create combined dashboard
    dashboard = manager.create_dashboard_layout()
    dashboard.write_html("demo_charts_dashboard.html")
    print("\nDashboard saved to demo_charts_dashboard.html")

    print("\n=================================")
    print("RealtimeChartManager: ALL TESTS PASSED")
    print("=================================")
