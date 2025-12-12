"""
MH-U-CBF Digital Twin - Standalone Streamlit Application

Real-time microgrid visualization with U-CBF safety monitoring.
Designed for easy deployment on Streamlit Cloud / Hugging Face Spaces.

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
Date: December 2025

Run: streamlit run app.py
"""

import streamlit as st
import time
import math
import random
from typing import Dict, Any
from enum import Enum

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="MH-U-CBF Digital Twin",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
try:
    from components.microgrid_realtime import render_realtime_microgrid
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False

try:
    from components.realtime_charts import RealtimeChartManager, ChartConfig
    CHARTS_AVAILABLE = True
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


# =============================================================================
# GLOBAL CSS
# =============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@500;700&display=swap');

:root {
  --bg0: #f6f8fc;
  --ink: #0f172a;
  --muted: #475569;
  --glass: rgba(255,255,255,.62);
  --stroke: rgba(15,23,42,.14);
  --primary: #0ea5e9;
  --shadow-md: 0 14px 30px rgba(2,6,23,.10);
  --radius-lg: 18px;
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--ink);
}

.stApp {
    background: #f8fafc;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--stroke);
}

[data-testid="stPlotlyChart"], [data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,255,.78), rgba(255,255,255,.54));
    border: 1px solid var(--stroke);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(16px);
    padding: 16px;
}

