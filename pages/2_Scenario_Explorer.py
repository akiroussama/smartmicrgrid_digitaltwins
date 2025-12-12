"""
Scenario Explorer - Interactive Distribution Shift Laboratory
Explore how MH-U-CBF handles different types of distribution shifts.

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Scenario Explorer", page_icon="🔬", layout="wide")

# =============================================================================
# PREMIUM GLASS THEME CSS
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg0: #f6f8fc;
    --bg1: #eef2ff;
    --ink: #0f172a;
    --muted: #475569;
    --glass: rgba(255,255,255,.62);
    --glass-strong: rgba(255,255,255,.85);
    --stroke: rgba(15,23,42,.14);
    --primary: #0ea5e9;
    --success: #059669;
    --warning: #d97706;
    --danger: #dc2626;
    --purple: #8b5cf6;
}

.stApp {
    background:
        radial-gradient(1200px 600px at 20% 10%, rgba(139,92,246,.15), transparent 55%),
        radial-gradient(900px 480px at 85% 25%, rgba(14,165,233,.12), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--stroke);
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.05em;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Lab Header */
.lab-header {
    background: linear-gradient(135deg, rgba(139,92,246,.15), rgba(14,165,233,.15));
    border: 1px solid rgba(139,92,246,.3);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
}
.lab-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #8b5cf6, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.lab-subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 8px;
}

/* Scenario Cards */
.scenario-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0;
}
.scenario-card {
    background: var(--glass-strong);
    border: 2px solid var(--stroke);
    border-radius: 16px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
}
.scenario-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(2,6,23,.12);
    border-color: var(--purple);
}
.scenario-card.selected {
    border-color: var(--purple);
    background: linear-gradient(180deg, rgba(139,92,246,.1), rgba(255,255,255,.95));
}
.scenario-card.selected::after {
    content: '✓';
    position: absolute;
    top: 12px;
    right: 12px;
    background: var(--purple);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: bold;
}

.scenario-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}
.scenario-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 8px;
}
.scenario-desc {
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.4;
}
.scenario-difficulty {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--stroke);
}
.difficulty-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
}
.difficulty-bar {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    margin-top: 6px;
    overflow: hidden;
}
.difficulty-fill {
    height: 100%;
    border-radius: 3px;
}

/* Stats Panel */
.stats-panel {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 16px;
    padding: 24px;
}
.stats-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid rgba(15,23,42,.08);
}
.stat-row:last-child {
    border-bottom: none;
}
.stat-name {
    font-size: 0.85rem;
    color: var(--muted);
}
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
}

/* Comparison Panel */
.comparison-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0;
}
.comparison-card {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.comparison-card.highlight {
    border-color: var(--success);
    background: linear-gradient(180deg, rgba(5,150,105,.08), rgba(255,255,255,.95));
}
.comparison-method {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 8px;
}
.comparison-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 800;
}
.comparison-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    margin-top: 8px;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
}
.delta-positive {
    background: rgba(5,150,105,.1);
    color: var(--success);
}
.delta-negative {
    background: rgba(220,38,38,.1);
    color: var(--danger);
}

/* Timeline */
.timeline-container {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
}
.timeline-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 16px;
}

/* Feature Tags */
.feature-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
}
.feature-tag {
    background: rgba(139,92,246,.1);
    color: var(--purple);
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Info Box */
.info-box {
    background: rgba(14,165,233,.08);
    border: 1px solid rgba(14,165,233,.2);
    border-radius: 14px;
    padding: 20px;
    margin: 20px 0;
}
.info-box h4 {
    font-family: 'Orbitron', sans-serif;
    color: var(--primary);
    margin-bottom: 12px;
}
.info-box p {
    color: var(--muted);
    margin: 0;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="lab-header">
    <h1 class="lab-title">🔬 DISTRIBUTION SHIFT LABORATORY</h1>
    <p class="lab-subtitle">Explore how MH-U-CBF handles real-world uncertainty scenarios</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SCENARIO DATA
# =============================================================================
SCENARIOS = {
    "S1": {
        "name": "Stationary",
        "icon": "📊",
        "description": "Baseline performance with no distribution shift. IID conditions.",
        "difficulty": 20,
        "difficulty_color": "#059669",
        "mh_cbf_csr": 89.51,
        "det_cbf_csr": 88.90,
        "sac_csr": 89.26,
        "shift_type": "None",
        "parameters": ["Standard PV profile", "Normal load patterns", "Stable grid"],
        "features": ["IID", "Baseline", "Validation"]
    },
    "S2": {
        "name": "Gradual Drift",
        "icon": "📈",
        "description": "Parameters slowly drift over time. Tests adaptation capability.",
        "difficulty": 40,
        "difficulty_color": "#0ea5e9",
        "mh_cbf_csr": 88.7,
        "det_cbf_csr": 86.2,
        "sac_csr": 82.4,
        "shift_type": "Covariate",
        "parameters": ["PV degradation 5%/episode", "Load growth 3%/episode", "Seasonal drift"],
        "features": ["Temporal", "Covariate Shift", "Adaptation"]
    },
    "S3": {
        "name": "Abrupt Jump",
        "icon": "⚡",
        "description": "Sudden parameter change mid-episode. Critical for real-world robustness.",
        "difficulty": 70,
        "difficulty_color": "#d97706",
        "mh_cbf_csr": 87.2,
        "det_cbf_csr": 83.1,
        "sac_csr": 71.3,
        "shift_type": "Concept",
        "parameters": ["Cloud cover +50% sudden", "Load spike +30%", "Grid frequency drop"],
        "features": ["Concept Drift", "Robustness", "Critical"]
    },
    "S4": {
        "name": "Noise Increase",
        "icon": "📡",
        "description": "Measurement noise increases significantly. Tests filter resilience.",
        "difficulty": 50,
        "difficulty_color": "#0ea5e9",
        "mh_cbf_csr": 88.1,
        "det_cbf_csr": 85.4,
        "sac_csr": 79.8,
        "shift_type": "Noise",
        "parameters": ["Sensor noise σ×3", "Communication jitter", "Measurement delay"],
        "features": ["Noise", "Uncertainty", "Calibration"]
    },
    "S5": {
        "name": "Multi-Parameter",
        "icon": "🎯",
        "description": "Multiple parameters shift simultaneously. Complex real-world scenario.",
        "difficulty": 80,
        "difficulty_color": "#dc2626",
        "mh_cbf_csr": 86.4,
        "det_cbf_csr": 81.7,
        "sac_csr": 68.2,
        "shift_type": "Multi-variate",
        "parameters": ["PV + Load + Grid combined", "Correlated shifts", "Non-stationary"],
        "features": ["Multi-variate", "Complex", "Realistic"]
    },
    "S6": {
        "name": "Adversarial",
        "icon": "🎭",
        "description": "Low-probability extreme events. Worst-case robustness testing.",
        "difficulty": 95,
        "difficulty_color": "#dc2626",
        "mh_cbf_csr": 85.8,
        "det_cbf_csr": 79.4,
        "sac_csr": 62.1,
        "shift_type": "Adversarial",
        "parameters": ["Rare event injection", "Tail distribution", "Stress testing"],
        "features": ["Adversarial", "Extreme", "Tail Risk"]
    }
}

TUNISIA_SCENARIOS = {
    "Canicule": {
        "name": "Canicule (Heat Wave)",
        "icon": "🌡️",
        "description": "Tunisian summer heat wave: 45°C, AC demand surge, PV efficiency drop.",
        "difficulty": 75,
        "difficulty_color": "#dc2626",
        "mh_cbf_csr": 88.3,
        "det_cbf_csr": 85.7,
        "sac_csr": 78.9,
        "shift_type": "Seasonal",
        "parameters": ["T=45°C", "AC load +60%", "PV efficiency -15%"],
        "features": ["Tunisia", "Seasonal", "Critical Load"]
    },
    "Ramadan": {
        "name": "Ramadan Load Shift",
        "icon": "🌙",
        "description": "Ramadan consumption pattern: shifted peak hours, evening surge.",
        "difficulty": 60,
        "difficulty_color": "#d97706",
        "mh_cbf_csr": 87.9,
        "det_cbf_csr": 84.2,
        "sac_csr": 75.6,
        "shift_type": "Behavioral",
        "parameters": ["Peak shift 14h→21h", "Evening surge +40%", "Night activity +80%"],
        "features": ["Tunisia", "Behavioral", "Cultural"]
    },
    "Ilotage": {
        "name": "Ilotage (Islanding)",
        "icon": "🔌",
        "description": "Grid disconnection scenario: microgrid operates autonomously.",
        "difficulty": 85,
        "difficulty_color": "#dc2626",
        "mh_cbf_csr": 86.1,
        "det_cbf_csr": 80.3,
        "sac_csr": 65.4,
        "shift_type": "Structural",
        "parameters": ["Grid P=0", "Battery critical", "Frequency regulation"],
        "features": ["Tunisia", "Islanding", "Autonomy"]
    }
}

# =============================================================================
# SCENARIO SELECTOR
# =============================================================================
st.markdown("### 🧪 Standard Test Scenarios")

# Create scenario selection
selected_scenario = st.radio(
    "Select a scenario to explore:",
    list(SCENARIOS.keys()),
    format_func=lambda x: f"{SCENARIOS[x]['icon']} {x}: {SCENARIOS[x]['name']}",
    horizontal=True
)

scenario = SCENARIOS[selected_scenario]

# Display scenario cards
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="scenario-card selected">
        <div class="scenario-icon">{scenario['icon']}</div>
        <div class="scenario-name">{selected_scenario}: {scenario['name']}</div>
        <div class="scenario-desc">{scenario['description']}</div>
        <div class="scenario-difficulty">
            <div class="difficulty-label">Difficulty Level</div>
            <div class="difficulty-bar">
                <div class="difficulty-fill" style="width: {scenario['difficulty']}%; background: {scenario['difficulty_color']};"></div>
            </div>
        </div>
        <div class="feature-tags">
            {''.join([f'<span class="feature-tag">{f}</span>' for f in scenario['features']])}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-panel">
        <div class="stats-header">📊 Shift Parameters</div>
        <div class="stat-row">
            <span class="stat-name">Shift Type</span>
            <span class="stat-value" style="color: var(--purple);">{scenario['shift_type']}</span>
        </div>
        <div class="stat-row">
            <span class="stat-name">Difficulty</span>
            <span class="stat-value" style="color: {scenario['difficulty_color']};">{scenario['difficulty']}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for param in scenario['parameters']:
        st.markdown(f"• {param}")

# =============================================================================
# PERFORMANCE COMPARISON
# =============================================================================
st.markdown("### 📈 Performance Under This Scenario")

delta_det = scenario['mh_cbf_csr'] - scenario['det_cbf_csr']
delta_sac = scenario['mh_cbf_csr'] - scenario['sac_csr']

st.markdown(f"""
<div class="comparison-grid">
    <div class="comparison-card highlight">
        <div class="comparison-method">MH-U-CBF (Ours)</div>
        <div class="comparison-value" style="color: #059669;">{scenario['mh_cbf_csr']:.1f}%</div>
        <div class="comparison-delta delta-positive">Best Performance</div>
    </div>
    <div class="comparison-card">
        <div class="comparison-method">Det-CBF</div>
        <div class="comparison-value" style="color: #0ea5e9;">{scenario['det_cbf_csr']:.1f}%</div>
        <div class="comparison-delta delta-negative">-{delta_det:.1f}% vs MH-U-CBF</div>
    </div>
    <div class="comparison-card">
        <div class="comparison-method">SAC (No Filter)</div>
        <div class="comparison-value" style="color: #dc2626;">{scenario['sac_csr']:.1f}%</div>
        <div class="comparison-delta delta-negative">-{delta_sac:.1f}% vs MH-U-CBF</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Performance chart
