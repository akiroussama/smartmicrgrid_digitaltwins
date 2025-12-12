"""
Control Panel Component
-----------------------
Provides UI controls for simulation scenarios and U-CBF parameters.
"""

import streamlit as st
from enum import Enum
from typing import Tuple, Dict, Any, Optional

class ScenarioType(Enum):
    NORMAL = "Normal Operation"
    HEATWAVE = "Heatwave (High Load)"
    CLOUD_COVER = "Heavy Cloud Cover (Low PV)"
    CYBER_ATTACK = "Cyber Attack / Safety Violation"

class UCBFParameters:
    def __init__(self, lambda_val: float = 0.1, gamma_val: float = 0.5):
        self.lambda_val = lambda_val
        self.gamma_val = gamma_val

def apply_control_panel_css():
    """Apply specific CSS for the control panel (if needed)"""
    pass

def create_scenario_selector(key_prefix: str = "ctrl") -> Tuple[ScenarioType, str]:
    """
    Render a scenario selector in the sidebar.
    Returns: (Selected ScenarioType, Description)
    """
    scenario_options = {
        ScenarioType.NORMAL: "Standard nominal operation with balanced generation and load.",
        ScenarioType.HEATWAVE: "Extreme load spike due to AC usage. Tests battery discharge limits.",
        ScenarioType.CLOUD_COVER: "Sudden drop in PV generation. Tests grid backup and battery support.",
        ScenarioType.CYBER_ATTACK: "FORCED UNSAFE STATE. Simulates sensor spoofing or control failure to trigger U-CBF.",
    }

    selected_scenario_name = st.selectbox(
        "Simulation Scenario",
        options=[s.value for s in ScenarioType],
        index=0,
        key=f"{key_prefix}_scenario_select",
        help="Choose a scenario to test the Digital Twin's response."
    )

    # Convert back to Enum
    selected_scenario = next(s for s in ScenarioType if s.value == selected_scenario_name)
    
    # Display description
    description = scenario_options[selected_scenario]
    st.caption(f"ℹ️ {description}")
    
    if selected_scenario == ScenarioType.CYBER_ATTACK:
        st.error("⚠️ WARNING: This scenario will force safety violations!")

    return selected_scenario, description

def create_parameter_panel(key_prefix: str = "ctrl") -> UCBFParameters:
    """
    Render U-CBF tuning parameters.
    """
    with st.expander("🛠️ U-CBF Tuning", expanded=False):
        lambda_val = st.slider(
            "Lambda (Decay Rate)",
            min_value=0.01, max_value=1.0, value=0.1, step=0.01,
            key=f"{key_prefix}_lambda",
            help="Control Barrier Function decay rate."
        )
        
        gamma_val = st.slider(
            "Gamma (Class K Class)",
            min_value=0.1, max_value=5.0, value=1.0, step=0.1,
            key=f"{key_prefix}_gamma",
            help="Class K function gain."
        )
        
    return UCBFParameters(lambda_val, gamma_val)

def create_perturbation_injector(key_prefix: str = "ctrl") -> Optional[str]:
    """
    Buttons to inject one-time faults.
    """
    st.markdown("### ⚡ Inject Faults")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Drop Voltage", key=f"{key_prefix}_drop_v"):
            return "drop_voltage"
    with col2:
        if st.button("Spike Freq", key=f"{key_prefix}_spike_f"):
            return "spike_freq"
    return None
