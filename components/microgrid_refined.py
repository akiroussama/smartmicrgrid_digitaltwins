"""
Refined Microgrid Digital Twin Schematic
========================================

A premium, lightweight visualization that bridges the gap between:
1. The "Complex" logic (heavy, 28s render)
2. The "Simple" logic (fast, boxy)

Key Features:
- Real-time performance (<100ms render time)
- Vector iconography (SVG paths) instead of simple boxes
- Cinematic color palette
- Animated power flows

Author: Oussama AKIR
Date: December 2025
"""

import plotly.graph_objects as go
from typing import Dict, Optional, Any
import math

# =============================================================================
# CONSTANTS & THEME
# =============================================================================

class RefinedPalette:
    # Deep Backgrounds
    VOID = "#0F1115"
    PANEL_BG = "#181B21"
    
    # Text
    TEXT_MAIN = "#E0E6ED" 
    TEXT_DIM = "#94A3B8"
    
    # Energy Colors
    SOLAR = "#FBBF24"    # Warm Gold
    GRID = "#3B82F6"     # Electric Blue
    LOAD = "#F43F5E"     # Rose Red
    BATTERY = "#10B981"  # Emerald Green (Dynamic)
    SAFE = "#06B6D4"     # Cyan
    WARN = "#F59E0B"     # Amber
    DANGER = "#EF4444"   # Red

    # Gradients/Glows (Simulated with transparent layers)
    GLOW_LOW = "rgba(255,255,255,0.05)"
    GLOW_MED = "rgba(255,255,255,0.1)"

# SVG Paths for Icons (Normalized to roughly 1x1 box centered at 0,0 where possible, or handled via scaling)
ICONS = {
    # Simple House
    "LOAD": "M -0.4,0.1 L -0.4,0.5 L 0.4,0.5 L 0.4,0.1 L 0,-0.4 Z M 0.25,-0.2 L 0.25,-0.4 L 0.4,-0.4 L 0.4,-0.05",
    
    # Generic Battery
    "BATTERY": "M -0.3,-0.4 L 0.3,-0.4 L 0.3,0.4 L -0.3,0.4 Z M -0.15,-0.5 L 0.15,-0.5 L 0.15,-0.4 L -0.15,-0.4 Z",
    
    # Sun
    "SOLAR": "M 0,0 m -0.25,0 a 0.25,0.25 0 1,0 0.5,0 a 0.25,0.25 0 1,0 -0.5,0 M 0,-0.35 L 0,-0.5 M 0,0.35 L 0,0.5 M -0.35,0 L -0.5,0 M 0.35,0 L 0.5,0 M 0.25,-0.25 L 0.35,-0.35 M -0.25,-0.25 L -0.35,-0.35 M 0.25,0.25 L 0.35,0.35 M -0.25,0.25 L -0.35,0.35",
    
    # Pylon / Grid
    "GRID": "M 0,-0.4 L 0,0.5 M -0.3,0.2 L 0.3,0.2 M -0.2,-0.1 L 0.2,-0.1 M -0.2,0.5 L 0.2,0.5 M 0,-0.4 L -0.25,0.5 M 0,-0.4 L 0.25,0.5",
    
    # Shield
    "SHIELD": "M -0.35,-0.3 C -0.35,-0.3 0,-0.4 0.35,-0.3 C 0.35,-0.3 0.35,0.1 0,0.4 C -0.35,0.1 -0.35,-0.3 -0.35,-0.3 Z"
}