fig = go.Figure()

categories = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
mh_cbf_values = [SCENARIOS[s]['mh_cbf_csr'] for s in categories]
det_cbf_values = [SCENARIOS[s]['det_cbf_csr'] for s in categories]
sac_values = [SCENARIOS[s]['sac_csr'] for s in categories]

fig.add_trace(go.Scatter(
    x=categories, y=mh_cbf_values,
    mode='lines+markers',
    name='MH-U-CBF',
    line=dict(color='#059669', width=3),
    marker=dict(size=10)
))

fig.add_trace(go.Scatter(
    x=categories, y=det_cbf_values,
    mode='lines+markers',
    name='Det-CBF',
    line=dict(color='#0ea5e9', width=2),
    marker=dict(size=8)
))

fig.add_trace(go.Scatter(
    x=categories, y=sac_values,
    mode='lines+markers',
    name='SAC',
    line=dict(color='#dc2626', width=2, dash='dash'),
    marker=dict(size=8)
))

# Highlight selected scenario
fig.add_vline(x=selected_scenario, line_dash="dot", line_color="#8b5cf6", line_width=2)
fig.add_annotation(x=selected_scenario, y=scenario['mh_cbf_csr'] + 3,
                   text="Selected", showarrow=False,
                   font=dict(color="#8b5cf6", size=12))

