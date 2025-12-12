"""
Digital Twin Dashboard - Main Streamlit Application

Real-time visualization with smooth updates like hospital monitors.
Uses @st.fragment for partial updates without full page refresh.

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
Date: December 2025
Version: 2.0.0 - Smooth real-time updates (hospital monitor style)

Run with: streamlit run app/digital_twin_dashboard.py
"""

import streamlit as st
import time
import math
import random
from typing import Dict, Any
from datetime import datetime
import base64
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Microgrid Digital Twin - U-CBF Safety System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
try:
    from app.components.microgrid_schematic import (
        create_microgrid_schematic,
        create_battery_gauge,
        create_cbf_status_indicator,
        SCHEMATIC_VERSION  # For cache invalidation
    )
    SCHEMATIC_AVAILABLE = True
except ImportError:
    SCHEMATIC_AVAILABLE = False
    SCHEMATIC_VERSION = "unknown"

# Import SIMPLE animated schematic (fast, real-time capable)
try:
    from app.components.microgrid_simple import create_simple_microgrid
    SIMPLE_SCHEMATIC_AVAILABLE = True
except ImportError:
    SIMPLE_SCHEMATIC_AVAILABLE = False

try:
    from app.components.microgrid_refined import create_refined_microgrid
    REFINED_SCHEMATIC_AVAILABLE = True
except ImportError:
    REFINED_SCHEMATIC_AVAILABLE = False

try:
    from app.components.microgrid_html import render_microgrid_html
    HTML_SCHEMATIC_AVAILABLE = True
except ImportError:
    HTML_SCHEMATIC_AVAILABLE = False

# Import NEON schematic (high-tech dark theme with CSS animations)
try:
    from app.components.microgrid_neon import render_neon_microgrid
    NEON_SCHEMATIC_AVAILABLE = True
except ImportError:
    NEON_SCHEMATIC_AVAILABLE = False

# Import REALTIME schematic (flicker-free with JavaScript DOM updates)
try:
    from app.components.microgrid_realtime import render_realtime_microgrid
    REALTIME_SCHEMATIC_AVAILABLE = True
except ImportError:
    REALTIME_SCHEMATIC_AVAILABLE = False

try:
    from app.components.realtime_charts import RealtimeChartManager, ChartConfig
    CHARTS_AVAILABLE = True

    # Light theme config for charts
    LIGHT_CHART_CONFIG = ChartConfig(
        background_color='#FFFFFF',
        paper_color='#FFFFFF',
        grid_color='#E9ECEF',
        text_color='#2C3E50',
        safe_color='#27AE60',
        warning_color='#F39C12',
        danger_color='#E74C3C',
        pv_color='#F1C40F',
        battery_charge_color='#27AE60',
        battery_discharge_color='#E74C3C',
        grid_buy_color='#3498DB',
        grid_sell_color='#9B59B6',
        load_color='#E67E22',
        cbf_color='#1ABC9C'
    )
except ImportError:
    CHARTS_AVAILABLE = False
    LIGHT_CHART_CONFIG = None

try:
    from app.components.control_panel import (
        create_scenario_selector,
        create_parameter_panel,
        create_perturbation_injector,
        apply_control_panel_css,
        ScenarioType,
        UCBFParameters
    )
    CONTROLS_AVAILABLE = True
except ImportError:
    CONTROLS_AVAILABLE = False
    # Fallback enum if import fails (should not happen if file exists)
    class ScenarioType:
        NORMAL = "Normal"
        HEATWAVE = "Heatwave"
        CLOUD_COVER = "Cloud Cover"
        CYBER_ATTACK = "Cyber Attack"



# =============================================================================
# APPLY GLOBAL CSS (CYBERPUNK THEME)
# =============================================================================