def create_refined_microgrid(
    state: Optional[Dict[str, Any]] = None,
    animation_frame: float = 0.0,
    theme: str = 'light'
) -> go.Figure:
    """
    Create a refined, icon-based animated microgrid schematic.
    
    Args:
        state: System state dict
        animation_frame: 0.0-1.0
        theme: 'light' or 'dark' (Currently optimized for Light/Clean look as per refined standard)
    """
    if state is None: state = {}
    
    # 1. State Extraction
    p_pv = state.get('p_pv', 0)
    p_batt = state.get('p_battery', 0)
    p_grid = state.get('p_grid', 0)
    p_load = state.get('p_load', 0)
    soc = state.get('soc', 0.5)
    voltage = state.get('voltage', 230)
    freq = state.get('frequency', 50)
    is_safe = state.get('is_safe', True)
    cbf_active = state.get('cbf_active', False)
    barrier = state.get('barrier_value', 1.0)
    
    # 2. Dynamic Colors
    batt_color = RefinedPalette.BATTERY if soc > 0.4 else (RefinedPalette.WARN if soc > 0.2 else RefinedPalette.DANGER)
    cbf_color = RefinedPalette.SAFE if is_safe else RefinedPalette.DANGER
    if cbf_active: cbf_color = RefinedPalette.WARN
    
    # 3. Layout Configuration (Normalized 0-1 coord system)
    # Positions (cx, cy)
    POS_SOLAR = (0.2, 0.82)
    POS_CBF   = (0.5, 0.82)
    POS_LOAD  = (0.8, 0.82)
    POS_BATTERY = (0.3, 0.20)
    POS_GRID    = (0.7, 0.20)
    
    BUS_Y = 0.51
    ICON_SCALE = 2.5 # Scale factor for the SVG paths
    
    fig = go.Figure()
    
    # =========================================================================
    # DRAWING HELPER
    # =========================================================================
    def add_icon(pos, path_svg, color, label, value_text, subtext=None, scale=1.0):
        cx, cy = pos
        
        # 1. Icon Shape (Path)
        fig.add_shape(
            type="path",
            path=path_svg,
            fillcolor=color, # Solid fill for clean look
            line=dict(color=color, width=1),
            opacity=0.9,
            x0=cx - 0.08, y0=cy - 0.08, # Bounds aren't strictly used by path, but help Plotly auto-range if needed
            x1=cx + 0.08, y1=cy + 0.08,
            xref="x", yref="y",
            xsizemode="pixel", ysizemode="pixel",
            xanchor=cx, yanchor=cy
        )
        
        # NOTE: Plotly 'path' shapes in data coordinates can be tricky to scale universally without transforms.
        # Alternatively, we use Scatter markers with custom SVG paths, OR we just map the SVG content.
        # For reliability in this 'Refined' version, we will actually use Marker symbols where possible, 
        # or simplified paths interpreted manually if needed. 
        # BUT, standard plotly paths are absolute coordinates. 
        # To make it easy, we will use a TRANSFORMED path string generator.
        
        scaled_path = _transform_svg_path(path_svg, cx, cy, 0.12 * scale, 0.12 * scale)
        
        # Halo / Glow (Circle behind)
        fig.add_shape(
            type="circle",
            x0=cx - 0.09*scale, y0=cy - 0.09*scale,
            x1=cx + 0.09*scale, y1=cy + 0.09*scale,
            fillcolor=color,
            opacity=0.15,
            line=dict(width=0),
            layer="below"
        )
        
        # Actual Icon Line Drawing
        fig.add_shape(
            type="path",
            path=scaled_path,
            fillcolor=color,
            line=dict(width=0), # Fill only
            layer="above"
        )
        
        # Labels
        fig.add_annotation(
            x=cx, y=cy + 0.11,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color=RefinedPalette.TEXT_DIM, size=12)
        )
        fig.add_annotation(
            x=cx, y=cy - 0.11,
            text=f"<b>{value_text}</b>",
            showarrow=False,
            font=dict(color=color, size=16, family="monospace")
        )
        if subtext:
             fig.add_annotation(
                x=cx, y=cy - 0.15,
                text=subtext,
                showarrow=False,
                font=dict(color=RefinedPalette.TEXT_DIM, size=11)
            )

    # =========================================================================
    # COMPONENTS
    # =========================================================================
    
    # Solar
    add_icon(POS_SOLAR, ICONS["SOLAR"], RefinedPalette.SOLAR, "SOLAR PV", f"{p_pv:.1f} kW")
    
    # Load
    add_icon(POS_LOAD, ICONS["LOAD"], RefinedPalette.LOAD, "LOAD", f"{p_load:.1f} kW")
    
    # Battery
    batt_sub = f"{soc*100:.0f}%"
    add_icon(POS_BATTERY, ICONS["BATTERY"], batt_color, "BATTERY", f"{abs(p_batt):.1f} kW", batt_sub)
    
    # Grid
    grid_lbl = "IMPORT" if p_grid > 0 else "EXPORT"
    add_icon(POS_GRID, ICONS["GRID"], RefinedPalette.GRID, "GRID", f"{abs(p_grid):.1f} kW", grid_lbl)
    
    # U-CBF Shield
    shield_sub = f"h = {barrier:.2f}"
    shield_lbl = "ACTIVE" if cbf_active else ("SAFE" if is_safe else "VIOLATION")
    add_icon(POS_CBF, ICONS["SHIELD"], cbf_color, "U-CBF CORE", shield_lbl, shield_sub, scale=1.3)
    
    # =========================================================================
    # POWER BUS & CONNECTIONS
    # =========================================================================
    
    # Bus Bar
    fig.add_shape(
        type="rect",
        x0=0.05, y0=BUS_Y - 0.02,
        x1=0.95, y1=BUS_Y + 0.02,
        fillcolor="#F97316", # Orange bus
        line=dict(color="#C2410C", width=2),
        layer="below"
    )
    
    # Connection Lines (Vertical/Horizontal)
    def connect(x, y_start, y_end, color):
        fig.add_shape(type="line", x0=x, y0=y_start, x1=x, y1=y_end, 
                      line=dict(color=color, width=2, dash="dot"), layer="below")
        
    # Wire connections
    connect(POS_SOLAR[0], POS_SOLAR[1]-0.15, BUS_Y, RefinedPalette.SOLAR)
    connect(POS_LOAD[0], POS_LOAD[1]-0.15, BUS_Y, RefinedPalette.LOAD)
    connect(POS_CBF[0], POS_CBF[1]-0.15, BUS_Y, cbf_color)
    connect(POS_BATTERY[0], POS_BATTERY[1]+0.15, BUS_Y, batt_color)
    connect(POS_GRID[0], POS_GRID[1]+0.15, BUS_Y, RefinedPalette.GRID)

    # =========================================================================
    # ANIMATIONS (PARTICLES)
    # =========================================================================
    
    offset = animation_frame * 0.1
    
    # Helper to add flow
    def add_flow(x, y_start, y_end, color, direction="down"):
        # Determine start/end based on flow direction preference
        # If 'down', particles move y_start -> y_end
        # checks logic external to this func
        _add_animated_flow(fig, x, y_start, x, y_end, color, offset, direction)

    # PV -> Bus
    if p_pv > 0.1:
        add_flow(POS_SOLAR[0], POS_SOLAR[1]-0.15, BUS_Y+0.02, RefinedPalette.SOLAR, "down")

    # Bus -> Load
    if p_load > 0.1:
        add_flow(POS_LOAD[0], BUS_Y+0.02, POS_LOAD[1]-0.15, RefinedPalette.LOAD, "up")
        
    # Battery <-> Bus
    if abs(p_batt) > 0.1:
        direction = "up" if p_batt > 0 else "down" # Discharging (>0) = up to bus
        # If charging (<0), down from bus
        y1, y2 = POS_BATTERY[1]+0.15, BUS_Y-0.02
        add_flow(POS_BATTERY[0], y1, y2, batt_color, direction)
        
    # Grid <-> Bus
    if abs(p_grid) > 0.1:
        direction = "up" if p_grid > 0 else "down" # Import (>0) = up to bus
        y1, y2 = POS_GRID[1]+0.15, BUS_Y-0.02
        add_flow(POS_GRID[0], y1, y2, RefinedPalette.GRID, direction)

    # =========================================================================
    # GLOBAL LAYOUT
    # =========================================================================
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        height=450,
        showlegend=False
    )
    
    # Bus Label
    fig.add_annotation(
        x=0.5, y=BUS_Y,
        text=f"<b>AC BUS | {voltage:.0f}V {freq:.1f}Hz</b>",
        font=dict(color="white", size=11, family="monospace"),
        showarrow=False,
        bgcolor="rgba(0,0,0,0.5)",
        borderpad=4,
        bordercolor="#C2410C",
        borderwidth=1,
        rx=4
    )

    return fig

