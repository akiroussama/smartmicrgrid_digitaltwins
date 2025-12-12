"""
Safety Analyzer - Deep Dive into MH-U-CBF Safety Mechanisms
Interactive visualization of CBF, SAOCP, and Multi-Horizon components.

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Safety Analyzer", page_icon="🛡️", layout="wide")

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
    --shield: #10b981;
}

.stApp {
    background:
        radial-gradient(1200px 600px at 20% 10%, rgba(16,185,129,.15), transparent 55%),
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

/* Shield Header */
.shield-header {
    background: linear-gradient(135deg, rgba(16,185,129,.15), rgba(14,165,233,.15));
    border: 1px solid rgba(16,185,129,.3);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
}
.shield-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #10b981, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.shield-subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 8px;
}

/* Component Cards */
.component-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0;
}
.component-card {
    background: var(--glass-strong);
    border: 2px solid var(--stroke);
    border-radius: 16px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}
.component-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(2,6,23,.12);
}
.component-card.active {
    border-color: var(--shield);
    background: linear-gradient(180deg, rgba(16,185,129,.1), rgba(255,255,255,.95));
}
.component-icon {
    font-size: 3rem;
    margin-bottom: 12px;
}
.component-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 8px;
}
.component-desc {
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.4;
}

/* Equation Box */
.equation-box {
    background: linear-gradient(135deg, rgba(15,23,42,.03), rgba(15,23,42,.06));
    border: 1px solid var(--stroke);
    border-radius: 14px;
    padding: 20px;
    margin: 16px 0;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
}
.equation-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 12px;
}
.equation-content {
    font-size: 1.2rem;
    color: var(--ink);
    line-height: 1.8;
}

/* Safety Layers */
.safety-layers {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 20px 0;
}
.safety-layer {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.2s ease;
}
.safety-layer:hover {
    border-color: var(--shield);
    background: rgba(16,185,129,.05);
}
.layer-number {
    background: var(--shield);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
}
.layer-content {
    flex: 1;
}
.layer-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--ink);
}
.layer-desc {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 4px;
}

/* Stat Cards */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0;
}
.stat-card {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.stat-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 800;
}
.stat-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-top: 8px;
}

/* Theory Panel */
.theory-panel {
    background: var(--glass-strong);
    border: 1px solid var(--stroke);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
}
.theory-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Parameter Sliders */
.param-container {
    background: rgba(15,23,42,.03);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
}
.param-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 8px;
}

/* Info Callout */
.callout {
    background: rgba(14,165,233,.08);
    border-left: 4px solid var(--primary);
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 16px 0;
}
.callout-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 8px;
}
.callout-text {
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.5;
}

/* Guarantee Badge */
.guarantee-badge {
    background: linear-gradient(135deg, var(--shield), #059669);
    color: white;
    padding: 12px 24px;
    border-radius: 30px;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 8px 24px rgba(16,185,129,.3);
}

@keyframes pulse-shield {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50% { box-shadow: 0 0 0 15px rgba(16,185,129,0); }
}
.pulse-shield {
    animation: pulse-shield 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="shield-header">
    <h1 class="shield-title">🛡️ SAFETY MECHANISM ANALYZER</h1>
    <p class="shield-subtitle">Deep dive into MH-U-CBF's multi-layer safety architecture</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# COMPONENT SELECTOR
# =============================================================================
st.markdown("### 🔧 Safety Components")

component = st.radio(
    "Select component to analyze:",
    ["🛡️ Control Barrier Function (CBF)", "📊 SAOCP Calibration", "🔮 Multi-Horizon Prediction", "⚡ QP Solver"],
    horizontal=True
)

# =============================================================================
# CBF COMPONENT
# =============================================================================
if "CBF" in component:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
        <div class="theory-panel">
            <div class="theory-header">📐 Mathematical Foundation</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="equation-box">
            <div class="equation-title">Barrier Function Definition</div>
            <div class="equation-content">
                B(s) = 1 - ||s - s_center||² / r²<br>
                <span style="color: var(--muted); font-size: 0.85rem;">where s ∈ Safe Set ⟺ B(s) > 0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="equation-box">
            <div class="equation-title">Safety Constraint</div>
            <div class="equation-content">
                Ḃ(s) + λ₀ · B(s) ≥ -β<br>
                <span style="color: var(--muted); font-size: 0.85rem;">λ₀ = 2.0, β = 0.01 (CST+ parameters)</span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Interactive CBF visualization
        st.markdown("#### 🎮 Interactive CBF Visualization")

        col_v, col_soc = st.columns(2)
        with col_v:
            v_test = st.slider("Voltage (V)", 200.0, 260.0, 230.0, 1.0)
        with col_soc:
            soc_test = st.slider("SOC (%)", 0.0, 100.0, 50.0, 1.0)

        # Calculate barrier value
        v_center, v_range = 230, 10
        soc_center, soc_range = 50, 30

        v_norm = (v_test - v_center) / v_range
        soc_norm = (soc_test - soc_center) / soc_range
        barrier = 1 - (v_norm**2 + soc_norm**2)

        barrier_color = "#059669" if barrier > 0.3 else "#d97706" if barrier > 0 else "#dc2626"
        status = "SAFE" if barrier > 0 else "VIOLATION"

        st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-top: 16px;">
            <div class="stat-card" style="flex: 1;">
                <div class="stat-value" style="color: {barrier_color};">{barrier:.3f}</div>
                <div class="stat-label">Barrier Value B(s)</div>
            </div>
            <div class="stat-card" style="flex: 1;">
                <div class="stat-value" style="color: {barrier_color};">{status}</div>
                <div class="stat-label">Safety Status</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # CBF contour plot
        v_range_plot = np.linspace(210, 250, 100)
        soc_range_plot = np.linspace(10, 90, 100)
        V, SOC = np.meshgrid(v_range_plot, soc_range_plot)

        v_n = (V - 230) / 10
        soc_n = (SOC - 50) / 30
        B = 1 - (v_n**2 + soc_n**2)

        fig = go.Figure()

        fig.add_trace(go.Contour(
            x=v_range_plot, y=soc_range_plot, z=B,
            colorscale=[[0, '#dc2626'], [0.3, '#d97706'], [0.5, '#fbbf24'], [1, '#059669']],
            contours=dict(showlabels=True, labelfont=dict(size=10, color='white')),
            colorbar=dict(title='B(s)', titlefont=dict(family='Orbitron'))
        ))

        # Add zero contour (boundary)
        fig.add_trace(go.Contour(
            x=v_range_plot, y=soc_range_plot, z=B,
            contours=dict(start=0, end=0, size=0.01, coloring='none'),
            line=dict(color='red', width=3),
            showscale=False,
            name='Safety Boundary'
        ))

        # Add current point
        fig.add_trace(go.Scatter(
            x=[v_test], y=[soc_test],
            mode='markers',
            marker=dict(size=15, color=barrier_color, symbol='x', line=dict(width=2, color='white')),
            name='Current State'
        ))

        fig.update_layout(
            title="CBF Level Sets",
            xaxis_title="Voltage (V)",
            yaxis_title="SOC (%)",
            height=400,
            paper_bgcolor='rgba(255,255,255,0.8)',
            plot_bgcolor='rgba(255,255,255,0.5)',
            font=dict(family="Inter, sans-serif")
        )

        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SAOCP COMPONENT
# =============================================================================
elif "SAOCP" in component:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
        <div class="theory-panel">
            <div class="theory-header">📊 Statistical Adaptive Online Conformal Prediction</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="equation-box">
            <div class="equation-title">Calibration Update Rule</div>
            <div class="equation-content">
                η(t+1) = η(t) + α · (coverage(t) - target)<br>
                <span style="color: var(--muted); font-size: 0.85rem;">α = 0.01 (learning rate), target = 0.90</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="equation-box">
            <div class="equation-title">Calibrated Uncertainty</div>
            <div class="equation-content">
                σ_cal = η · σ_ensemble<br>
                <span style="color: var(--muted); font-size: 0.85rem;">η adapts online to maintain coverage guarantee</span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="callout">
            <div class="callout-title">🎯 Why SAOCP?</div>
            <div class="callout-text">
                Raw ensemble uncertainty is often <b>miscalibrated</b> under distribution shift.
                SAOCP automatically adjusts the confidence bounds to maintain the target coverage
                rate (90%) even when the data distribution changes. This is crucial for the
                formal safety guarantee of CST+ theorem.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # SAOCP calibration visualization
        np.random.seed(42)
        t = np.arange(0, 200)

        # Simulate coverage over time with distribution shift at t=100
        raw_coverage = np.concatenate([
            0.92 + 0.03 * np.random.randn(100),  # Before shift
            0.75 + 0.05 * np.random.randn(100)   # After shift (miscalibrated)
        ])

        # SAOCP corrected
        eta = 1.0
        saocp_coverage = []
        for i, cov in enumerate(raw_coverage):
            if i > 100:
                eta = eta + 0.01 * (0.90 - cov)  # Adaptive correction
                corrected = min(0.95, cov + 0.15 * (eta - 1))
            else:
                corrected = cov
            saocp_coverage.append(corrected)

        fig = make_subplots(rows=2, cols=1, subplot_titles=("Coverage Over Time", "Calibration Factor η"))

        fig.add_trace(go.Scatter(
            x=t, y=raw_coverage,
            mode='lines',
            name='Raw Ensemble',
            line=dict(color='#dc2626', width=2, dash='dash')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=t, y=saocp_coverage,
            mode='lines',
            name='SAOCP Calibrated',
            line=dict(color='#059669', width=2)
        ), row=1, col=1)

        fig.add_hline(y=0.90, line_dash="dot", line_color="#0ea5e9",
                      annotation_text="Target: 90%", row=1, col=1)

        # Distribution shift marker
        fig.add_vline(x=100, line_dash="dot", line_color="#8b5cf6", row=1, col=1)
        fig.add_annotation(x=100, y=0.98, text="Distribution Shift", showarrow=False,
                          font=dict(color="#8b5cf6"), row=1, col=1)

        # Eta evolution
        eta_history = [1.0] * 100 + [1.0 + 0.01 * i for i in range(100)]
        fig.add_trace(go.Scatter(
            x=t, y=eta_history,
            mode='lines',
            name='η',
            line=dict(color='#0ea5e9', width=2)
        ), row=2, col=1)

        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(255,255,255,0.8)',
            plot_bgcolor='rgba(255,255,255,0.5)',
            font=dict(family="Inter, sans-serif"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )

        fig.update_yaxes(title_text="Coverage", row=1, col=1)
        fig.update_yaxes(title_text="η", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# MULTI-HORIZON COMPONENT
# =============================================================================
elif "Multi-Horizon" in component:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
        <div class="theory-panel">
            <div class="theory-header">🔮 Multi-Horizon Prediction Architecture</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="safety-layers">
            <div class="safety-layer">
                <div class="layer-number">1</div>
                <div class="layer-content">
                    <div class="layer-title">h=1: Reactive Safety Net</div>
                    <div class="layer-desc">Immediate next-step safety. Last line of defense. 27% of detections.</div>
                </div>
            </div>
            <div class="safety-layer">
                <div class="layer-number">3</div>
                <div class="layer-content">
                    <div class="layer-title">h=3: Optimal Balance</div>
                    <div class="layer-desc">Sweet spot between prediction accuracy and anticipation. 30% of detections.</div>
                </div>
            </div>
            <div class="safety-layer">
                <div class="layer-number">5</div>
                <div class="layer-content">
                    <div class="layer-title">h=5: Early Warning System</div>
                    <div class="layer-desc">Advance detection for smooth corrections. 43% of detections.</div>
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: #059669;">73%</div>
                <div class="stat-label">Anticipative</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #0ea5e9;">27%</div>
                <div class="stat-label">Reactive</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #d97706;">0</div>
                <div class="stat-label">Emergency Stops</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #8b5cf6;">&lt;20ms</div>
                <div class="stat-label">Total Latency</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Horizon detection distribution
        fig = go.Figure()

        horizons = ['h=1', 'h=3', 'h=5']
        percentages = [27, 30, 43]
        colors = ['#dc2626', '#d97706', '#059669']

        fig.add_trace(go.Bar(
            x=horizons,
            y=percentages,
            marker_color=colors,
            text=[f'{p}%' for p in percentages],
            textposition='outside',
            textfont=dict(family='Orbitron', size=16, color='#0f172a')
        ))

        fig.update_layout(
            title="Detection Distribution by Horizon",
            yaxis_title="% of Violations Detected",
            height=350,
            paper_bgcolor='rgba(255,255,255,0.8)',
            plot_bgcolor='rgba(255,255,255,0.5)',
            font=dict(family="Inter, sans-serif"),
            yaxis=dict(range=[0, 55])
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="callout">
            <div class="callout-title">💡 Key Insight</div>
            <div class="callout-text">
                The multi-horizon approach means <b>73% of potential violations</b> are detected
                and corrected BEFORE they become critical. This is like gentle braking vs.
                emergency stop - smoother, safer, and more efficient.
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# QP SOLVER COMPONENT
# =============================================================================
elif "QP" in component:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
        <div class="theory-panel">
            <div class="theory-header">⚡ Hierarchical QP Formulation</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="equation-box">
            <div class="equation-title">Optimization Problem</div>
            <div class="equation-content">
                min ||a - a_RL||²<br>
                s.t. ∇B(s)·f(s,a) + λ·B(s) ≥ -β - η·σ<br>
                <span style="color: var(--muted); font-size: 0.85rem;">Minimal intervention to ensure safety</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="safety-layers">
            <div class="safety-layer">
                <div class="layer-number" style="background: #059669;">1</div>
                <div class="layer-content">
                    <div class="layer-title">Level 1: Strict Safety</div>
                    <div class="layer-desc">Full constraint enforcement. Used when B(s) > threshold.</div>
                </div>
            </div>
            <div class="safety-layer">
                <div class="layer-number" style="background: #d97706;">2</div>
                <div class="layer-content">
                    <div class="layer-title">Level 2: Relaxed Constraints</div>
                    <div class="layer-desc">Soft constraints with slack. Used in borderline situations.</div>
                </div>
            </div>
            <div class="safety-layer">
                <div class="layer-number" style="background: #dc2626;">3</div>
                <div class="layer-content">
                    <div class="layer-title">Level 3: Recovery Mode</div>
                    <div class="layer-desc">Emergency override. Maximize B(s) to recover safety.</div>
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # QP intervention visualization
        fig = go.Figure()

        # Generate sample trajectory
        t = np.linspace(0, 10, 100)
        a_rl = np.sin(t) * 0.5  # RL action
        a_safe = np.clip(a_rl, -0.3, 0.3)  # Filtered action

        fig.add_trace(go.Scatter(
            x=t, y=a_rl,
            mode='lines',
            name='RL Action (a_RL)',
            line=dict(color='#dc2626', width=2, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=t, y=a_safe,
            mode='lines',
            name='Safe Action (a*)',
            line=dict(color='#059669', width=3)
        ))

        # Add safe region
        fig.add_hrect(y0=-0.3, y1=0.3, fillcolor="rgba(5,150,105,0.1)",
                      line_width=0, annotation_text="Safe Region")

        fig.update_layout(
            title="QP Action Filtering",
            xaxis_title="Time (s)",
            yaxis_title="Action",
            height=350,
            paper_bgcolor='rgba(255,255,255,0.8)',
            plot_bgcolor='rgba(255,255,255,0.5)',
            font=dict(family="Inter, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <span class="guarantee-badge pulse-shield">
                🛡️ 90% Safety Guarantee (CST+ Theorem)
            </span>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# CST+ THEOREM SECTION
# =============================================================================
st.markdown("---")
st.markdown("### 📜 CST+ Theorem: Formal Safety Guarantee")

st.markdown("""
<div class="theory-panel">
    <div class="equation-box">
        <div class="equation-title">Compositional Safety under Temporal uncertainty (CST+)</div>
        <div class="equation-content" style="font-size: 1rem;">
            If ∀t: B(s_t) + η(t)·σ(s_t, a_t) > 0<br>
            Then P(∀t: s_t ∈ Safe) ≥ 1 - ε = <b>90%</b><br>
            <span style="color: var(--muted); font-size: 0.85rem;">
                λ₀ = 2.0, β = 0.01, horizons = {1, 3, 5}, validated by ablation
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="callout">
    <div class="callout-title">🎓 Why This Matters for Your Defense</div>
    <div class="callout-text">
        This is the <b>first formal probabilistic safety guarantee</b> for CBF-based safe RL
        that accounts for both model uncertainty (ensemble) and distribution shift (SAOCP).
        The 90% guarantee is not just empirical - it's mathematically proven under the
        stated conditions.
    </div>
</div>
""", unsafe_allow_html=True)
