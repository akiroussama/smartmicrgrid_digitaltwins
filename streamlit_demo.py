"""
U-CBF MVP Demo - Streamlit Web Application
"""

import streamlit as st
import numpy as np
import json
import sys
sys.path.append('.')

from src.environments.microgrid_env import MicrogridEnv
from src.dynamics.ensemble_nn import EnsembleDynamics
from src.safety.cbf_filter import CBFSafetyFilter
from src.uncertainty.saocp_calibrator import SAOCPCalibrator

# Page configuration
st.set_page_config(
    page_title="U-CBF MVP Demo",
    page_icon="⚡",
    layout="wide"
)

# Title
st.title("⚡ U-CBF: Uncertainty-aware Control Barrier Functions")
st.markdown("**Microgrid Safety Control Demo**")

# Load models (cached)
@st.cache_resource
def load_models():
    """Load all models (cached for performance)"""
    try:
        ensemble = EnsembleDynamics(n_networks=5)
        ensemble.load('results/checkpoints/ensemble_n5.pt')

        cbf = CBFSafetyFilter()
        saocp = SAOCPCalibrator()

        return ensemble, cbf, saocp
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None

# Sidebar
st.sidebar.header("Configuration")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Live Simulation", "Results Dashboard"]
)

# Main content
if page == "Overview":
    st.header("📚 Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Problem Statement")
        st.markdown("""
        **Challenge**: Ensuring safety in autonomous control systems under uncertainty.

        **Key Issues**:
        - Model uncertainty in dynamics predictions
        - Distribution shifts in real-world deployment
        - Safety-critical constraints (voltage, frequency)
        """)

        st.subheader("Our Solution: U-CBF")
        st.markdown("""
        1. **Ensemble Dynamics**: N=5 networks for epistemic uncertainty
        2. **SAOCP Calibration**: Adaptive conformal prediction
        3. **CBF Safety Filter**: QP-based action filtering
        4. **Watchdog**: Distribution shift detection
        """)

    with col2:
        st.subheader("System Architecture")
        st.code("""
        ┌─────────────┐
        │ RL Policy   │
        │   (SAC)     │
        └──────┬──────┘
               │ u_rl
               ▼
        ┌─────────────────────┐
        │ Ensemble Dynamics   │
        │ ŝ_{t+1}, σ_ensemble │
        └──────┬──────────────┘
               │
               ▼
        ┌─────────────────┐
        │ SAOCP Calibrator│
        │   σ_calibrated  │
        └──────┬──────────┘
               │
               ▼
        ┌─────────────────┐
        │  CBF Filter     │
        │    (QP)         │
        └──────┬──────────┘
               │ u_safe
               ▼
        ┌─────────────────┐
        │   Environment   │
        └─────────────────┘
        """, language="text")

    st.markdown("---")

    # Metrics
    try:
        with open('results/validation/metrics_summary.json', 'r') as f:
            metrics = json.load(f)

        st.subheader("📊 Key Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Average CVR",
                f"{metrics['summary']['avg_cvr']:.4f}",
                delta="Lower is better",
                delta_color="inverse"
            )

        with col2:
            st.metric(
                "Average Reward",
                f"{metrics['summary']['avg_reward']:.2f}"
            )

        with col3:
            st.metric(
                "Scenarios Tested",
                len(metrics['scenarios'])
            )

    except FileNotFoundError:
        st.info("📋 Run validation pipeline to see results: `python scripts/05_run_validation.py`")

elif page == "Live Simulation":
    st.header("🔴 Live Simulation")

    ensemble, cbf, saocp = load_models()

    if ensemble is None:
        st.error("Models not loaded. Please run training pipeline first.")
        st.stop()

    # Simulation controls
    col1, col2 = st.columns(2)

    with col1:
        n_steps = st.slider("Simulation Steps", 10, 500, 100)

    with col2:
        lambda_tight = st.slider("Safety Margin (λ)", 1.0, 10.0, 3.0, 0.5)

    if st.button("▶️ Run Simulation", type="primary"):
        # Create environment
        env = MicrogridEnv()
        state, _ = env.reset(seed=42)

        # Storage
        states_list = []
        actions_list = []
        rewards_list = []

        # Run simulation
        progress_bar = st.progress(0)

        for t in range(n_steps):
            # Random policy for demo
            action = np.random.uniform(env.action_space.low, env.action_space.high)

            # Predict
            pred_mean, pred_std = ensemble.predict(state, action)
            sigma_cal = saocp.calibrate(pred_std[0])

            # Filter
            cbf.lambda_tight = lambda_tight
            action_safe, _ = cbf.filter_action(state, action, pred_mean[0], sigma_cal)

            # Step
            next_state, reward, terminated, truncated, _ = env.step(action_safe)

            # Store
            states_list.append(state)
            actions_list.append(action_safe)
            rewards_list.append(reward)

            if terminated or truncated:
                break

            state = next_state
            progress_bar.progress((t + 1) / n_steps)

        # Display results
        st.success(f"✅ Simulation complete! {len(states_list)} steps")

        # Plot voltage
        states_array = np.array(states_list)
        st.subheader("Voltage Trajectory")
        st.line_chart(states_array[:, 4])  # Voltage is index 4

        # Plot frequency
        st.subheader("Frequency Trajectory")
        st.line_chart(states_array[:, 5])  # Frequency is index 5

elif page == "Results Dashboard":
    st.header("📊 Results Dashboard")

    try:
        with open('results/validation/metrics_summary.json', 'r') as f:
            metrics = json.load(f)

        # Display scenario results
        st.subheader("Scenario Performance")

        for scenario_id, results in metrics['scenarios'].items():
            with st.expander(f"Scenario {scenario_id}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("CVR", f"{results['cvr']:.4f}")

                with col2:
                    st.metric("Avg Reward", f"{results['avg_reward']:.2f}")

        st.markdown("---")

        # Summary
        st.subheader("Summary Statistics")
        st.json(metrics['summary'])

    except FileNotFoundError:
        st.warning("No validation results found. Please run validation pipeline first:")
        st.code("python scripts/05_run_validation.py", language="bash")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**U-CBF MVP Demo v1.0**")
st.sidebar.markdown("Thesis: Oussama AKIR")