# =============================================================================
# UTILS
# =============================================================================

def _transform_svg_path(svg_path: str, cx: float, cy: float, sx: float, sy: float) -> str:
    """
    Very basic SVG path transformer to scale and translate standard paths 
    defined around (0,0) to target coordinates.
    Handles M, L, C, Q, Z, A commands roughly.
    """
    commands = svg_path.split()
    new_cmds = []
    
    # This is a naive parser; strictly assumes space-delimited standard SVG path d-string
    # And assumes relative/absolute commands handled simply.
    # Actually, proper SVG parsing is complex. 
    # For these specific simple icons defined above, we can just perform 
    # a manual string formatting if we defined them as lists of points, 
    # or use a smarter regex approach.
    
    # REVISED STRATEGY: 
    # The constants above are simple strings. We will parse numbers and scale them.
    # Non-numbers (letters) are kept as is.
    
    # We will assume absolute coordinates in the definitions above used a -0.5 to 0.5 range?
    # Actually I defined them relative to center 0.0.
    
    import re
    tokens = re.findall(r'[A-Za-z]|[-+]?[0-9]*\.?[0-9]+', svg_path)
    
    transformed = []
    for token in tokens:
        if token.isalpha():
            transformed.append(token)
        else:
            try:
                val = float(token)
                # We alternate X and Y? No, SVG commands vary.
                # To do this safely without a full parser, we will simplify:
                # We will ONLY scale the 'd' string if it's strictly numeric sequences.
                # But generic SVG is hard.
                
                # ALTERNATIVE: Just use Plotly's 'path' shape which supports a transform string?
                # Plotly shapes don't support 'transform="translate(...) scale(...)"' natively in the layout shape dict easily
                # without using SVG strings which Plotly supports but maybe not fully for 'shape'.
                
                # Let's try the simplest robust way:
                # Don't transform here. Define scale in layout? No.
                # Just Parse all numbers. 
                # Since all my defined icons use simplistic M x,y ... structure,
                # we can assume pairs.
                # BUT 'A' command has radius, rotation etc.
                
                # FALLBACK: 
                # Let's use a specialized function for just these known icons.
                pass 
            except ValueError:
                pass
    
    # Since writing a full SVG parser in 100ms runtime is bad, 
    # I will do a character-stream parse which is safer for these specific strings.
    
    res = []
    
    # Identify number indices
    # We will assume the icons are defined cleanly.
    # Actually, let's use a simpler approach: 
    # Define the geometry as Python lists of polygons for the simple ones, 
    # and just one complex one (Sun).
    
    # Better yet, let's just do the numeric replacement using regex with a callback
    # that tracks X/Y toggle? That's risky for 'A' commands.
    
    # For this specific task, I'll rewrite the paths in the constants to be formatted strings
    # and format them at runtime? No, too messy.
    
    # BEST APPROACH FOR ROBUSTNESS: 
    # Use the regex to find numbers.
    # Since all my paths are relative to 0,0, and I control them...
    # I will just scale X and Y.
    # 'A' command args: rx ry x-axis-rotation large-arc-flag sweep-flag x y
    # rx, ry are lengths (Scale). rotation (No scale). flags (No scale). x,y (Scale+Translate).
    
    # Since I only have lines (L) and Moves (M) and one Arc (A) in Solar...
    # I will simplify the Solar icon to lines for safety, or careful manual handling.
    # Solar icon above: "M ... a ... a ..." (relative arc).
    
    # Re-writing tokens loop with basic state machine for the specific ICONS used.
    
    current_cmd = ''
    idx = 0
    
    # simplified helper to scale a value
    def tx(v): return float(v) * sx + cx
    def ty(v): return float(v) * sy + cy
    def s(v): return float(v) * sx # scalar scale
    
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            current_cmd = t
            res.append(t)
            i += 1
        else:
            # It's a number. Handle based on command.
            # M x y
            # L x y
            # C x1 y1 x2 y2 x y
            # Q x1 y1 x y
            # A rx ry rot large sweep x y
            # Z (no args)
            # H x, V y
            # Lowercase = relative. UPcase = absolute.
            
            # Since I can redefine the constants, I will use ONLY M, L, Z and C (absolute) to make this easy.
            # I will redefine the icons in the CREATE function to be render-ready or simple logic.
            pass
            i+=1
            
    # HACK: For this specific file, I will just rewrite the _transform_svg_path to be a simple 
    # regex sub that assumes all numbers are coordinates and scales them. 
    # This works for M, L, C, Q if we don't use Arc or rotation.
    # I will Replace the 'SOLAR' arc path with a Line-only starburst to be safe.
    
    def repl(match):
        val = float(match.group())
        # We don't know if it's X or Y without context.
        # But if we assume square scaling (sx==sy) and no rotation, 
        # then scalar scaling is identical.
        # Translation is the catch.
        return str(val) # Placeholder
        
    return "" # Replace with local implementation in the main function