st.markdown("""
<style>
/* ═════════════════════════════════════════════════════════════════════════════
   SCIENTIFIC LIGHT PREMIUM - GLOBAL STYLESHEET
   ═════════════════════════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
  --bg0: #f6f8fc;
  --bg1: #eef2ff;
  --ink: #0f172a;
  --muted: #475569;
  --glass: rgba(255,255,255,.62);
  --glass-strong: rgba(255,255,255,.78);
  --stroke: rgba(15,23,42,.14);
  --primary: #0ea5e9;
  
  --shadow-lg: 0 24px 60px rgba(2,6,23,.10);
  --shadow-md: 0 14px 30px rgba(2,6,23,.10);
  --shadow-sm: 0 10px 18px rgba(2,6,23,.08);
  
  --radius-lg: 18px;
  --radius-md: 14px;
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--ink);
}

/* ─── GLOBAL BACKGROUND ─────────────────────────────────────────────────── */
.stApp {
    background: #f8fafc;
    background-attachment: fixed;
}

/* ─── STREAMLIT COMPONENT OVERRIDES ────────────────────────────────────── */

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--stroke);
    box-shadow: 20px 0 40px rgba(0,0,0,0.02);
}

/* Plotly Charts & Metrics Containers -> Glass Cards */
[data-testid="stPlotlyChart"], [data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--glass-strong), var(--glass)) padding-box,
                linear-gradient(180deg, rgba(14,165,233,.35), rgba(15,23,42,.10)) border-box;
    border: 1px solid transparent;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(16px);
    padding: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stPlotlyChart"]:hover, [data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(2,6,23,.12);
}

/* Metric Text Styling */
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.75rem;
    color: var(--muted);
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    color: var(--ink);
}

/* Custom HTML Cards (Status, System Info) */
.premium-card {
    background: linear-gradient(180deg, rgba(255,255,255,.78), rgba(255,255,255,.54));
    border: 1px solid var(--stroke);
    border-radius: var(--radius-md);
    padding: 14px;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(12px);
    text-align: center;
}
.premium-card .label {
    color: var(--muted);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin-bottom: 4px;
}
.premium-card .value {
    color: var(--ink);
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 1.2rem;
}

/* Buttons */
.stButton > button {
    border-radius: 99px;
    font-weight: 600;
    border: 1px solid var(--stroke);
    background: white;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    border-color: var(--primary);
    color: var(--primary);
}

/* Headers */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.05em;
    color: var(--ink);
}

/* Remove default header/footer */
/* Remove default header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ─── WIDGET OVERRIDES (Remove Red) ────────────────────────────────────── */

/* Sliders (Blue Theme) */
div[data-baseweb="slider"] div[role="slider"] {
    background-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(14,165,233,.2) !important;
}
div[data-baseweb="slider"] div[data-testid="stTickBar"] > div {
    background: var(--primary) !important;
}
/* The track is tricky to target without specific classes, but often this works: */
div[data-baseweb="slider"] > div > div > div > div {
    background: var(--primary) !important;
}

/* Primary Button (Start -> Green) */
button[kind="primary"] {
    background: #22c55e !important;
    border: 1px solid #16a34a !important;
    box-shadow: 0 4px 12px rgba(34,197,94,0.2) !important;
    color: white !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    background: #16a34a !important;
    box-shadow: 0 6px 16px rgba(34,197,94,0.3) !important;
    transform: translateY(-1px);
}
button[kind="primary"]:focus {
    box-shadow: 0 0 0 4px rgba(34,197,94,0.2) !important;
    outline: none !important;
}

/* Secondary Button (Stop/Reset -> Neutral/Blue Legacy) */
button[kind="secondary"] {
    border: 1px solid var(--stroke) !important;
    background: white !important;
    color: var(--ink) !important;
}
button[kind="secondary"]:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    background: #f0f9ff !important;
}
button[kind="secondary"]:focus {
    box-shadow: 0 0 0 4px rgba(14,165,233,0.15) !important;
    border-color: var(--primary) !important;
    outline: none !important;
}

/* Remove Red Focus globally */
*:focus-visible {
    outline: 2px solid var(--primary) !important;
    outline-offset: 2px;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SIMULATION DATA GENERATOR (Smooth continuous data like real systems)
# =============================================================================

class SimulationDataGenerator:
    """Generates smooth, continuous simulation data like a real system"""

    def __init__(self):
        self.step = 0
        self.start_time = time.time()
        # Smooth state variables (no jumps)
        self._voltage = 230.0
        self._frequency = 50.0
        self._soc = 0.65
        self._pv = 25.0
        self._load = 35.0
        self._barrier = 12.0
        self._scenario = ScenarioType.NORMAL
        self._param_lambda = 0.1
        self._param_gamma = 1.0

    def set_scenario(self, scenario: ScenarioType):
        """Set the current active scenario"""
        self._scenario = scenario

    def set_params(self, params: Any):
        """Set U-CBF parameters"""
        if hasattr(params, 'lambda_val'):
            self._param_lambda = params.lambda_val
            self._param_gamma = params.gamma_val

    def get_state(self) -> Dict[str, Any]:
        """Generate next state with smooth transitions"""
        t = time.time() - self.start_time
        self.step += 1

        # Smooth sinusoidal variations (hospital monitor style)
        # Small incremental changes, not random jumps

        # Voltage: slow oscillation around 230V
        self._voltage += 0.1 * math.sin(t * 0.5) + random.gauss(0, 0.05)
        self._voltage = max(218, min(242, self._voltage))

        # Frequency: very stable with tiny variations
        self._frequency += 0.01 * math.sin(t * 0.3) + random.gauss(0, 0.005)
        self._frequency = max(49.2, min(50.8, self._frequency))

        # SOC: slow charge/discharge cycles
        soc_trend = 0.0005 * math.sin(t * 0.1)
        self._soc += soc_trend + random.gauss(0, 0.001)
        self._soc = max(0.15, min(0.95, self._soc))

        # PV: follows sun pattern with cloud variations
        hour = (t / 10) % 24  # Accelerated day cycle
        sun_factor = max(0, math.sin(math.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0
        self._pv += 0.5 * (35 * sun_factor - self._pv) * 0.1 + random.gauss(0, 0.2)
        self._pv = max(0, min(50, self._pv))

        # Load: base load with small variations
        self._load += 0.3 * math.sin(t * 0.2) + random.gauss(0, 0.1)
        self._load = max(20, min(50, self._load))

        # Scenario Overrides
        if self._scenario == ScenarioType.HEATWAVE:
            # High load, draining battery
            self._load = 45.0 + 5 * math.sin(t * 0.2)
            self._pv = 15.0 + 2 * math.sin(t * 0.1) # Less PV to stress system
        
        elif self._scenario == ScenarioType.CLOUD_COVER:
            # Drop PV to near zero
            self._pv = 5.0 + 2 * random.random()
            
        elif self._scenario == ScenarioType.CYBER_ATTACK:
            # FORCE UNSAFE STATE
            # 1. Voltage Violation
            self._voltage = 255.0 + 5 * math.sin(t) # > 242V Limit
            # 2. SOC Depletion
            self._soc = 0.05 + 0.01 * math.sin(t)   # < 15% Limit
            # 3. Frequency Instability
            self._frequency = 51.5 + 0.5 * math.sin(t*2)
            
            # Force unsafe barrier
            target_barrier = -5.0 # Explicitly negative
            self._barrier = -5.0 + random.gauss(0, 0.5)

        # Standard Barrier Logic (if not overridden by Cyber Attack)
        if self._scenario != ScenarioType.CYBER_ATTACK:
            # Barrier value: follows safety margin
            # h(x) = min(V_max - V, V - V_min, SOC - SOC_min, ...)
            # Simplified proxy:
            v_margin = min(242 - self._voltage, self._voltage - 218)
            soc_margin = (self._soc - 0.15) * 100 # Scale to comparable mag
            
            # Combine margins (soft min)
            target_barrier = min(v_margin, soc_margin)
            self._barrier += 0.2 * (target_barrier - self._barrier)

        # CBF Control Logic simulation
        # If barrier is low, CBF should Activate to push system back
        if self._barrier < 2.0: # Threshold for activation
            cbf_active = True
            # In a real closed loop, this would modify inputs. 
            # Here we just show the flag.
        else:
            cbf_active = False

        # Safety Check
        is_safe = self._barrier > 0

        # Power balance
        p_battery = self._pv - self._load + random.gauss(0, 0.5)
        p_grid = -p_battery * 0.3 + random.gauss(0, 0.3)

        return {
            'step': self.step,
            'timestamp': t,
            'voltage': self._voltage,
            'frequency': self._frequency,
            'soc': self._soc,
            'p_pv': self._pv,
            'p_load': self._load,
            'p_battery': p_battery,
            'p_grid': p_grid,
            'barrier_value': self._barrier,
            'cbf_active': cbf_active,
            'is_safe': is_safe,
            'safety_margin': max(0, self._barrier),
            'sigma_calibrated': 0.8 + 0.1 * math.sin(t * 0.4),
            'prediction_mean': self._voltage,
            'prediction_std': 1.5 + 0.5 * abs(math.sin(t * 0.3)),
            'tariff': 0.19 if 8 <= hour <= 20 else 0.11,
            'time_of_day': hour,
            'scenario': self._scenario.value if hasattr(self._scenario, 'value') else str(self._scenario)
        }


    def reset(self):
        """Reset to initial state"""
        self.__init__()


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.is_running = False
        st.session_state.simulation_speed = 1.0
        st.session_state.generator = SimulationDataGenerator()
        st.session_state.current_state = st.session_state.generator.get_state()

        # Initialize schematic cache (will be populated on first render)
        st.session_state.schematic_cache_key = None
        st.session_state.cached_schematic = None
        st.session_state.schematic_needs_full_render = True

        if CHARTS_AVAILABLE:
            config = LIGHT_CHART_CONFIG if LIGHT_CHART_CONFIG else ChartConfig()
            st.session_state.chart_manager = RealtimeChartManager(
                window_size=200,
                config=config
            )
            # Pre-populate with initial data
            for _ in range(100):
                st.session_state.chart_manager.update(
                    st.session_state.generator.get_state()
                )
        else:
            st.session_state.chart_manager = None


# =============================================================================
# REAL-TIME UPDATE FRAGMENT (Smooth updates without full refresh)
# =============================================================================

@st.fragment(run_every=0.5)  # Update every 500ms
def realtime_data_fragment():
    """Fragment that updates simulation data smoothly"""
    if st.session_state.is_running:
        # Generate multiple steps per update for smoother appearance
        steps_per_update = max(1, int(st.session_state.simulation_speed * 2))

        for _ in range(steps_per_update):
            st.session_state.current_state = st.session_state.generator.get_state()
            if st.session_state.chart_manager:
                st.session_state.chart_manager.update(st.session_state.current_state)


@st.fragment(run_every=0.5)
def realtime_status_fragment():
    """Fragment for status bar - updates smoothly"""
    state = st.session_state.current_state

    cols = st.columns(6)

    with cols[0]:
        status_icon = "🟢" if st.session_state.is_running else "⏹️"
        status_text = "RUNNING" if st.session_state.is_running else "STOPPED"
        speed_text = f"({st.session_state.simulation_speed}x)" if st.session_state.is_running else ""
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Status</div>
            <div class="value">{status_icon} {status_text} <span style="font-size:0.8rem;color:var(--muted);">{speed_text}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Step</div>
            <div class="value">{state['step']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        v = state['voltage']
        v_color = "#27AE60" if 220 <= v <= 240 else "#E74C3C"
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Voltage</div>
            <div class="value" style="color:{v_color};">{v:.1f} V</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        f = state['frequency']
        f_color = "#27AE60" if 49.5 <= f <= 50.5 else "#E74C3C"
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Frequency</div>
            <div class="value" style="color:{f_color};">{f:.2f} Hz</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[4]:
        soc = state['soc'] * 100
        soc_color = "#27AE60" if 30 <= soc <= 80 else "#F39C12"
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Battery</div>
            <div class="value" style="color:{soc_color};">{soc:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[5]:
        if not state['is_safe']:
            safety = ("🔴", "VIOLATION", "#E74C3C")
        elif state['cbf_active']:
            safety = ("🟡", "ACTIVE", "#F39C12")
        else:
            safety = ("🟢", "SAFE", "#27AE60")
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">U-CBF</div>
            <div class="value" style="color:{safety[2]};">{safety[0]} {safety[1]}</div>
        </div>
        """, unsafe_allow_html=True)


