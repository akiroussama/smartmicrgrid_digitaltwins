"""Real-time plotting components for Streamlit dashboard"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def plot_realtime_trajectory(states, time_window=100):
    """Plot real-time state trajectory with rolling window"""
    fig, ax = plt.subplots(figsize=(10, 4))

    # Show only last time_window steps
    if len(states) > time_window:
        states_shown = states[-time_window:]
        t_start = len(states) - time_window
    else:
        states_shown = states
        t_start = 0

    time = np.arange(t_start, t_start + len(states_shown))

    ax.plot(time, states_shown, linewidth=2, color='#2E86AB')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('State Value')
    ax.grid(True, alpha=0.3)

    return fig


def plot_cbf_evolution(cbf_values, time_window=100):
    """Plot CBF values with safety threshold"""
    fig, ax = plt.subplots(figsize=(10, 4))

    if len(cbf_values) > time_window:
        cbf_shown = cbf_values[-time_window:]
        t_start = len(cbf_values) - time_window
    else:
        cbf_shown = cbf_values
        t_start = 0

    time = np.arange(t_start, t_start + len(cbf_shown))

    ax.plot(time, cbf_shown, linewidth=2, color='#06A77D', label='CBF Value')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Safety Threshold')
    ax.fill_between(time, 0, np.maximum(cbf_shown, 0), alpha=0.2, color='green')

    ax.set_xlabel('Time Step')
    ax.set_ylabel('CBF Value h(x)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def display_live_metrics(cvr, avg_reward, interventions):
    """Display live performance metrics"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CVR", f"{cvr:.1%}", delta=f"{(cvr-0.95)*100:.1f}%")

    with col2:
        st.metric("Avg Reward", f"{avg_reward:.1f}")

    with col3:
        st.metric("Interventions", f"{interventions:.1%}")