[data-testid="stMetricLabel"] {
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

.premium-card {
    background: linear-gradient(180deg, rgba(255,255,255,.78), rgba(255,255,255,.54));
    border: 1px solid var(--stroke);
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 10px 18px rgba(2,6,23,.08);
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

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.05em;
    color: var(--ink);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

button[kind="primary"] {
    background: #22c55e !important;
    border: 1px solid #16a34a !important;
    color: white !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SCENARIO TYPES
# =============================================================================

class ScenarioType(Enum):
    NORMAL = "Normal Operation"
    HEATWAVE = "Heatwave (High Load)"
    CLOUD_COVER = "Heavy Cloud Cover (Low PV)"
    CYBER_ATTACK = "Cyber Attack / Safety Violation"


# =============================================================================
# SIMULATION DATA GENERATOR
# =============================================================================

class SimulationDataGenerator:
    """Generates smooth, continuous simulation data"""

    def __init__(self):
        self.step = 0
        self.start_time = time.time()
        self._voltage = 230.0
        self._frequency = 50.0
        self._soc = 0.65
        self._pv = 25.0
        self._load = 35.0
        self._barrier = 12.0
        self._scenario = ScenarioType.NORMAL

    def set_scenario(self, scenario: ScenarioType):
        self._scenario = scenario

    def get_state(self) -> Dict[str, Any]:
        t = time.time() - self.start_time
        self.step += 1

        # Smooth variations
        self._voltage += 0.1 * math.sin(t * 0.5) + random.gauss(0, 0.05)
        self._voltage = max(218, min(242, self._voltage))

        self._frequency += 0.01 * math.sin(t * 0.3) + random.gauss(0, 0.005)
        self._frequency = max(49.2, min(50.8, self._frequency))

        soc_trend = 0.0005 * math.sin(t * 0.1)
        self._soc += soc_trend + random.gauss(0, 0.001)
        self._soc = max(0.15, min(0.95, self._soc))

        hour = (t / 10) % 24
        sun_factor = max(0, math.sin(math.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0
        self._pv += 0.5 * (35 * sun_factor - self._pv) * 0.1 + random.gauss(0, 0.2)
        self._pv = max(0, min(50, self._pv))

        self._load += 0.3 * math.sin(t * 0.2) + random.gauss(0, 0.1)
        self._load = max(20, min(50, self._load))

        # Scenario overrides
        if self._scenario == ScenarioType.HEATWAVE:
            self._load = 45.0 + 5 * math.sin(t * 0.2)
            self._pv = 15.0 + 2 * math.sin(t * 0.1)
        elif self._scenario == ScenarioType.CLOUD_COVER:
            self._pv = 5.0 + 2 * random.random()
        elif self._scenario == ScenarioType.CYBER_ATTACK:
            self._voltage = 255.0 + 5 * math.sin(t)
            self._soc = 0.05 + 0.01 * math.sin(t)
            self._frequency = 51.5 + 0.5 * math.sin(t*2)
            self._barrier = -5.0 + random.gauss(0, 0.5)

        # Barrier calculation
        if self._scenario != ScenarioType.CYBER_ATTACK:
            v_margin = min(242 - self._voltage, self._voltage - 218)
            soc_margin = (self._soc - 0.15) * 100
            target_barrier = min(v_margin, soc_margin)
            self._barrier += 0.2 * (target_barrier - self._barrier)

        cbf_active = self._barrier < 2.0
        is_safe = self._barrier > 0

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
            'scenario': self._scenario.value
        }

    def reset(self):
        self.__init__()


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.is_running = False
        st.session_state.simulation_speed = 1.0
        st.session_state.generator = SimulationDataGenerator()
        st.session_state.current_state = st.session_state.generator.get_state()

        if CHARTS_AVAILABLE:
            st.session_state.chart_manager = RealtimeChartManager(
                window_size=200,
                config=LIGHT_CHART_CONFIG
            )
            for _ in range(100):
                st.session_state.chart_manager.update(
                    st.session_state.generator.get_state()
                )
        else:
            st.session_state.chart_manager = None


# =============================================================================
# FRAGMENTS (Real-time updates)
# =============================================================================

@st.fragment(run_every=0.5)
def realtime_data_fragment():
    if st.session_state.is_running:
        steps = max(1, int(st.session_state.simulation_speed * 2))
        for _ in range(steps):
            st.session_state.current_state = st.session_state.generator.get_state()
            if st.session_state.chart_manager:
                st.session_state.chart_manager.update(st.session_state.current_state)


@st.fragment(run_every=0.5)
def realtime_status_fragment():
    state = st.session_state.current_state
    cols = st.columns(6)

    with cols[0]:
        status_icon = "🟢" if st.session_state.is_running else "⏹️"
        status_text = "RUNNING" if st.session_state.is_running else "STOPPED"
        st.markdown(f"""
        <div class="premium-card">
            <div class="label">Status</div>
            <div class="value">{status_icon} {status_text}</div>
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


@st.fragment(run_every=2.0)
def render_schematic_fragment():
    state = st.session_state.current_state
    if REALTIME_AVAILABLE:
        render_realtime_microgrid(state)
    else:
        st.info("Schematic component not available. Showing metrics only.")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("☀️ PV", f"{state['p_pv']:.1f} kW")
        with col2:
            st.metric("🔋 Battery", f"{state['soc']*100:.0f}%")
        with col3:
            st.metric("🏠 Load", f"{state['p_load']:.1f} kW")
        with col4:
            st.metric("🛡️ Barrier", f"{state['barrier_value']:.2f}")


@st.fragment(run_every=0.5)
def realtime_charts_fragment():
    if CHARTS_AVAILABLE and st.session_state.chart_manager:
        manager = st.session_state.chart_manager

        col1, col2 = st.columns(2)
        with col1:
            fig_vf = manager.create_voltage_frequency_chart()
            st.plotly_chart(fig_vf, use_container_width=True, key="chart_vf")
        with col2:
            fig_power = manager.create_power_flow_chart()
            st.plotly_chart(fig_power, use_container_width=True, key="chart_power")

        col3, col4 = st.columns(2)
        with col3:
            fig_soc = manager.create_soc_chart()
            st.plotly_chart(fig_soc, use_container_width=True, key="chart_soc")
        with col4:
            fig_cbf = manager.create_cbf_timeline()
            st.plotly_chart(fig_cbf, use_container_width=True, key="chart_cbf")


# =============================================================================
# CONTROL PANEL
# =============================================================================

def render_control_panel():
    with st.sidebar:
        st.markdown("## 🎮 Control Panel")

        st.markdown("### ▶️ Simulation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", use_container_width=True, type="primary"):
                st.session_state.is_running = True
                st.toast("Simulation started!", icon="▶️")
        with col2:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.is_running = False
                st.toast("Simulation stopped", icon="⏹️")

        col3, col4 = st.columns(2)
        with col3:
            if st.button("⏭️ Step", use_container_width=True):
                st.session_state.current_state = st.session_state.generator.get_state()
                if st.session_state.chart_manager:
                    st.session_state.chart_manager.update(st.session_state.current_state)
        with col4:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.generator.reset()
                if st.session_state.chart_manager:
                    st.session_state.chart_manager.reset()
                    for _ in range(100):
                        st.session_state.chart_manager.update(
                            st.session_state.generator.get_state()
                        )
                st.toast("Reset complete", icon="🔄")

        st.session_state.simulation_speed = st.slider(
            "Speed", 0.5, 5.0, st.session_state.simulation_speed, 0.5, format="%.1fx"
        )

        st.divider()

        st.markdown("### 📅 Scenario")
        scenario_name = st.selectbox(
            "Select Scenario",
            [s.value for s in ScenarioType],
            index=0
        )
        selected_scenario = next(s for s in ScenarioType if s.value == scenario_name)
        st.session_state.generator.set_scenario(selected_scenario)

        if selected_scenario == ScenarioType.CYBER_ATTACK:
            st.error("⚠️ This will force safety violations!")

        st.divider()

        st.markdown("""
        <div style="text-align:center;color:#95A5A6;font-size:0.8rem;padding:20px 0;">
            <p><strong>PhD Thesis</strong></p>
            <p>Oussama AKIR</p>
            <p>Sup'Com, Tunisia 2025</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# HEADER
# =============================================================================

def render_header():
    st.markdown("""
<div style="background: linear-gradient(180deg, rgba(255,255,255,.65), rgba(255,255,255,.45)); border: 1px solid rgba(15,23,42,.14); border-radius: 18px; padding: 20px 32px; margin-bottom: 24px; box-shadow: 0 14px 30px rgba(2,6,23,.10); border-left: 6px solid #0ea5e9;">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div style="flex: 1;">
<h1 style="color:#0f172a;margin:0;font-weight:700;font-size:2rem;font-family:Orbitron, sans-serif;letter-spacing:0.05em;">
🏭 MICROGRID DIGITAL TWIN
</h1>
<p style="color:#475569;margin:8px 0 0;font-size:1rem;font-family:Inter, sans-serif;">
MH-U-CBF: Multi-Horizon Uncertainty-Aware Control Barrier Functions
</p>
</div>
<div style="text-align:right;color:#64748b;font-size:0.9rem;">
<div style="color:#0f172a; font-weight:700;">Oussama AKIR</div>
<div>PhD Candidate</div>
<div style="font-size: 0.8rem; color:#94a3b8;">Sup'Com, Tunisia</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    init_session_state()
    render_control_panel()
    render_header()

    realtime_data_fragment()
    realtime_status_fragment()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown("### 🏗️ System Overview")
    render_schematic_fragment()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    if CHARTS_AVAILABLE:
        st.markdown("### 📈 Real-Time Monitoring")
        realtime_charts_fragment()

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;color:#95A5A6;font-size:0.85rem;padding:20px;">
        <strong>MH-U-CBF</strong> - Multi-Horizon Uncertainty-Bounded Control Barrier Functions<br/>
        PhD Research - Sup'Com, University of Carthage, Tunisia - 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