# REMOVED: @st.fragment from schematic - too heavy for real-time (5500 lines regenerated)
# Schematic now only updates on manual refresh or state change
def render_schematic_with_cache():
    """Render schematic with smart caching - NOT real-time (too heavy)"""
    if not SCHEMATIC_AVAILABLE:
        st.warning("Schematic component not available")
        return

    state = st.session_state.current_state

    # Create a cache key based on significant state changes only
    # Round values to avoid regenerating on tiny fluctuations
    # Include SCHEMATIC_VERSION to force regeneration when code changes
    cache_key = (
        SCHEMATIC_VERSION,                # Force regeneration when code updates
        round(state['voltage'], 0),       # Only update if voltage changes by 1V
        round(state['frequency'], 1),     # Only update if freq changes by 0.1Hz
        round(state['soc'] * 100, 0),     # Only update if SOC changes by 1%
        round(state['p_pv'], 0),          # Only update if PV changes by 1kW
        state['cbf_active'],              # Update on CBF state change
        state['is_safe'],                 # Update on safety state change
    )

    # Check if we need to regenerate
    if 'schematic_cache_key' not in st.session_state:
        st.session_state.schematic_cache_key = None
        st.session_state.cached_schematic = None

    if cache_key != st.session_state.schematic_cache_key or st.session_state.cached_schematic is None:
        # First load: use fast_mode for instant display
        is_first_load = st.session_state.cached_schematic is None

        if is_first_load:
            # FAST MODE: Skip particles/animations for instant first display
            fig = create_microgrid_schematic(
                state,
                theme='light',
                fast_mode=True,  # No particles, no animations = 80% faster
                show_animations=False,
                particle_density=0
            )
            st.session_state.cached_schematic = fig
            st.session_state.schematic_cache_key = cache_key
            st.session_state.schematic_needs_full_render = True  # Flag for full render later
        else:
            # Subsequent updates: full quality (already displayed, can afford time)
            fig = create_microgrid_schematic(
                state,
                theme='light',
                fast_mode=False,
                show_animations=True,
                particle_density=8  # Moderate particles
            )
            st.session_state.cached_schematic = fig
            st.session_state.schematic_cache_key = cache_key
            st.session_state.schematic_needs_full_render = False

    # Display cached figure
    st.plotly_chart(
        st.session_state.cached_schematic,
        width='stretch',
        theme=None,
        key=f"schematic_cached"
    )