# =============================================================================
# REDEFINED ICONS (Absolute M/L/C only for safe parsing)
# =============================================================================
# Scaled roughly to -0.5 to 0.5.
# We will manually apply (val * scale + center) logic.

def _get_icon_path(name, cx, cy, scale):
    s = scale
    
    # Helper for points
    def p(x, y): return f"{cx + x*s:.3f},{cy + y*s:.3f}"
    
    if name == "LOAD":
        # House
        return (f"M {p(-0.4, 0.1)} L {p(-0.4, 0.5)} "
                f"L {p(0.4, 0.5)} L {p(0.4, 0.1)} "
                f"L {p(0, -0.4)} Z " # Roof/Body
                f"M {p(0.25, -0.2)} L {p(0.25, -0.4)} " # Chimney
                f"L {p(0.4, -0.4)} L {p(0.4, -0.05)}")
                
    elif name == "BATTERY":
        # Body and Terminal
        return (f"M {p(-0.3, -0.4)} L {p(0.3, -0.4)} "
                f"L {p(0.3, 0.4)} L {p(-0.3, 0.4)} Z "
                f"M {p(-0.15, -0.5)} L {p(0.15, -0.5)} "
                f"L {p(0.15, -0.4)} L {p(-0.15, -0.4)} Z")
                
    elif name == "GRID":
        # Pylon simplified
        return (f"M {p(0, -0.4)} L {p(0, 0.5)} " # Spine
                f"M {p(-0.3, 0.2)} L {p(0.3, 0.2)} " # Arm 1
                f"M {p(-0.2, -0.1)} L {p(0.2, -0.1)} " # Arm 2
                f"M {p(-0.25, 0.5)} L {p(0, -0.4)} L {p(0.25, 0.5)}") # Legs
                
    elif name == "SOLAR":
        # Sun with rays (Lines only)
        # Center box approx circle
        core = (f"M {p(-0.2, -0.2)} L {p(0.2, -0.2)} "
                f"L {p(0.2, 0.2)} L {p(-0.2, 0.2)} Z")
        rays = ""
        for i in range(8):
            ang = i * (math.pi / 4)
            r1, r2 = 0.3, 0.5
            x1, y1 = math.cos(ang)*r1, math.sin(ang)*r1
            x2, y2 = math.cos(ang)*r2, math.sin(ang)*r2
            rays += f" M {p(x1, y1)} L {p(x2, y2)}"
        return core + rays
        
    elif name == "SHIELD":
        # Simple Shield
        return (f"M {p(-0.35, -0.3)} "
                f"Q {p(0, -0.4)} {p(0.35, -0.3)} " # Top curve
                f"Q {p(0.35, 0.1)} {p(0, 0.4)} "   # Side/Bottom R
                f"Q {p(-0.35, 0.1)} {p(-0.35, -0.3)} " # Side/Bottom L
                f"Z")
                
    return ""

