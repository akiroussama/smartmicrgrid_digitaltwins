"""
Simplified 2D Animated Microgrid Digital Twin
==============================================

Lightweight version optimized for real-time animation:
- Fast generation (< 0.5s vs 28s for full version)
- ~50 shapes vs 570+ in full version
- Real-time power flow animations
- Clear, readable values that update every 500ms

Author: Oussama AKIR
Date: December 2025
"""

import plotly.graph_objects as go
from typing import Dict, Optional, Any
import math

# Version for cache invalidation
SIMPLE_SCHEMATIC_VERSION = "1.0.0"


def create_simple_microgrid(
    state: Optional[Dict[str, Any]] = None,
    animation_frame: float = 0.0,
    theme: str = 'light'
) -> go.Figure:
    """
    Create a simplified 2D animated microgrid schematic.

    Args:
        state: Dictionary with system state values
        animation_frame: 0.0-1.0 for power flow animation
        theme: 'light' or 'dark'

    Returns:
        Plotly figure object
    """
    # Default state values
    if state is None:
        state = {}

    # Extract values with defaults
    p_pv = state.get('p_pv', 25.0)
    p_battery = state.get('p_battery', -5.0)
    p_grid = state.get('p_grid', 10.0)
    p_load = state.get('p_load', 30.0)
    soc = state.get('soc', 0.65)
    voltage = state.get('voltage', 230.0)
    frequency = state.get('frequency', 50.0)
    cbf_active = state.get('cbf_active', False)
    is_safe = state.get('is_safe', True)
    barrier_value = state.get('barrier_value', 0.05)

    # Theme colors
    if theme == 'dark':
        bg_color = '#0a0a1a'
        text_color = '#e0e0e0'
        box_color = '#1a1a2e'
        border_color = '#3a3a5e'
        bus_color = '#ff7700'
    else:
        bg_color = '#ffffff'
        text_color = '#2c3e50'
        box_color = '#f8f9fa'
        border_color = '#dee2e6'
        bus_color = '#ff8c00'

    # Component colors
    pv_color = '#f59e0b'      # Solar gold
    battery_color = '#22c55e' if soc > 0.3 else '#ef4444'  # Green or red
    grid_color = '#3b82f6'    # Blue
    load_color = '#ef4444'    # Red
    cbf_color = '#06b6d4' if is_safe else '#ef4444'  # Cyan or red

    # Create figure
    fig = go.Figure()

    # Layout positions (2D grid layout)
    # Top row: PV | CBF | Load
    # Middle: ========= BUS =========
    # Bottom row: Battery | Grid

    pv_pos = (0.2, 0.75)
    cbf_pos = (0.5, 0.75)
    load_pos = (0.8, 0.75)
    bus_y = 0.5
    battery_pos = (0.3, 0.25)
    grid_pos = (0.7, 0.25)

    box_w = 0.12
    box_h = 0.15

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPONENT BOXES (Simple rectangles)
    # ═══════════════════════════════════════════════════════════════════════════

    # PV Panel
    fig.add_shape(
        type="rect",
        x0=pv_pos[0] - box_w, y0=pv_pos[1] - box_h,
        x1=pv_pos[0] + box_w, y1=pv_pos[1] + box_h,
        fillcolor=_lighten(pv_color, 0.8),
        line=dict(color=pv_color, width=3),
    )
    fig.add_annotation(
        x=pv_pos[0], y=pv_pos[1] + 0.05,
        text="<b>SOLAR PV</b>",
        showarrow=False,
        font=dict(size=14, color=pv_color),
    )
    fig.add_annotation(
        x=pv_pos[0], y=pv_pos[1] - 0.05,
        text=f"<b>{p_pv:.1f} kW</b>",
        showarrow=False,
        font=dict(size=18, color=pv_color, family="monospace"),
    )

    # U-CBF Safety Filter
    cbf_fill = _lighten(cbf_color, 0.8) if is_safe else '#ffe5e5'
    fig.add_shape(
        type="rect",
        x0=cbf_pos[0] - box_w, y0=cbf_pos[1] - box_h,
        x1=cbf_pos[0] + box_w, y1=cbf_pos[1] + box_h,
        fillcolor=cbf_fill,
        line=dict(color=cbf_color, width=3),
    )
    status_text = "ACTIVE" if cbf_active else ("SAFE" if is_safe else "ALERT!")
    fig.add_annotation(
        x=cbf_pos[0], y=cbf_pos[1] + 0.06,
        text="<b>U-CBF</b>",
        showarrow=False,
        font=dict(size=14, color=cbf_color),
    )
    fig.add_annotation(
        x=cbf_pos[0], y=cbf_pos[1] - 0.02,
        text=f"<b>{status_text}</b>",
        showarrow=False,
        font=dict(size=16, color=cbf_color, family="monospace"),
    )
    fig.add_annotation(
        x=cbf_pos[0], y=cbf_pos[1] - 0.08,
        text=f"h={barrier_value:.3f}",
        showarrow=False,
        font=dict(size=11, color=text_color),
    )

    # Load
    fig.add_shape(
        type="rect",
        x0=load_pos[0] - box_w, y0=load_pos[1] - box_h,
        x1=load_pos[0] + box_w, y1=load_pos[1] + box_h,
        fillcolor=_lighten(load_color, 0.85),
        line=dict(color=load_color, width=3),
    )
    fig.add_annotation(
        x=load_pos[0], y=load_pos[1] + 0.05,
        text="<b>LOAD</b>",
        showarrow=False,
        font=dict(size=14, color=load_color),
    )
    fig.add_annotation(
        x=load_pos[0], y=load_pos[1] - 0.05,
        text=f"<b>{p_load:.1f} kW</b>",
        showarrow=False,
        font=dict(size=18, color=load_color, family="monospace"),
    )

    # Battery
    batt_fill_color = '#22c55e' if soc > 0.5 else ('#eab308' if soc > 0.2 else '#ef4444')
    fig.add_shape(
        type="rect",
        x0=battery_pos[0] - box_w, y0=battery_pos[1] - box_h,
        x1=battery_pos[0] + box_w, y1=battery_pos[1] + box_h,
        fillcolor=_lighten(batt_fill_color, 0.8),
        line=dict(color=batt_fill_color, width=3),
    )
    batt_status = "+" if p_battery > 0 else ("−" if p_battery < 0 else "")
    fig.add_annotation(
        x=battery_pos[0], y=battery_pos[1] + 0.06,
        text="<b>BATTERY</b>",
        showarrow=False,
        font=dict(size=14, color=batt_fill_color),
    )
    fig.add_annotation(
        x=battery_pos[0], y=battery_pos[1] - 0.02,
        text=f"<b>{soc*100:.0f}%</b>",
        showarrow=False,
        font=dict(size=20, color=batt_fill_color, family="monospace"),
    )
    fig.add_annotation(
        x=battery_pos[0], y=battery_pos[1] - 0.09,
        text=f"{batt_status}{abs(p_battery):.1f} kW",
        showarrow=False,
        font=dict(size=12, color=text_color),
    )

    # Grid
    grid_direction = "IMPORT" if p_grid > 0 else "EXPORT"
    fig.add_shape(
        type="rect",
        x0=grid_pos[0] - box_w, y0=grid_pos[1] - box_h,
        x1=grid_pos[0] + box_w, y1=grid_pos[1] + box_h,
        fillcolor=_lighten(grid_color, 0.85),
        line=dict(color=grid_color, width=3),
    )
    fig.add_annotation(
        x=grid_pos[0], y=grid_pos[1] + 0.06,
        text="<b>GRID</b>",
        showarrow=False,
        font=dict(size=14, color=grid_color),
    )
    fig.add_annotation(
        x=grid_pos[0], y=grid_pos[1] - 0.02,
        text=f"<b>{grid_direction}</b>",
        showarrow=False,
        font=dict(size=12, color=grid_color),
    )
    fig.add_annotation(
        x=grid_pos[0], y=grid_pos[1] - 0.08,
        text=f"<b>{abs(p_grid):.1f} kW</b>",
        showarrow=False,
        font=dict(size=16, color=grid_color, family="monospace"),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # AC POWER BUS (Horizontal bar)
    # ═══════════════════════════════════════════════════════════════════════════

    fig.add_shape(
        type="rect",
        x0=0.05, y0=bus_y - 0.02,
        x1=0.95, y1=bus_y + 0.02,
        fillcolor=bus_color,
        line=dict(color='#cc6600', width=2),
    )
    fig.add_annotation(
        x=0.5, y=bus_y,
        text=f"<b>AC BUS  |  {voltage:.0f}V  |  {frequency:.1f}Hz</b>",
        showarrow=False,
        font=dict(size=12, color='white'),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # POWER FLOW ARROWS (Animated)
    # ═══════════════════════════════════════════════════════════════════════════

    # Animation offset for moving arrows
    offset = animation_frame * 0.1

    # PV to Bus (always down if p_pv > 0)
    if p_pv > 0.5:
        _add_animated_flow(fig, pv_pos[0], pv_pos[1] - box_h - 0.02,
                          pv_pos[0], bus_y + 0.03, pv_color, offset, "down")

    # Battery to/from Bus
    if abs(p_battery) > 0.5:
        direction = "up" if p_battery > 0 else "down"
        batt_color_flow = '#22c55e' if p_battery > 0 else '#ef4444'
        _add_animated_flow(fig, battery_pos[0], battery_pos[1] + box_h + 0.02,
                          battery_pos[0], bus_y - 0.03, batt_color_flow, offset, direction)

    # Grid to/from Bus
    if abs(p_grid) > 0.5:
        direction = "up" if p_grid > 0 else "down"
        grid_flow_color = '#3b82f6' if p_grid > 0 else '#9b59b6'
        _add_animated_flow(fig, grid_pos[0], grid_pos[1] + box_h + 0.02,
                          grid_pos[0], bus_y - 0.03, grid_flow_color, offset, direction)

    # Bus to Load (always to the right/down)
    if p_load > 0.5:
        _add_animated_flow(fig, load_pos[0], bus_y + 0.03,
                          load_pos[0], load_pos[1] - box_h - 0.02, load_color, offset, "up")

    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS INDICATORS
    # ═══════════════════════════════════════════════════════════════════════════

    # Power balance check
    net_power = p_pv + p_battery + p_grid - p_load
    balance_ok = abs(net_power) < 1.0

    # Title
    fig.add_annotation(
        x=0.5, y=1.02,
        xref="paper", yref="paper",
        text="<b>MICROGRID DIGITAL TWIN</b>",
        showarrow=False,
        font=dict(size=22, color=text_color, family="Arial Black"),
    )

    # Safety status bar at bottom
    status_color = '#22c55e' if is_safe else '#ef4444'
    safety_text = "SYSTEM SAFE" if is_safe else "SAFETY VIOLATION!"
    fig.add_annotation(
        x=0.5, y=-0.05,
        xref="paper", yref="paper",
        text=f"<b>{safety_text}</b>  |  Net: {net_power:+.1f} kW",
        showarrow=False,
        font=dict(size=14, color=status_color),
        bgcolor=_lighten(status_color, 0.9),
        borderpad=8,
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # LAYOUT
    # ═══════════════════════════════════════════════════════════════════════════

    fig.update_layout(
        showlegend=False,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        margin=dict(l=20, r=20, t=60, b=60),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.05, 1.05],
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 1],
            scaleanchor="x",
            scaleratio=0.7,
            fixedrange=True,
        ),
        height=500,
    )

    return fig