# REMOVED @st.fragment - Heavy schematic is too slow (28s generation, 570+ shapes)
# Now it only renders ONCE per page load and uses cached version
def realtime_schematic_fragment():
    """Render schematic - NO real-time updates (too heavy with 570+ shapes)"""
    render_schematic_with_cache()


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLIFIED ANIMATED SCHEMATIC (Real-time capable - 70ms generation)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMATIC RENDERING (Fragment with longer interval = less flicker)
# Updates every 2 seconds instead of 0.5 = 4x less flicker
# ═══════════════════════════════════════════════════════════════════════════════

@st.fragment(run_every=2.0)  # Update every 2 seconds (less frequent = less flicker)
def render_realtime_schematic_fragment():
    """Render schematic with real-time updates every 2 seconds.

    Uses longer interval (2s vs 0.5s) to reduce flicker while still
    showing live data. CSS animations run continuously between updates.
    """
    state = st.session_state.current_state

    # Use the beautiful REALTIME/NEON schematic
    if REALTIME_SCHEMATIC_AVAILABLE:
        render_realtime_microgrid(state)
    elif NEON_SCHEMATIC_AVAILABLE:
        render_neon_microgrid(state)
    elif HTML_SCHEMATIC_AVAILABLE:
        render_microgrid_html(state)
    elif REFINED_SCHEMATIC_AVAILABLE:
        fig = create_refined_microgrid(state=state, animation_frame=0.5, theme='light')
        st.plotly_chart(fig, use_container_width=True, theme=None,
                       config={'displayModeBar': False, 'staticPlot': True})
    elif SIMPLE_SCHEMATIC_AVAILABLE:
        fig = create_simple_microgrid(state=state, animation_frame=0.5, theme='light')
        st.plotly_chart(fig, use_container_width=True, theme=None,
                       config={'displayModeBar': False, 'staticPlot': True})
    else:
        render_schematic_with_cache()