# Overwriting the generic helper to use this specific one
def _transform_svg_path(svg_path, cx, cy, sx, sy):
    # This is a dummy for the linter/logic flow, 
    # we actually call _get_icon_path directly in a modified add_icon
    return "" 
    
def add_icon_proxy(fig, name, pos, color, label, value_text, subtext=None, scale=1.0):
    cx, cy = pos
    path = _get_icon_path(name, cx, cy, 0.12 * scale)
    
    # Fill/Stroke
    fig.add_shape(
        type="path",
        path=path,
        fillcolor=color if name != "GRID" and name != "SOLAR" else "rgba(0,0,0,0)", # Grid/Solar more line-based
        line=dict(color=color, width=2),
        layer="above"
    )
    
    # Glow backing
    fig.add_shape(
        type="circle",
        x0=cx - 0.1*scale, y0=cy - 0.1*scale,
        x1=cx + 0.1*scale, y1=cy + 0.1*scale,
        fillcolor=color,
        opacity=0.1,
        line=dict(width=0),
        layer="below"
    )
    
    # Labels (re-using previous logic)
    fig.add_annotation(
        x=cx, y=cy + 0.11*scale,
        text=f"<b>{label}</b>",
        showarrow=False,
        font=dict(color=RefinedPalette.TEXT_DIM, size=11)
    )
    fig.add_annotation(
        x=cx, y=cy - 0.13*scale,
        text=f"<b>{value_text}</b>",
        showarrow=False,
        font=dict(color=color, size=15, family="monospace")
    )
    if subtext:
        fig.add_annotation(
            x=cx, y=cy - 0.17*scale,
            text=subtext,
            showarrow=False,
            font=dict(color=RefinedPalette.TEXT_DIM, size=10)
        )