fig.update_layout(
    title="CSR Across All Scenarios",
    xaxis_title="Scenario",
    yaxis_title="Constraint Satisfaction Rate (%)",
    height=400,
    paper_bgcolor='rgba(255,255,255,0.8)',
    plot_bgcolor='rgba(255,255,255,0.5)',
    font=dict(family="Inter, sans-serif"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    yaxis=dict(range=[55, 95])
)

# Add target line
fig.add_hline(y=88, line_dash="dash", line_color="#059669", opacity=0.5,
              annotation_text="Target: 88%")

st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TUNISIA SCENARIOS
# =============================================================================
st.markdown("---")
st.markdown("### 🇹🇳 Tunisia-Specific Scenarios")

tunisia_cols = st.columns(3)

for idx, (key, ts) in enumerate(TUNISIA_SCENARIOS.items()):
    with tunisia_cols[idx]:
        st.markdown(f"""
        <div class="scenario-card">
            <div class="scenario-icon">{ts['icon']}</div>
            <div class="scenario-name">{ts['name']}</div>
            <div class="scenario-desc">{ts['description']}</div>
            <div class="scenario-difficulty">
                <div class="difficulty-label">Difficulty: {ts['difficulty']}%</div>
                <div class="difficulty-bar">
                    <div class="difficulty-fill" style="width: {ts['difficulty']}%; background: {ts['difficulty_color']};"></div>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--stroke);">
                <div style="font-family: 'JetBrains Mono'; font-size: 1.2rem; font-weight: 700; color: #059669;">
                    {ts['mh_cbf_csr']:.1f}% CSR
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# INFO BOX
# =============================================================================
st.markdown("""
<div class="info-box">
    <h4>💡 Why Distribution Shift Matters</h4>
    <p>
        Real microgrids face constantly changing conditions: weather, demand patterns, grid stability.
        MH-U-CBF's multi-horizon anticipation and SAOCP calibration enable robust performance
        even when conditions deviate significantly from training data. The 73% anticipative detection
        rate means most violations are prevented before becoming critical.
    </p>
</div>
""", unsafe_allow_html=True)