@st.fragment(run_every=0.5)
def realtime_charts_fragment():
    """Fragment for charts - updates smoothly like hospital monitors.

    FLICKER-FREE SOLUTION:
    - Use STABLE keys (not time.time()) so Streamlit reuses existing components
    - Charts have uirevision set so Plotly preserves UI state across data updates
    - Charts have transition set for smooth 300ms animations between data points
    """
    if CHARTS_AVAILABLE and st.session_state.chart_manager:
        manager = st.session_state.chart_manager

        # Row 1: Voltage/Frequency + Power Flows
        col1, col2 = st.columns(2)
        with col1:
            fig_vf = manager.create_voltage_frequency_chart()
            # STABLE KEY: Streamlit reuses component, Plotly animates data changes
            st.plotly_chart(fig_vf, width='stretch', key="chart_voltage_frequency")
        with col2:
            fig_power = manager.create_power_flow_chart()
            st.plotly_chart(fig_power, width='stretch', key="chart_power_flow")

        # Row 2: SOC + CBF Timeline
        col3, col4 = st.columns(2)
        with col3:
            fig_soc = manager.create_soc_chart()
            st.plotly_chart(fig_soc, width='stretch', key="chart_soc")
        with col4:
            fig_cbf = manager.create_cbf_timeline()
            st.plotly_chart(fig_cbf, width='stretch', key="chart_cbf_timeline")