# REPLACING THE DRAWING HELPER INSIDE create_refined_microgrid with add_icon_proxy logic
# We need to monkey-patch or just paste the correct function body. 
# Since I am writing the whole file, I will rewrite the body of create_refined_microgrid below correctly.

# ... (Redefining the main function to use the improved helpers) ...
def create_refined_microgrid(state: Optional[Dict[str, Any]] = None, animation_frame: float = 0.0, theme: str = 'light') -> go.Figure:
    if state is None: state = {}
    
    p_pv = state.get('p_pv', 0)
    p_batt = state.get('p_battery', 0)
    p_grid = state.get('p_grid', 0)
    p_load = state.get('p_load', 0)
    soc = state.get('soc', 0.5)
    voltage = state.get('voltage', 230)
    freq = state.get('frequency', 50)
    is_safe = state.get('is_safe', True)
    cbf_active = state.get('cbf_active', False)
    barrier = state.get('barrier_value', 1.0)
    
    batt_color = RefinedPalette.BATTERY if soc > 0.4 else (RefinedPalette.WARN if soc > 0.2 else RefinedPalette.DANGER)
    cbf_color = RefinedPalette.SAFE if is_safe else RefinedPalette.DANGER
    if cbf_active: cbf_color = RefinedPalette.WARN
    
    # Positions
    POS_SOLAR = (0.2, 0.75)
    POS_CBF   = (0.5, 0.75)
    POS_LOAD  = (0.8, 0.75)
    POS_BATTERY = (0.3, 0.25)
    POS_GRID    = (0.7, 0.25)
    BUS_Y = 0.5
    
    fig = go.Figure()
    
    # 1. Connectors (Behind)
    for x, y, c in [(POS_SOLAR[0], POS_SOLAR[1]-0.1, RefinedPalette.SOLAR), 
                    (POS_LOAD[0], POS_LOAD[1]-0.1, RefinedPalette.LOAD),
                    (POS_CBF[0], POS_CBF[1]-0.1, cbf_color)]:
        fig.add_shape(type="line", x0=x, y0=y, x1=x, y1=BUS_Y, line=dict(color="#CBD5E1", width=2, dash="dot"), layer="below")
        
    for x, y, c in [(POS_BATTERY[0], POS_BATTERY[1]+0.1, batt_color), 
                    (POS_GRID[0], POS_GRID[1]+0.1, RefinedPalette.GRID)]:
        fig.add_shape(type="line", x0=x, y0=y, x1=x, y1=BUS_Y, line=dict(color="#CBD5E1", width=2, dash="dot"), layer="below")

    # 2. Bus
    fig.add_shape(type="rect", x0=0.05, y0=BUS_Y-0.025, x1=0.95, y1=BUS_Y+0.025, 
                  fillcolor="white", line=dict(color="#F97316", width=2))
    fig.add_annotation(x=0.5, y=BUS_Y, text=f"<b>AC BUS | {voltage:.0f}V {freq:.1f}Hz</b>", 
                       font=dict(color="#F97316", size=11, family="monospace"), showarrow=False)

    # 3. Icons
    add_icon_proxy(fig, "SOLAR", POS_SOLAR, RefinedPalette.SOLAR, "SOLAR", f"{p_pv:.1f} kW")
    add_icon_proxy(fig, "LOAD", POS_LOAD, RefinedPalette.LOAD, "LOAD", f"{p_load:.1f} kW")
    add_icon_proxy(fig, "BATTERY", POS_BATTERY, batt_color, "BATTERY", f"{abs(p_batt):.1f} kW", f"{soc*100:.0f}%")
    add_icon_proxy(fig, "GRID", POS_GRID, RefinedPalette.GRID, "GRID", f"{abs(p_grid):.1f} kW", "IMPORT" if p_grid > 0 else "EXPORT")
    
    cbf_txt = "ACTIVE" if cbf_active else "SAFE"
    if not is_safe: cbf_txt = "UNSAFE"
    add_icon_proxy(fig, "SHIELD", POS_CBF, cbf_color, "U-CBF", cbf_txt, f"h={barrier:.2f}", scale=1.2)

    # 4. Particles
    offset = animation_frame * 0.1
    
    def flow(x1, y1, x2, y2, c, d):
        _add_animated_flow(fig, x1, y1, x2, y2, c, offset, d)
        
    if p_pv > 0.5: flow(POS_SOLAR[0], POS_SOLAR[1]-0.15, POS_SOLAR[0], BUS_Y+0.03, RefinedPalette.SOLAR, "down")
    if p_load > 0.5: flow(POS_LOAD[0], BUS_Y+0.03, POS_LOAD[0], POS_LOAD[1]-0.15, RefinedPalette.LOAD, "up") # Wait, load consumes, so flow TO load. 'up' means 'towards end'? No, direction arg logic.
    # Logic from simple: "up" = away from bus? No.
    # "down" = t from 0 to 1. "up" = t from 1 to 0.
    # Solar(Top) -> Bus(Mid). Downgradient. (0.8 -> 0.5). Correct.
    # Bus(Mid) -> Load(Top). Upgradient. (0.5 -> 0.8). Correct.
    
    if abs(p_batt) > 0.5:
        # Bat(Low) <-> Bus(Mid). 
        # Charge (P<0): Bus -> Bat. Down (0.5->0.2).
        # Discharge (P>0): Bat -> Bus. Up (0.2->0.5).
        d = "up" if p_batt > 0 else "down"
        flow(POS_BATTERY[0], POS_BATTERY[1]+0.15, POS_BATTERY[0], BUS_Y-0.03, batt_color, d)

    if abs(p_grid) > 0.5:
        # Grid(Low) <-> Bus(Mid).
        # Import (P>0): Grid -> Bus. Up.
        # Export (P<0): Bus -> Grid. Down.
        d = "up" if p_grid > 0 else "down"
        flow(POS_GRID[0], POS_GRID[1]+0.15, POS_GRID[0], BUS_Y-0.03, RefinedPalette.GRID, d)

    # Layout
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(l=10, r=10, t=30, b=30),
        xaxis=dict(range=[0,1], showgrid=False, visible=False, fixedrange=True),
        yaxis=dict(range=[0,1], showgrid=False, visible=False, fixedrange=True),
        height=420,
        showlegend=False
    )
    
    return fig

def _add_animated_flow(fig, x1, y1, x2, y2, color, offset, direction):
    # Copied from efficient simple version
    dist = abs(y2-y1) + abs(x2-x1)
    num = max(3, int(dist * 12))
    for i in range(num):
        t = ((i/num) + offset) % 1.0 if direction == "down" else ((1 - i/num) + offset) % 1.0
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        
        # Scale size by proximity to center of packet? No, just trail.
        op = 0.4 + 0.6 * (1 - abs(t-0.5)*2)
        sz = 4 + 4 * (1 - abs(t-0.5)*2)
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers',
            marker=dict(size=sz, color=color, opacity=op),
            hoverinfo='skip'
        ))

if __name__ == "__main__":
    create_refined_microgrid().show()