def _add_animated_flow(fig, x1, y1, x2, y2, color, offset, direction):
    """Add animated power flow indicators between two points."""
    # Calculate number of dots based on distance
    distance = abs(y2 - y1)
    num_dots = max(3, int(distance * 15))

    # Create animated dots along the path
    for i in range(num_dots):
        # Position with animation offset
        if direction == "down":
            t = ((i / num_dots) + offset) % 1.0
        else:
            t = ((1 - i / num_dots) + offset) % 1.0

        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        # Varying opacity for trail effect
        opacity = 0.3 + 0.7 * (1 - abs(t - 0.5) * 2)
        size = 6 + 4 * (1 - abs(t - 0.5) * 2)

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(
                size=size,
                color=color,
                opacity=opacity,
            ),
            hoverinfo='skip',
            showlegend=False,
        ))


def _lighten(hex_color, factor=0.5):
    """Lighten a hex color by blending with white."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    return f'#{r:02x}{g:02x}{b:02x}'


# Quick test
if __name__ == "__main__":
    import time

    start = time.time()
    fig = create_simple_microgrid()
    elapsed = time.time() - start

    print(f"Generation time: {elapsed*1000:.1f}ms")
    print(f"Shapes: {len(fig.layout.shapes) if fig.layout.shapes else 0}")
    print(f"Annotations: {len(fig.layout.annotations) if fig.layout.annotations else 0}")
    print(f"Traces: {len(fig.data)}")

    fig.show()