@st.fragment(run_every=0.5)
def realtime_metrics_fragment():
    """Fragment for key metrics panel"""
    state = st.session_state.current_state

    col1, col2 = st.columns(2)
    with col1:
        st.metric("☀️ PV Output", f"{state['p_pv']:.1f} kW")
        st.metric("🏠 Load", f"{state['p_load']:.1f} kW")
    with col2:
        st.metric("🔌 Grid", f"{state['p_grid']:.1f} kW")
        st.metric("🔋 Battery", f"{state['p_battery']:.1f} kW")

    # CBF Status
    st.markdown("---")
    barrier = state['barrier_value']
    st.metric("🛡️ Barrier h(s)", f"{barrier:.2f}")

    # Progress bar for barrier
    barrier_pct = min(100, max(0, (barrier + 5) / 20 * 100))
    bar_color = "#27AE60" if barrier > 5 else "#F39C12" if barrier > 0 else "#E74C3C"
    st.markdown(f"""
    <div style="background:#E9ECEF;border-radius:4px;height:8px;margin-top:8px;">
        <div style="background:{bar_color};width:{barrier_pct}%;height:100%;border-radius:4px;transition:width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Scenario Status
    scenario_name = state.get('scenario', 'Normal')
    if scenario_name == 'Cyber Attack / Safety Violation':
        st.error(f"⚠️ {scenario_name}")
    elif scenario_name != 'Normal Operation':
        st.warning(f"⚡ {scenario_name}")



# =============================================================================
# CONTROL PANEL (Static - no fragment needed)
# =============================================================================

def render_control_panel():
    """Render sidebar controls"""
    with st.sidebar:
        st.markdown("## 🎮 Control Panel")

        # Simulation controls
        st.markdown("### ▶️ Simulation")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", width="stretch", type="primary"):
                st.session_state.is_running = True
                st.toast("Simulation started!", icon="▶️")
        with col2:
            if st.button("⏹️ Stop", width="stretch"):
                st.session_state.is_running = False
                st.toast("Simulation stopped", icon="⏹️")

        col3, col4 = st.columns(2)
        with col3:
            if st.button("⏭️ Step", width="stretch"):
                st.session_state.current_state = st.session_state.generator.get_state()
                if st.session_state.chart_manager:
                    st.session_state.chart_manager.update(st.session_state.current_state)
        with col4:
            if st.button("🔄 Reset", width="stretch"):
                st.session_state.generator.reset()
                if st.session_state.chart_manager:
                    st.session_state.chart_manager.reset()
                    for _ in range(100):
                        st.session_state.chart_manager.update(
                            st.session_state.generator.get_state()
                        )
                st.toast("Reset complete", icon="🔄")

        # Speed control
        st.session_state.simulation_speed = st.slider(
            "Speed",
            min_value=0.5,
            max_value=5.0,
            value=st.session_state.simulation_speed,
            step=0.5,
            format="%.1fx"
        )

        st.divider()

        # Scenario selection
        st.markdown("### 📅 Scenario")
        if CONTROLS_AVAILABLE:
            scenario, info = create_scenario_selector(key_prefix="ctrl")
            # Update generator with selected scenario
            st.session_state.generator.set_scenario(scenario)
        else:
            st.selectbox("Scenario", ["Normal", "Heatwave", "Cloudy", "Peak Demand"])

        st.divider()

        # U-CBF Parameters
        st.markdown("### ⚙️ Parameters")
        if CONTROLS_AVAILABLE:
            params = create_parameter_panel(key_prefix="ctrl")
            st.session_state.generator.set_params(params)
        else:
            st.slider("λ Safety", 1.0, 10.0, 3.0)

        st.divider()

        # Footer
        st.markdown("""
        <div style="text-align:center;color:#95A5A6;font-size:0.8rem;padding:20px 0;">
            <p><strong>PhD Thesis</strong></p>
            <p>Oussama AKIR</p>
            <p>Sup'Com, Tunisia</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# HEADER
# =============================================================================

def get_img_as_base64(file_path):
    """Reads an image file and converts it to base64 string"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_header():
    """Render dashboard header with Logo, Title and Supervisor info"""
    
    # Path to Sup'Com Logo
    # Assuming the app is run from the root of the repo, the path relative to CWD is:
    logo_path = os.path.join("src", "pictures", "supcomLogo.png")
    logo_b64 = get_img_as_base64(logo_path)
    
    st.markdown(f"""
<div style="background: linear-gradient(180deg, rgba(255,255,255,.65), rgba(255,255,255,.45)); border: 1px solid rgba(15,23,42,.14); border-radius: 18px; padding: 20px 32px; margin-bottom: 24px; box-shadow: 0 14px 30px rgba(2,6,23,.10); backdrop-filter: blur(20px); border-left: 6px solid #0ea5e9;">
<div style="display:flex;justify-content:space-between;align-items:center;">
<!-- LEFT: LOGO -->
<div style="flex: 0 0 auto; margin-right: 24px;">
<img src="data:image/png;base64,{logo_b64}" style="height: 80px; width: auto; object-fit: contain;">
</div>
<!-- CENTER: TITLE -->
<div style="flex: 1; text-align: left;">
<h1 style="color:#0f172a;margin:0;font-weight:700;font-size:2rem;font-family:Orbitron, sans-serif;letter-spacing:0.05em;">
MICROGRID DIGITAL TWIN
</h1>
<p style="color:#475569;margin:8px 0 0;font-size:1rem;font-family:Inter, sans-serif;">
Uncertainty-Aware Control Barrier Functions for Safe Reinforcement Learning
</p>
</div>
<!-- RIGHT: DETAILS -->
<div style="text-align:right;color:#64748b;font-size:0.9rem;font-family:Inter, sans-serif;border-left: 1px solid #e2e8f0; padding-left: 24px;">
<div style="color:#0f172a; font-weight:700; font-size: 1rem; margin-bottom: 4px;">Oussama AKIR</div>
<div style="margin-bottom: 2px;">PhD Candidate</div>
<div style="margin-bottom: 2px;"><strong>Encadrante: Mme Rim Barrak</strong></div>
<div style="font-size: 0.8rem; color:#94a3b8;">Sup'Com, Tunisia</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application - OPTIMIZED FOR FAST INITIAL LOAD"""

    # Initialize
    init_session_state()

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 1: INSTANT DISPLAY (Header, status bar - no heavy computation)
    # ══════════════════════════════════════════════════════════════════════════

    # Control panel in sidebar (instant - just UI elements)
    render_control_panel()

    # Header (instant - just HTML)
    render_header()

    # Update data (this fragment runs every 500ms - lightweight)
    realtime_data_fragment()

    # Status bar (smooth updates - lightweight HTML)
    realtime_status_fragment()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SCHEMATIC (Heavy - with loading indicator)
    # ══════════════════════════════════════════════════════════════════════════
    schematic_header_cols = st.columns([4, 1])
    with schematic_header_cols[0]:
        st.markdown("### 🏗️ System Overview")
    with schematic_header_cols[1]:
        if st.button("🔄 Refresh", key="refresh_schematic", help="Regenerate schematic with current state"):
            st.session_state.schematic_cache_key = None  # Force regeneration
            st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # REALTIME SCHEMATIC (Updates every 2 seconds - reduced flicker)
    # CSS animations run continuously, values update less frequently
    # ═══════════════════════════════════════════════════════════════════════════

    # Render the beautiful schematic with real-time updates
    # Fragment updates every 2 seconds (vs 0.5s) = 4x less flicker
    render_realtime_schematic_fragment()
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown("### 📈 Real-Time Monitoring")
        realtime_charts_fragment()

    with col_side:
        st.markdown("### 📊 Live Metrics")
        realtime_metrics_fragment()



    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;color:#95A5A6;font-size:0.85rem;padding:20px;">
        <strong>MH-U-CBF</strong> - Multi-Horizon Uncertainty-Bounded Control Barrier Functions<br/>
        PhD Research - Sup'Com, University of Carthage, Tunisia - 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
