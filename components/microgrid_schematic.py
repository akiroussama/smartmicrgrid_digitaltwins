"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   MICROGRID DIGITAL TWIN - HYPERCINEMATIC EDITION v4.0                       ║
║   ═══════════════════════════════════════════════════════════════════════   ║
║                                                                              ║
║   🏆 TURING PRIZE 2026 CANDIDATE                                            ║
║                                                                              ║
║   Upgrades over v3 (your current working version):                           ║
║   • True Bezier-powered particle flows (electrons follow smooth curves)      ║
║   • Gradient “plasma stream” particles (head–tail fading, variable size)     ║
║   • Stronger spatial separation & depth layering (hyper-cinematic)           ║
║   • Refined U‑CBF energy field (crisper geometry and glow balance)          ║
║   • Extra hover info & polish while preserving your API and behavior         ║
║                                                                              ║
║   Core features (retained & enhanced):                                       ║
║   • Animated particle flow along power routes                                ║
║   • Glowing neon components with glass-morphism                              ║
║   • 3D isometric-inspired rendering of PV, battery, load, grid              ║
║   • Energy field visualization around U-CBF safety filter                   ║
║   • Cinematic dark theme + clean light theme (for thesis slides)            ║
║   • Publication-grade typography and tooltips                                ║
║                                                                              ║
║   Author:  Oussama AKIR                                                      ║
║   Institution: Sup'Com, University of Carthage, Tunisia                      ║
║   Date:    December 2025                                                     ║
║   Version: 4.0.0 - HyperCinematic Edition                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMATIC VERSION - Increment to force cache invalidation
# ═══════════════════════════════════════════════════════════════════════════════
SCHEMATIC_VERSION = "4.1.0"  # Updated: Fixed HUD overlap + label truncation

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import math
import random

# Plotly for interactive visualization
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots  # noqa: F401  (kept for extensibility)
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None  # type: ignore

# NumPy for calculations (optional)
try:
    import numpy as np  # noqa: F401
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CINEMATIC COLOR SYSTEM                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@dataclass(frozen=True)
class CinematicPalette:
    """
    Premium cinematic color palette inspired by high-end fintech dashboards
    and sci-fi interfaces. Designed for maximum visual impact.
    """
    # Deep Space Background
    VOID_BLACK: str = "#0a0a0f"
    DEEP_SPACE: str = "#0d1117"
    COSMIC_DARK: str = "#161b22"
    NEBULA_GRAY: str = "#21262d"
    STELLAR_GRAY: str = "#30363d"

    # Neon Accent Colors
    NEON_CYAN: str = "#00d4ff"
    NEON_BLUE: str = "#0080ff"
    ELECTRIC_PURPLE: str = "#a855f7"
    PLASMA_PINK: str = "#ec4899"

    # Energy Colors
    SOLAR_GOLD: str = "#fbbf24"
    SOLAR_ORANGE: str = "#f97316"
    FUSION_YELLOW: str = "#facc15"

    # Status Colors
    MATRIX_GREEN: str = "#00ff88"
    SAFE_EMERALD: str = "#10b981"
    WARNING_AMBER: str = "#f59e0b"
    DANGER_RED: str = "#ef4444"
    CRITICAL_RED: str = "#dc2626"

    # Battery Gradient
    BATTERY_FULL: str = "#22c55e"
    BATTERY_MID: str = "#84cc16"
    BATTERY_LOW: str = "#eab308"
    BATTERY_CRITICAL: str = "#ef4444"

    # Glass Effects
    GLASS_WHITE: str = "rgba(255, 255, 255, 0.05)"
    GLASS_BORDER: str = "rgba(255, 255, 255, 0.1)"
    GLASS_HIGHLIGHT: str = "rgba(255, 255, 255, 0.15)"

    # Grid/Power Colors
    GRID_BLUE: str = "#3b82f6"
    GRID_EXPORT: str = "#8b5cf6"
    POWER_BUS: str = "#f97316"
    COPPER_GLOW: str = "#fb923c"


@dataclass
class CinematicTheme:
    """Complete cinematic theme configuration - TURING PRIZE GRAND FORMAT."""
    font_family: str = "'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    font_mono: str = "'SF Mono', 'Fira Code', 'Consolas', monospace"

    # ═══ MASSIF SIZES (Thesis Defense - Back of Room Readable) ═══
    title_size: int = 32          # Was 24 → Now 32
    subtitle_size: int = 18       # Was 14 → Now 18
    label_size: int = 18          # Was 12 → Now 18 (Component labels)
    value_size: int = 28          # Was 18 → Now 28 (Component values)
    unit_size: int = 16           # Was 11 → Now 16

    # ═══ HUD SIZES (Balanced for visibility without overlap) ═══
    hud_label_size: int = 13      # HUD metric labels (reduced to prevent overlap)
    hud_value_size: int = 22      # HUD values (reduced from 36 - still visible, no overlap)
    hud_icon_size: int = 16       # HUD icons

    glow_blur: int = 20
    shadow_blur: int = 30

    particle_count: int = 12
    animation_duration: int = 2000  # ms


# Dark palette (default cinematic)
PALETTE = CinematicPalette()
THEME = CinematicTheme()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  LIGHT THEME PALETTE (for thesis presentation)                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@dataclass(frozen=True)
class LightPalette:
    """
    Professional light theme palette for thesis defense.
    Clean, scientific, publication-quality appearance.
    """

    # Light Background
    VOID_BLACK: str = "#FFFFFF"
    DEEP_SPACE: str = "#FAFBFC"
    COSMIC_DARK: str = "#F0F2F5"
    NEBULA_GRAY: str = "#E9ECEF"
    STELLAR_GRAY: str = "#6C757D"

    # Accent Colors
    NEON_CYAN: str = "#0077B6"
    NEON_BLUE: str = "#0096C7"
    ELECTRIC_PURPLE: str = "#7C3AED"
    PLASMA_PINK: str = "#DB2777"

    # Energy Colors
    SOLAR_GOLD: str = "#F59E0B"
    SOLAR_ORANGE: str = "#EA580C"
    FUSION_YELLOW: str = "#EAB308"

    # Status Colors
    MATRIX_GREEN: str = "#10B981"
    SAFE_EMERALD: str = "#059669"
    WARNING_AMBER: str = "#D97706"
    DANGER_RED: str = "#DC2626"
    CRITICAL_RED: str = "#B91C1C"

    # Battery Gradient
    BATTERY_FULL: str = "#22C55E"
    BATTERY_MID: str = "#84CC16"
    BATTERY_LOW: str = "#EAB308"
    BATTERY_CRITICAL: str = "#EF4444"

    # Glass Effects
    GLASS_WHITE: str = "rgba(0, 0, 0, 0.03)"
    GLASS_BORDER: str = "rgba(0, 0, 0, 0.08)"
    GLASS_HIGHLIGHT: str = "rgba(0, 0, 0, 0.05)"

    # Grid/Power Colors
    GRID_BLUE: str = "#2563EB"
    GRID_EXPORT: str = "#7C3AED"
    POWER_BUS: str = "#EA580C"
    COPPER_GLOW: str = "#F97316"


LIGHT_THEME = LightPalette()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  SPACIOUS LAYOUT SYSTEM                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@dataclass
class SpacedLayout:
    """
    GRAND FORMAT LAYOUT - Thesis Defense Edition.
    Schematic compressed up, massive HUD at bottom.
    Uses 100% width, optimized for large screen presentation.
    """
    WIDTH: float = 1.0
    HEIGHT: float = 1.0

    # ═══ COMPRESSED SCHEMATIC (pushed UP to leave room for HUD) ═══
    # Top: Solar Array - pushed higher
    SOLAR: Tuple[float, float] = (0.50, 0.92)

    # Middle: Power Bus - raised
    BUS_Y: float = 0.68
    BUS_X_START: float = 0.02      # Edge-to-edge (was 0.08)
    BUS_X_END: float = 0.98        # Edge-to-edge (was 0.92)

    # Component Row - raised to make room for HUD
    BATTERY: Tuple[float, float] = (0.12, 0.38)    # Was 0.22
    CBF_FILTER: Tuple[float, float] = (0.50, 0.38) # Was 0.22
    LOAD: Tuple[float, float] = (0.88, 0.38)       # Was 0.22

    # External Grid - adjusted
    GRID: Tuple[float, float] = (0.12, 0.10)       # Was -0.08

    # ═══ COMPONENT SIZES (optimized for no overlap) ═══
    SOLAR_W: float = 0.36          # Solar panel width
    SOLAR_H: float = 0.12          # Solar panel height

    BATTERY_W: float = 0.14        # Battery width
    BATTERY_H: float = 0.18        # Battery height

    CBF_W: float = 0.26            # CBF width (no overlap with neighbors)
    CBF_H: float = 0.22            # CBF height

    LOAD_W: float = 0.14           # Load (house) width
    LOAD_H: float = 0.14           # Load height

    GRID_W: float = 0.12           # Grid transformer width
    GRID_H: float = 0.10           # Grid transformer height

    BUS_H: float = 0.035           # Power bus thickness

    # ═══ HUD ZONE (Bottom 25% of canvas) ═══
    HUD_Y: float = -0.18           # HUD center Y position
    HUD_HEIGHT: float = 0.12       # Height of each HUD panel
    HUD_PANEL_WIDTH: float = 0.145 # Width of each panel (6 panels fit)


LAYOUT = SpacedLayout()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN SCHEMATIC CREATOR                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def create_microgrid_schematic(
    state: Optional[Union[Dict, Any]] = None,
    show_animations: bool = True,
    theme: str = "dark",
    show_cbf_details: bool = True,
    show_values: bool = True,
    compact_mode: bool = False,
    particle_density: int = 12,
    fast_mode: bool = False,  # NEW: Skip heavy effects for faster initial load
) -> "go.Figure":
    """
    Hyper-cinematic microgrid schematic with animated particle flows,
    glowing components, and U‑CBF energy field.

    API is compatible with your existing cinematic implementation.

    Args:
        fast_mode: If True, skip particles, animations, and complex effects
                   for faster initial rendering (reduces load time by ~80%)
    """
    # Override settings in fast_mode for instant display
    if fast_mode:
        show_animations = False
        particle_density = 0  # No particles
    global PALETTE

    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly is required: pip install plotly")

    # Select palette
    if theme == "light":
        active_palette = LIGHT_THEME
        text_color = "#2C3E50"
    else:
        active_palette = CinematicPalette()
        text_color = "white"

    PALETTE = active_palette

    values = _extract_state(state)
    fig = go.Figure()

    height = 600 if not compact_mode else 480

    fig.update_layout(
        paper_bgcolor=active_palette.DEEP_SPACE,
        plot_bgcolor=active_palette.DEEP_SPACE,
        margin=dict(l=20, r=20, t=80, b=40),
        height=height,
        title=dict(
            text=_create_cinematic_title(values),
            font=dict(
                family=THEME.font_family,
                size=THEME.title_size,
                color=active_palette.NEON_CYAN,
            ),
            x=0.5,
            xanchor="center",
            y=0.96,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.08, 1.08],
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.30, 1.05],  # Extended for GRAND FORMAT HUD
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True,
        ),
        showlegend=False,
        hovermode="closest",
        dragmode=False,
        font=dict(family=THEME.font_family, color=text_color),
        # Skip animation buttons in fast_mode (saves rendering time)
        updatemenus=[] if fast_mode else [
            dict(
                type="buttons",
                showactive=False,
                x=0.02,
                y=-0.06,
                xanchor="left",
                buttons=[
                    dict(
                        label="▶ LIVE",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 80, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                    dict(
                        label="⏸ PAUSE",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                ],
                font=dict(color=active_palette.NEON_CYAN, size=11),
                bgcolor=active_palette.COSMIC_DARK,
                bordercolor=active_palette.NEON_CYAN,
                borderwidth=1,
            )
        ],
    )

    # LAYERS (back → front)
    _render_background_grid(fig)

    # Skip heavy visual effects in fast_mode (saves ~40% render time)
    if not fast_mode:
        _render_glow_effects(fig, values)
        _render_bezier_connections(fig, values)
    _render_power_bus_3d(fig, values)

    _render_solar_array_3d(fig, values, show_values)
    _render_battery_3d(fig, values, show_values)
    _render_cbf_shield_ultra(fig, values, show_cbf_details)
    _render_load_3d_ultra(fig, values, show_values)
    _render_grid_3d(fig, values, show_values)

    _render_power_flow_static(fig, values)

    if show_animations:
        _add_particle_animation(fig, values, particle_density)

    # Skip HUD in fast_mode - dashboard has its own status bar
    if not fast_mode:
        _render_status_hud(fig, values)
        # Optional: bus hover with aggregate info (net power, etc.)
        _add_bus_hover(fig, values)

    return fig


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STATE EXTRACTION                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _extract_state(state: Optional[Any]) -> Dict[str, float]:
    """Extract and validate state values."""
    defaults = {
        "p_pv": 42.5,
        "p_battery": -8.3,
        "p_grid": 12.1,
        "p_load": 46.3,
        "soc": 0.72,
        "voltage": 233.5,
        "frequency": 50.02,
        "cbf_active": False,
        "is_safe": True,
        "barrier_value": 38.7,
        "safety_margin": 6.5,
        "sigma_calibrated": 0.78,
        "tariff": 0.195,
        "irradiance": 920.0,
        "temperature": 28.5,
    }

    if state is None:
        return defaults

    if hasattr(state, "__dict__"):
        state_dict = vars(state)
    elif isinstance(state, dict):
        state_dict = state
    else:
        return defaults

    result = defaults.copy()
    for k in defaults:
        if k in state_dict and state_dict[k] is not None:
            result[k] = state_dict[k]

    result["soc"] = max(0.0, min(1.0, result["soc"]))
    return result


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CINEMATIC TITLE                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _create_cinematic_title(values: Dict) -> str:
    """Create epic cinematic title with status."""
    is_safe = values.get("is_safe", True)
    cbf_active = values.get("cbf_active", False)

    if not is_safe:
        status = f"<span style='color:{PALETTE.DANGER_RED}'>◉ VIOLATION DETECTED</span>"
    elif cbf_active:
        status = f"<span style='color:{PALETTE.WARNING_AMBER}'>◉ CBF INTERVENING</span>"
    else:
        status = f"<span style='color:{PALETTE.MATRIX_GREEN}'>◉ NOMINAL</span>"

    return (
        f"<b>MICROGRID DIGITAL TWIN</b>"
        f"<br><span style='font-size:12px; color:{PALETTE.STELLAR_GRAY};'>"
        f"Tunis, Tunisia · Real-Time Monitoring · {status}</span>"
    )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  BACKGROUND GRID                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_background_grid(fig: "go.Figure") -> None:
    """Render subtle futuristic grid pattern."""
    grid_color = "rgba(48, 54, 61, 0.3)"

    for x in [0.0, 0.25, 0.5, 0.75, 1.0]:
        fig.add_shape(
            type="line",
            x0=x,
            y0=-0.15,
            x1=x,
            y1=1.0,
            line=dict(color=grid_color, width=0.5),
            layer="below",
        )

    for y in [0.0, 0.25, 0.5, 0.75, 1.0]:
        fig.add_shape(
            type="line",
            x0=-0.05,
            y0=y,
            x1=1.05,
            y1=y,
            line=dict(color=grid_color, width=0.5),
            layer="below",
        )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  GLOW EFFECTS (Ambient lighting)                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_glow_effects(fig: "go.Figure", values: Dict) -> None:
    """Render ambient glow effects behind components."""
    _add_radial_glow(fig, LAYOUT.SOLAR[0], LAYOUT.SOLAR[1], PALETTE.SOLAR_GOLD, 0.25, 0.08)

    soc = values.get("soc", 0.5)
    if soc > 0.5:
        batt_glow = PALETTE.SAFE_EMERALD
    elif soc > 0.2:
        batt_glow = PALETTE.WARNING_AMBER
    else:
        batt_glow = PALETTE.DANGER_RED
    _add_radial_glow(fig, LAYOUT.BATTERY[0], LAYOUT.BATTERY[1], batt_glow, 0.18, 0.06)

    cbf_active = values.get("cbf_active", False)
    is_safe = values.get("is_safe", True)
    if not is_safe:
        cbf_glow = PALETTE.DANGER_RED
        cbf_intensity = 0.30
    elif cbf_active:
        cbf_glow = PALETTE.WARNING_AMBER
        cbf_intensity = 0.25
    else:
        cbf_glow = PALETTE.NEON_CYAN
        cbf_intensity = 0.15
    _add_radial_glow(fig, LAYOUT.CBF_FILTER[0], LAYOUT.CBF_FILTER[1], cbf_glow, 0.28, cbf_intensity)

    _add_radial_glow(fig, LAYOUT.LOAD[0], LAYOUT.LOAD[1], PALETTE.SOLAR_ORANGE, 0.18, 0.06)


def _add_radial_glow(
    fig: "go.Figure",
    cx: float,
    cy: float,
    color: str,
    radius: float,
    intensity: float,
) -> None:
    """Add radial gradient glow effect using layered circles."""
    layers = 8
    for i in range(layers, 0, -1):
        r = radius * (i / layers)
        opacity = intensity * (1 - i / layers) ** 0.5
        fig.add_shape(
            type="circle",
            x0=cx - r,
            y0=cy - r,
            x1=cx + r,
            y1=cy + r,
            fillcolor=_hex_to_rgba(color, opacity),
            line=dict(width=0),
            layer="below",
        )


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex to rgba string."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  BEZIER CONNECTION PATHS                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_bezier_connections(fig: "go.Figure", values: Dict) -> None:
    """Render elegant connection lines between components."""
    bus_y = LAYOUT.BUS_Y
    conn_style = dict(color=PALETTE.STELLAR_GRAY, width=2, dash="dot")

    sx, sy = LAYOUT.SOLAR
    _draw_bezier_vertical(
        fig,
        sx,
        sy - LAYOUT.SOLAR_H / 2 - 0.02,
        sx,
        bus_y + LAYOUT.BUS_H / 2 + 0.01,
        conn_style,
    )

    bx, by = LAYOUT.BATTERY
    _draw_bezier_vertical(
        fig,
        bx,
        by + LAYOUT.BATTERY_H / 2 + 0.02,
        bx,
        bus_y - LAYOUT.BUS_H / 2 - 0.01,
        conn_style,
    )

    cx, cy = LAYOUT.CBF_FILTER
    _draw_bezier_vertical(
        fig,
        cx,
        cy + LAYOUT.CBF_H / 2,
        cx,
        bus_y - LAYOUT.BUS_H / 2 - 0.01,
        conn_style,
    )

    lx, ly = LAYOUT.LOAD
    _draw_bezier_vertical(
        fig,
        lx,
        ly + LAYOUT.LOAD_H / 2 + 0.02,
        lx,
        bus_y - LAYOUT.BUS_H / 2 - 0.01,
        conn_style,
    )

    gx, gy = LAYOUT.GRID
    _draw_bezier_curve(
        fig,
        gx,
        gy + LAYOUT.GRID_H / 2 + 0.02,
        bx,
        by - LAYOUT.BATTERY_H / 2 - 0.02,
        conn_style,
    )


def _draw_bezier_vertical(
    fig: "go.Figure",
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    style: dict,
) -> None:
    fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=style, layer="below")


def _draw_bezier_curve(
    fig: "go.Figure",
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    style: dict,
) -> None:
    mid_y = (y0 + y1) / 2
    path = f"M {x0},{y0} Q {x0},{mid_y} {(x0 + x1)/2},{mid_y} T {x1},{y1}"
    fig.add_shape(type="path", path=path, line=style, layer="below")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3D POWER BUS                                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_power_bus_3d(fig: "go.Figure", values: Dict) -> None:
    """Render 3D-style power distribution bus with glow."""
    y = LAYOUT.BUS_Y
    x0, x1 = LAYOUT.BUS_X_START, LAYOUT.BUS_X_END
    h = LAYOUT.BUS_H

    for i in range(5, 0, -1):
        glow_h = h + i * 0.015
        fig.add_shape(
            type="rect",
            x0=x0 - 0.01,
            y0=y - glow_h / 2,
            x1=x1 + 0.01,
            y1=y + glow_h / 2,
            fillcolor=_hex_to_rgba(PALETTE.POWER_BUS, 0.03 * i),
            line=dict(width=0),
            layer="below",
        )

    fig.add_shape(
        type="rect",
        x0=x0 + 0.005,
        y0=y - h / 2 - 0.008,
        x1=x1 + 0.005,
        y1=y + h / 2 - 0.008,
        fillcolor="rgba(0, 0, 0, 0.4)",
        line=dict(width=0),
        layer="below",
    )

    fig.add_shape(
        type="rect",
        x0=x0,
        y0=y - h / 2,
        x1=x1,
        y1=y + h / 2,
        fillcolor="#c2410c",
        line=dict(color=PALETTE.COPPER_GLOW, width=2),
    )

    fig.add_shape(
        type="rect",
        x0=x0 + 0.01,
        y0=y + h / 2 - 0.008,
        x1=x1 - 0.01,
        y1=y + h / 2 - 0.002,
        fillcolor="rgba(255, 200, 150, 0.4)",
        line=dict(width=0),
    )

    node_positions = [
        LAYOUT.SOLAR[0],
        LAYOUT.BATTERY[0],
        LAYOUT.CBF_FILTER[0],
        LAYOUT.LOAD[0],
    ]
    for nx in node_positions:
        fig.add_shape(
            type="circle",
            x0=nx - 0.025,
            y0=y - 0.025,
            x1=nx + 0.025,
            y1=y + 0.025,
            fillcolor=_hex_to_rgba(PALETTE.NEON_CYAN, 0.2),
            line=dict(width=0),
        )
        fig.add_shape(
            type="circle",
            x0=nx - 0.012,
            y0=y - 0.012,
            x1=nx + 0.012,
            y1=y + 0.012,
            fillcolor=PALETTE.DEEP_SPACE,
            line=dict(color=PALETTE.NEON_CYAN, width=2),
        )

    fig.add_annotation(
        x=(x0 + x1) / 2,
        y=y,
        text="<b>◆ AC POWER BUS ◆ 230V 50Hz</b>",
        showarrow=False,
        font=dict(family=THEME.font_mono, size=10, color="white"),
    )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3D SOLAR ARRAY                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_solar_array_3d(fig: "go.Figure", values: Dict, show_values: bool) -> None:
    cx, cy = LAYOUT.SOLAR
    w, h = LAYOUT.SOLAR_W, LAYOUT.SOLAR_H
    p_pv = values.get("p_pv", 0.0)
    irradiance = values.get("irradiance", 850.0)

    fig.add_shape(
        type="rect",
        x0=cx - w / 2 + 0.008,
        y0=cy - h / 2 - 0.012,
        x1=cx + w / 2 + 0.008,
        y1=cy + h / 2 - 0.012,
        fillcolor="rgba(0, 0, 0, 0.5)",
        line=dict(width=0),
        layer="below",
    )

    fig.add_shape(
        type="rect",
        x0=cx - w / 2,
        y0=cy - h / 2,
        x1=cx + w / 2,
        y1=cy + h / 2,
        fillcolor=PALETTE.NEBULA_GRAY,
        line=dict(color=PALETTE.STELLAR_GRAY, width=2),
    )

    cells_x, cells_y = 5, 2
    margin = 0.012
    gap = 0.006
    cell_w = (w - 2 * margin - (cells_x - 1) * gap) / cells_x
    cell_h = (h - 2 * margin - (cells_y - 1) * gap) / cells_y

    for i in range(cells_x):
        for j in range(cells_y):
            cell_x = cx - w / 2 + margin + i * (cell_w + gap)
            cell_y = cy - h / 2 + margin + j * (cell_h + gap)
            fig.add_shape(
                type="rect",
                x0=cell_x,
                y0=cell_y,
                x1=cell_x + cell_w,
                y1=cell_y + cell_h,
                fillcolor="#1e3a5f",
                line=dict(color="#0f2744", width=1),
            )
            shimmer_opacity = 0.15 + 0.1 * ((i + j) % 2)
            fig.add_shape(
                type="rect",
                x0=cell_x + cell_w * 0.1,
                y0=cell_y + cell_h * 0.6,
                x1=cell_x + cell_w * 0.9,
                y1=cell_y + cell_h * 0.9,
                fillcolor=f"rgba(100, 180, 255, {shimmer_opacity})",
                line=dict(width=0),
            )

    for i in range(1, cells_x):
        bar_x = cx - w / 2 + margin + i * (cell_w + gap) - gap / 2
        fig.add_shape(
            type="line",
            x0=bar_x,
            y0=cy - h / 2 + margin,
            x1=bar_x,
            y1=cy + h / 2 - margin,
            line=dict(color="rgba(180, 180, 180, 0.6)", width=2),
        )

    fig.add_shape(
        type="line",
        x0=cx - w / 2 + margin,
        y0=cy,
        x1=cx + w / 2 - margin,
        y1=cy,
        line=dict(color="rgba(180, 180, 180, 0.6)", width=2),
    )

    sun_x = cx + w / 2 + 0.06
    sun_y = cy + 0.02
    sun_r = 0.025

    _add_radial_glow(fig, sun_x, sun_y, PALETTE.SOLAR_GOLD, 0.06, 0.3)

    for i in range(12):
        angle = i * (math.pi / 6)
        x1 = sun_x + math.cos(angle) * sun_r
        y1 = sun_y + math.sin(angle) * sun_r
        x2 = sun_x + math.cos(angle) * sun_r * 2
        y2 = sun_y + math.sin(angle) * sun_r * 2
        fig.add_shape(
            type="line",
            x0=x1,
            y0=y1,
            x1=x2,
            y1=y2,
            line=dict(color=PALETTE.SOLAR_GOLD, width=2),
        )

    fig.add_shape(
        type="circle",
        x0=sun_x - sun_r,
        y0=sun_y - sun_r,
        x1=sun_x + sun_r,
        y1=sun_y + sun_r,
        fillcolor=PALETTE.FUSION_YELLOW,
        line=dict(color=PALETTE.SOLAR_ORANGE, width=2),
    )

    efficiency = min(100.0, (p_pv / 50.0) * 100.0)
    fig.add_trace(
        go.Scatter(
            x=[cx],
            y=[cy],
            mode="markers",
            marker=dict(size=60, color="rgba(0,0,0,0)"),
            hovertemplate=(
                "<b style='color:#fbbf24'>☀ SOLAR PV ARRAY</b><br>"
                "─────────────────<br>"
                f"<b>Power Output:</b> {p_pv:.2f} kW<br>"
                f"<b>Irradiance:</b> {irradiance:.0f} W/m²<br>"
                f"<b>Efficiency:</b> {efficiency:.1f}%<br>"
                f"<b>Panels:</b> 10 × 500W<br>"
                f"<b>Temperature:</b> {values.get('temperature', 25):.1f}°C<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    if show_values:
        fig.add_annotation(
            x=cx,
            y=cy + h / 2 + 0.045,
            text="<b>SOLAR PV ARRAY</b>",
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=THEME.label_size,
                color=PALETTE.SOLAR_GOLD,
            ),
        )
        fig.add_annotation(
            x=cx,
            y=cy - h / 2 - 0.045,
            text=f"<b style='font-size:20px'>{p_pv:.1f}</b> <span style='font-size:12px'>kW</span>",
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=18,
                color=PALETTE.SOLAR_GOLD,
            ),
        )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3D BATTERY WITH LIQUID GAUGE                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_battery_3d(fig: "go.Figure", values: Dict, show_values: bool) -> None:
    cx, cy = LAYOUT.BATTERY
    w, h = LAYOUT.BATTERY_W, LAYOUT.BATTERY_H

    soc = values.get("soc", 0.5)
    p_battery = values.get("p_battery", 0.0)
    is_charging = p_battery > 0

    if soc >= 0.6:
        fill_color = PALETTE.BATTERY_FULL
        fill_light = "#4ade80"
    elif soc >= 0.3:
        fill_color = PALETTE.BATTERY_MID
        fill_light = "#a3e635"
    elif soc >= 0.15:
        fill_color = PALETTE.BATTERY_LOW
        fill_light = "#fbbf24"
    else:
        fill_color = PALETTE.BATTERY_CRITICAL
        fill_light = "#f87171"

    fig.add_shape(
        type="rect",
        x0=cx - w / 2 + 0.006,
        y0=cy - h / 2 - 0.010,
        x1=cx + w / 2 + 0.006,
        y1=cy + h / 2 - 0.010,
        fillcolor="rgba(0, 0, 0, 0.5)",
        line=dict(width=0),
        layer="below",
    )

    fig.add_shape(
        type="rect",
        x0=cx - w / 2,
        y0=cy - h / 2,
        x1=cx + w / 2,
        y1=cy + h / 2,
        fillcolor=PALETTE.COSMIC_DARK,
        line=dict(color=PALETTE.STELLAR_GRAY, width=2),
    )

    inner_m = 0.010
    cell_bottom = cy - h / 2 + inner_m
    cell_top = cy + h / 2 - inner_m - 0.02
    cell_height = cell_top - cell_bottom

    fig.add_shape(
        type="rect",
        x0=cx - w / 2 + inner_m,
        y0=cell_bottom,
        x1=cx + w / 2 - inner_m,
        y1=cell_top,
        fillcolor=PALETTE.VOID_BLACK,
        line=dict(width=0),
    )

    fill_height = cell_height * soc
    fill_top = cell_bottom + fill_height

    for i in range(5):
        layer_opacity = 0.6 + i * 0.08
        layer_bottom = cell_bottom + i * fill_height * 0.02
        fig.add_shape(
            type="rect",
            x0=cx - w / 2 + inner_m,
            y0=layer_bottom,
            x1=cx + w / 2 - inner_m,
            y1=fill_top,
            fillcolor=_hex_to_rgba(fill_color, layer_opacity),
            line=dict(width=0),
        )

    if fill_height > 0.02:
        fig.add_shape(
            type="line",
            x0=cx - w / 2 + inner_m + 0.01,
            y0=fill_top - 0.005,
            x1=cx + w / 2 - inner_m - 0.01,
            y1=fill_top - 0.005,
            line=dict(color="rgba(255,255,255,0.4)", width=3),
        )
        for bx, by in [
            (cx - 0.02, cell_bottom + fill_height * 0.3),
            (cx + 0.015, cell_bottom + fill_height * 0.5),
            (cx - 0.01, cell_bottom + fill_height * 0.7),
        ]:
            if by < fill_top - 0.01:
                fig.add_shape(
                    type="circle",
                    x0=bx - 0.004,
                    y0=by - 0.004,
                    x1=bx + 0.004,
                    y1=by + 0.004,
                    fillcolor="rgba(255,255,255,0.2)",
                    line=dict(width=0),
                )

    terminal_w = w * 0.4
    terminal_h = 0.020
    fig.add_shape(
        type="rect",
        x0=cx - terminal_w / 2,
        y0=cy + h / 2 - 0.002,
        x1=cx + terminal_w / 2,
        y1=cy + h / 2 + terminal_h,
        fillcolor=PALETTE.STELLAR_GRAY,
        line=dict(
            color=PALETTE.NEON_CYAN if is_charging else PALETTE.STELLAR_GRAY,
            width=1,
        ),
    )

    if is_charging:
        bolt_cx = cx
        bolt_cy = cy + 0.02
        bolt_size = 0.035
        bolt_path = (
            f"M {bolt_cx - bolt_size*0.3},{bolt_cy + bolt_size*0.5} "
            f"L {bolt_cx + bolt_size*0.15},{bolt_cy + bolt_size*0.05} "
            f"L {bolt_cx - bolt_size*0.05},{bolt_cy + bolt_size*0.05} "
            f"L {bolt_cx + bolt_size*0.3},{bolt_cy - bolt_size*0.5} "
            f"L {bolt_cx - bolt_size*0.15},{bolt_cy - bolt_size*0.05} "
            f"L {bolt_cx + bolt_size*0.05},{bolt_cy - bolt_size*0.05} Z"
        )
        fig.add_shape(
            type="path",
            path=bolt_path,
            fillcolor=PALETTE.FUSION_YELLOW,
            line=dict(color=PALETTE.SOLAR_ORANGE, width=1),
        )

    fig.add_annotation(
        x=cx,
        y=cy - 0.02,
        text=f"<b>{soc*100:.0f}%</b>",
        showarrow=False,
        font=dict(
            family=THEME.font_mono,
            size=20,
            color="white" if soc > 0.3 else fill_light,
        ),
    )

    status = (
        "⚡ Charging"
        if is_charging
        else "🔋 Discharging"
        if p_battery < 0
        else "● Idle"
    )
    fig.add_trace(
        go.Scatter(
            x=[cx],
            y=[cy],
            mode="markers",
            marker=dict(size=50, color="rgba(0,0,0,0)"),
            hovertemplate=(
                f"<b style='color:{fill_color}'>🔋 BATTERY STORAGE</b><br>"
                "─────────────────<br>"
                f"<b>State of Charge:</b> {soc*100:.1f}%<br>"
                f"<b>Power:</b> {abs(p_battery):.2f} kW<br>"
                f"<b>Status:</b> {status}<br>"
                f"<b>Capacity:</b> 50 kWh<br>"
                f"<b>Energy:</b> {soc*50:.1f} kWh<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    if show_values:
        fig.add_annotation(
            x=cx,
            y=cy + h / 2 + terminal_h + 0.04,
            text="<b>🔋 BATT</b>",  # Shortened to prevent truncation
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=THEME.label_size - 2,  # Slightly smaller
                color=fill_color,
            ),
        )
        status_symbol = "+" if is_charging else "−" if p_battery < 0 else ""
        power_color = (
            PALETTE.MATRIX_GREEN
            if is_charging
            else PALETTE.DANGER_RED
            if p_battery < 0
            else PALETTE.STELLAR_GRAY
        )
        fig.add_annotation(
            x=cx,
            y=cy - h / 2 - 0.045,
            text=f"<b>{status_symbol}{abs(p_battery):.1f}</b> kW",
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=THEME.value_size,
                color=power_color,
            ),
        )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  EPIC U-CBF SHIELD (STAR COMPONENT)                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_cbf_shield_ultra(
    fig: "go.Figure",
    values: Dict,
    show_details: bool,
    animation_frame: float = 0.0,  # 0.0 to 1.0 for animation state
    threat_sources: Optional[List[Tuple[float, float, float]]] = None,  # (x, y, intensity)
) -> None:
    """
    Render ultra-advanced U-CBF safety shield with holographic effects.
    
    Args:
        fig: Plotly figure object
        values: Dictionary containing CBF state values
        show_details: Whether to display detailed annotations
        animation_frame: Current animation frame (0.0 to 1.0)
        threat_sources: List of threat source positions and intensities
    """
    cx, cy = LAYOUT.CBF_FILTER
    w, h = LAYOUT.CBF_W, LAYOUT.CBF_H
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATE EXTRACTION & CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    cbf_active = values.get("cbf_active", False)
    is_safe = values.get("is_safe", True)
    barrier_value = values.get("barrier_value", 0.0)
    safety_margin = values.get("safety_margin", 0.0)
    sigma_calibrated = values.get("sigma_calibrated", 0.0)
    intervention_strength = values.get("intervention_strength", 0.0)
    constraint_slack = values.get("constraint_slack", 0.0)
    qp_solve_time = values.get("qp_solve_time", 0.001)
    
    # Normalize barrier for visual effects
    barrier_normalized = max(0, min(1, (barrier_value + 1) / 2))  # Map to 0-1
    
    # Calculate threat level (0 = safe, 1 = critical)
    if not is_safe:
        threat_level = 1.0
    elif cbf_active:
        threat_level = 0.5 + intervention_strength * 0.4
    else:
        threat_level = max(0, 0.3 - safety_margin / 10)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COLOR SYSTEM (State-Dependent with Gradients)
    # ═══════════════════════════════════════════════════════════════════════════
    class ShieldColors:
        if not is_safe:
            # CRITICAL - Red emergency state
            primary = "#ef4444"
            secondary = "#dc2626"
            tertiary = "#b91c1c"
            glow = "#ff6b6b"
            energy = "#ff0000"
            accent = "#fca5a5"
            status_text = "⚠ VIOLATION"
            energy_intensity = 0.8
            pulse_speed = 3.0
        elif cbf_active:
            # ACTIVE - Amber intervention state
            primary = "#f59e0b"
            secondary = "#d97706"
            tertiary = "#b45309"
            glow = "#fbbf24"
            energy = "#ff9500"
            accent = "#fcd34d"
            status_text = "⚡ ACTIVE"
            energy_intensity = 0.5
            pulse_speed = 2.0
        else:
            # NOMINAL - Cyan safe state
            primary = "#06b6d4"
            secondary = "#0891b2"
            tertiary = "#0e7490"
            glow = "#22d3ee"
            energy = "#00ffff"
            accent = "#67e8f9"
            status_text = "✓ NOMINAL"
            energy_intensity = 0.25
            pulse_speed = 1.0
        
        # Common colors
        shield_base = "#0a0a1a"
        shield_inner = "#151528"
        hologram_blue = "#00d4ff"
        hologram_purple = "#a855f7"
        grid_color = "rgba(100, 200, 255, 0.15)"
        
    colors = ShieldColors()
    
    # Animation calculations
    pulse = (math.sin(animation_frame * math.pi * 2 * colors.pulse_speed) + 1) / 2
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. OUTER ENERGY FIELD (Protective Barrier Visualization)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Dynamic ring count based on threat level
    ring_count = int(4 + threat_level * 8)
    
    for i in range(ring_count, 0, -1):
        ring_scale = 1.0 + i * 0.15
        ring_phase = (animation_frame + i * 0.1) % 1.0
        
        # Pulsing opacity
        base_opacity = colors.energy_intensity * (ring_count - i + 1) / ring_count
        pulse_opacity = base_opacity * (0.7 + 0.3 * math.sin(ring_phase * math.pi * 2))
        
        ring_w = w * ring_scale
        ring_h = h * ring_scale * 0.9
        
        # Outer energy hexagon
        hex_path = _create_hexagon_path(cx, cy, ring_w / 2)
        fig.add_shape(
            type="path",
            path=hex_path,
            fillcolor=_hex_to_rgba(colors.primary, pulse_opacity * 0.15),
            line=dict(
                color=_hex_to_rgba(colors.glow, pulse_opacity * 0.8),
                width=1.5 - i * 0.1,
                dash="dot" if i % 2 == 0 else "solid"
            ),
            layer="below"
        )
        
        # Energy particles on rings
        if i <= 3:
            particle_count = 6
            for p in range(particle_count):
                angle = (p / particle_count + ring_phase) * math.pi * 2
                px = cx + (ring_w / 2) * math.cos(angle)
                py = cy + (ring_w / 2 * 0.8) * math.sin(angle)
                particle_size = 3 + (3 - i) * 1.5
                
                fig.add_trace(go.Scatter(
                    x=[px], y=[py],
                    mode="markers",
                    marker=dict(
                        size=particle_size,
                        color=colors.glow,
                        opacity=pulse_opacity * 0.8
                    ),
                    hoverinfo="skip", showlegend=False
                ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. HOLOGRAPHIC PROJECTION BASE
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Projection platform (circular base)
    platform_radius = w * 0.7
    platform_y = cy - h * 0.55
    
    # Platform ellipse (perspective)
    platform_points = 40
    platform_xs = []
    platform_ys = []
    for i in range(platform_points + 1):
        angle = (i / platform_points) * math.pi * 2
        platform_xs.append(cx + platform_radius * math.cos(angle))
        platform_ys.append(platform_y + platform_radius * 0.25 * math.sin(angle))
    
    # Platform glow
    for g in range(5):
        glow_alpha = 0.15 - g * 0.03
        glow_expand = g * 0.008
        fig.add_trace(go.Scatter(
            x=[x + glow_expand * (x - cx) / platform_radius for x in platform_xs],
            y=[y - glow_expand for y in platform_ys],
            mode="lines",
            fill="toself",
            fillcolor=f"rgba(0, 200, 255, {glow_alpha})",
            line=dict(width=0),
            hoverinfo="skip", showlegend=False
        ))
    
    # Platform surface
    fig.add_trace(go.Scatter(
        x=platform_xs, y=platform_ys,
        mode="lines",
        fill="toself",
        fillcolor="rgba(10, 20, 40, 0.8)",
        line=dict(color=colors.hologram_blue, width=2),
        hoverinfo="skip", showlegend=False
    ))
    
    # Platform grid pattern
    grid_lines = 8
    for i in range(grid_lines):
        ratio = (i + 1) / (grid_lines + 1)
        # Radial lines
        angle = ratio * math.pi * 2
        gx1 = cx
        gy1 = platform_y
        gx2 = cx + platform_radius * 0.9 * math.cos(angle)
        gy2 = platform_y + platform_radius * 0.22 * math.sin(angle)
        fig.add_trace(go.Scatter(
            x=[gx1, gx2], y=[gy1, gy2],
            mode="lines",
            line=dict(color=colors.grid_color, width=1),
            hoverinfo="skip", showlegend=False
        ))
    
    # Concentric circles on platform
    for r in range(3):
        r_ratio = (r + 1) / 4
        circle_xs = []
        circle_ys = []
        for i in range(platform_points + 1):
            angle = (i / platform_points) * math.pi * 2
            circle_xs.append(cx + platform_radius * r_ratio * math.cos(angle))
            circle_ys.append(platform_y + platform_radius * 0.25 * r_ratio * math.sin(angle))
        fig.add_trace(go.Scatter(
            x=circle_xs, y=circle_ys,
            mode="lines",
            line=dict(color=colors.grid_color, width=1),
            hoverinfo="skip", showlegend=False
        ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. MAIN SHIELD BODY (3D Holographic Effect)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Shield drop shadow (grounded feel)
    shadow_offset = 0.012
    fig.add_shape(
        type="path",
        path=_create_shield_path_advanced(cx + shadow_offset, cy - shadow_offset, w, h),
        fillcolor="rgba(0, 0, 0, 0.4)",
        line=dict(width=0),
        layer="below"
    )
    
    # Shield outer glow (multiple layers)
    glow_layers = 6
    for g in range(glow_layers, 0, -1):
        glow_scale = 1.0 + g * 0.025
        glow_alpha = colors.energy_intensity * 0.15 * (glow_layers - g + 1) / glow_layers
        glow_alpha *= (0.7 + 0.3 * pulse)
        
        fig.add_shape(
            type="path",
            path=_create_shield_path_advanced(cx, cy, w * glow_scale, h * glow_scale),
            fillcolor=_hex_to_rgba(colors.glow, glow_alpha),
            line=dict(width=0),
            layer="below"
        )
    
    # Main shield body (dark metallic base)
    fig.add_shape(
        type="path",
        path=_create_shield_path_advanced(cx, cy, w, h),
        fillcolor=colors.shield_base,
        line=dict(color=colors.primary, width=3)
    )
    
    # Shield inner bevel (3D depth)
    bevel_inset = 0.92
    fig.add_shape(
        type="path",
        path=_create_shield_path_advanced(cx, cy + 0.003, w * bevel_inset, h * bevel_inset),
        fillcolor=colors.shield_inner,
        line=dict(color=_hex_to_rgba(colors.primary, 0.5), width=1.5)
    )
    
    # Shield highlight edge (top-left rim light)
    highlight_path = _create_shield_highlight_path(cx, cy, w, h)
    fig.add_shape(
        type="path",
        path=highlight_path,
        fillcolor="rgba(255, 255, 255, 0.1)",
        line=dict(width=0)
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. SHIELD INTERNAL STRUCTURE (Tech Details)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Internal hexagonal grid pattern
    hex_grid_size = 0.018
    hex_rows = 5
    hex_cols = 4
    
    grid_start_x = cx - (hex_cols - 1) * hex_grid_size * 0.9
    grid_start_y = cy - 0.02
    
    for row in range(hex_rows):
        row_offset = (row % 2) * hex_grid_size * 0.5
        for col in range(hex_cols):
            hx = grid_start_x + col * hex_grid_size * 1.8 + row_offset
            hy = grid_start_y + row * hex_grid_size * 0.8
            
            # Check if hex is within shield bounds (simplified)
            dist_from_center = math.sqrt((hx - cx)**2 + ((hy - cy) * 1.5)**2)
            if dist_from_center > w * 0.35:
                continue
            
            # Hex cell
            hex_path = _create_hexagon_path(hx, hy, hex_grid_size * 0.4)
            
            # Cell activity based on barrier value
            cell_activity = barrier_normalized * (0.5 + 0.5 * math.sin((row + col) * 0.5 + animation_frame * math.pi * 4))
            cell_alpha = 0.1 + cell_activity * 0.3
            
            fig.add_shape(
                type="path",
                path=hex_path,
                fillcolor=_hex_to_rgba(colors.primary, cell_alpha * 0.5),
                line=dict(color=_hex_to_rgba(colors.accent, cell_alpha), width=0.5)
            )
    
    # Circuit trace lines
    circuit_traces = [
        [(cx - 0.04, cy + 0.02), (cx - 0.02, cy + 0.02), (cx - 0.02, cy - 0.01), (cx, cy - 0.01)],
        [(cx + 0.04, cy + 0.02), (cx + 0.02, cy + 0.02), (cx + 0.02, cy + 0.01), (cx, cy + 0.01)],
        [(cx - 0.03, cy - 0.03), (cx, cy - 0.03), (cx, cy - 0.05)],
    ]
    
    for trace in circuit_traces:
        xs = [p[0] for p in trace]
        ys = [p[1] for p in trace]
        
        # Trace glow
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(color=colors.glow, width=3),
            opacity=0.2 * colors.energy_intensity,
            hoverinfo="skip", showlegend=False
        ))
        
        # Trace core
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(color=colors.primary, width=1),
            opacity=0.6,
            hoverinfo="skip", showlegend=False
        ))
        
        # Moving energy pulse on trace
        if cbf_active or not is_safe:
            pulse_pos = animation_frame
            if len(trace) >= 2:
                idx = int(pulse_pos * (len(trace) - 1))
                idx = min(idx, len(trace) - 2)
                t = (pulse_pos * (len(trace) - 1)) % 1
                
                pulse_x = trace[idx][0] + t * (trace[idx + 1][0] - trace[idx][0])
                pulse_y = trace[idx][1] + t * (trace[idx + 1][1] - trace[idx][1])
                
                fig.add_trace(go.Scatter(
                    x=[pulse_x], y=[pulse_y],
                    mode="markers",
                    marker=dict(size=6, color=colors.energy),
                    hoverinfo="skip", showlegend=False
                ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. CENTRAL CORE (U-CBF Processor)
    # ═══════════════════════════════════════════════════════════════════════════
    
    core_cx = cx
    core_cy = cy + 0.015
    core_size = 0.055
    
    # Core outer ring (spinning effect)
    ring_segments = 12
    for seg in range(ring_segments):
        seg_angle_start = (seg / ring_segments + animation_frame * 0.5) * math.pi * 2
        seg_angle_end = ((seg + 0.7) / ring_segments + animation_frame * 0.5) * math.pi * 2
        
        # Only draw every other segment for dashed effect
        if seg % 2 == 0:
            arc_points = 8
            arc_xs = []
            arc_ys = []
            for i in range(arc_points + 1):
                angle = seg_angle_start + (seg_angle_end - seg_angle_start) * (i / arc_points)
                arc_xs.append(core_cx + core_size * math.cos(angle))
                arc_ys.append(core_cy + core_size * 0.9 * math.sin(angle))
            
            fig.add_trace(go.Scatter(
                x=arc_xs, y=arc_ys,
                mode="lines",
                line=dict(color=colors.primary, width=2.5),
                hoverinfo="skip", showlegend=False
            ))
    
    # Core hexagon (main processor)
    core_hex = _create_hexagon_path(core_cx, core_cy, core_size * 0.65)
    
    # Core glow
    for g in range(4):
        glow_alpha = 0.25 - g * 0.05
        glow_size = core_size * (0.65 + g * 0.08)
        fig.add_shape(
            type="path",
            path=_create_hexagon_path(core_cx, core_cy, glow_size),
            fillcolor=_hex_to_rgba(colors.glow, glow_alpha * (0.6 + 0.4 * pulse)),
            line=dict(width=0)
        )
    
    # Core body
    fig.add_shape(
        type="path",
        path=core_hex,
        fillcolor=_hex_to_rgba(colors.primary, 0.4),
        line=dict(color=colors.glow, width=2)
    )
    
    # Core inner detail
    inner_hex = _create_hexagon_path(core_cx, core_cy, core_size * 0.4)
    fig.add_shape(
        type="path",
        path=inner_hex,
        fillcolor=colors.shield_base,
        line=dict(color=colors.primary, width=1)
    )
    
    # U-CBF Text with glow
    fig.add_annotation(
        x=core_cx, y=core_cy + 0.002,
        text="<b>U-CBF</b>", showarrow=False,
        font=dict(family="Arial Black", size=13, color=colors.glow),
        opacity=0.3
    )
    fig.add_annotation(
        x=core_cx, y=core_cy,
        text="<b>U-CBF</b>", showarrow=False,
        font=dict(family="Arial Black", size=13, color=colors.primary)
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 6. BARRIER VALUE VISUALIZATION (Arc Gauge)
    # ═══════════════════════════════════════════════════════════════════════════
    
    gauge_cx = cx
    gauge_cy = cy - 0.045
    gauge_radius = 0.05
    gauge_thickness = 0.008
    
    # Gauge background arc
    _draw_arc_segment(fig, gauge_cx, gauge_cy, gauge_radius, 
                      math.pi * 0.15, math.pi * 0.85,
                      "rgba(50, 50, 70, 0.5)", 6)
    
    # Gauge scale markings
    for i in range(11):
        mark_angle = math.pi * 0.15 + (math.pi * 0.7) * (i / 10)
        mark_inner = gauge_radius - 0.005
        mark_outer = gauge_radius + 0.005 if i % 5 == 0 else gauge_radius + 0.002
        
        mx1 = gauge_cx + mark_inner * math.cos(mark_angle)
        my1 = gauge_cy + mark_inner * math.sin(mark_angle)
        mx2 = gauge_cx + mark_outer * math.cos(mark_angle)
        my2 = gauge_cy + mark_outer * math.sin(mark_angle)
        
        fig.add_trace(go.Scatter(
            x=[mx1, mx2], y=[my1, my2],
            mode="lines",
            line=dict(color="rgba(255,255,255,0.3)", width=1),
            hoverinfo="skip", showlegend=False
        ))
    
    # Gauge fill based on barrier value
    fill_progress = barrier_normalized
    fill_angle_start = math.pi * 0.15
    fill_angle_end = fill_angle_start + (math.pi * 0.7) * fill_progress
    
    # Determine fill color based on barrier value
    if barrier_value < 0:
        gauge_color = PALETTE.DANGER_RED
    elif barrier_value < 0.5:
        gauge_color = PALETTE.WARNING_AMBER
    else:
        gauge_color = PALETTE.MATRIX_GREEN
    
    # Gauge fill glow
    _draw_arc_segment(fig, gauge_cx, gauge_cy, gauge_radius,
                      fill_angle_start, fill_angle_end,
                      _hex_to_rgba(gauge_color, 0.3), 10)
    
    # Gauge fill
    _draw_arc_segment(fig, gauge_cx, gauge_cy, gauge_radius,
                      fill_angle_start, fill_angle_end,
                      gauge_color, 5)
    
    # Gauge pointer
    pointer_angle = fill_angle_end
    pointer_len = gauge_radius + 0.012
    pointer_x = gauge_cx + pointer_len * math.cos(pointer_angle)
    pointer_y = gauge_cy + pointer_len * math.sin(pointer_angle)
    
    fig.add_trace(go.Scatter(
        x=[gauge_cx, pointer_x], y=[gauge_cy, pointer_y],
        mode="lines",
        line=dict(color=gauge_color, width=2),
        hoverinfo="skip", showlegend=False
    ))
    
    # Pointer tip
    fig.add_trace(go.Scatter(
        x=[pointer_x], y=[pointer_y],
        mode="markers",
        marker=dict(size=6, color=gauge_color, 
                   line=dict(color="white", width=1)),
        hoverinfo="skip", showlegend=False
    ))
    
    # Barrier value display (ENLARGED for thesis defense visibility)
    fig.add_annotation(
        x=gauge_cx, y=gauge_cy - 0.018,
        text=f"<b>h(x)</b>", showarrow=False,
        font=dict(size=10, color="rgba(255,255,255,0.6)")  # Was 7pt
    )
    fig.add_annotation(
        x=gauge_cx, y=gauge_cy - 0.035,
        text=f"<b>{barrier_value:.3f}</b>", showarrow=False,
        font=dict(family="Courier New", size=14, color=gauge_color)  # Was 10pt
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 7. STATUS INDICATOR PANEL
    # ═══════════════════════════════════════════════════════════════════════════
    
    status_y = cy - 0.09

    # Status background (WIDENED for readability)
    fig.add_shape(
        type="rect",
        x0=cx - 0.055, y0=status_y - 0.018,  # Wider and taller
        x1=cx + 0.055, y1=status_y + 0.015,
        fillcolor="rgba(0, 0, 0, 0.6)",
        line=dict(color=colors.primary, width=1)
    )

    # Status text with icon (ENLARGED for thesis defense)
    fig.add_annotation(
        x=cx, y=status_y,
        text=f"<b>{colors.status_text}</b>", showarrow=False,
        font=dict(family=THEME.font_family, size=13, color=colors.primary)  # Was 11pt
    )
    
    # Status indicator LED
    led_x = cx - 0.035
    led_y = status_y
    
    # LED glow
    if not is_safe or cbf_active:
        for g in range(3):
            fig.add_trace(go.Scatter(
                x=[led_x], y=[led_y],
                mode="markers",
                marker=dict(size=12 + g * 5, color=colors.primary, 
                           opacity=0.3 - g * 0.1),
                hoverinfo="skip", showlegend=False
            ))
    
    # LED body
    fig.add_trace(go.Scatter(
        x=[led_x], y=[led_y],
        mode="markers",
        marker=dict(size=6, color=colors.primary,
                   line=dict(color="white", width=0.5)),
        hoverinfo="skip", showlegend=False
    ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 8. SAFETY/VIOLATION INDICATOR
    # ═══════════════════════════════════════════════════════════════════════════
    
    indicator_y = cy - 0.12
    indicator_size = 0.018
    
    if is_safe:
        # Checkmark for safe state
        check_points = [
            (cx - indicator_size * 0.6, indicator_y),
            (cx - indicator_size * 0.1, indicator_y - indicator_size * 0.5),
            (cx + indicator_size * 0.8, indicator_y + indicator_size * 0.6)
        ]
        
        # Checkmark glow
        fig.add_trace(go.Scatter(
            x=[p[0] for p in check_points],
            y=[p[1] for p in check_points],
            mode="lines",
            line=dict(color=PALETTE.MATRIX_GREEN, width=6),
            opacity=0.3,
            hoverinfo="skip", showlegend=False
        ))
        
        # Checkmark
        fig.add_trace(go.Scatter(
            x=[p[0] for p in check_points],
            y=[p[1] for p in check_points],
            mode="lines",
            line=dict(color=PALETTE.MATRIX_GREEN, width=3),
            hoverinfo="skip", showlegend=False
        ))
    else:
        # X mark for violation
        x_lines = [
            [(cx - indicator_size, indicator_y - indicator_size),
             (cx + indicator_size, indicator_y + indicator_size)],
            [(cx - indicator_size, indicator_y + indicator_size),
             (cx + indicator_size, indicator_y - indicator_size)]
        ]
        
        for line in x_lines:
            # X glow
            fig.add_trace(go.Scatter(
                x=[line[0][0], line[1][0]],
                y=[line[0][1], line[1][1]],
                mode="lines",
                line=dict(color=PALETTE.DANGER_RED, width=6),
                opacity=0.4 * (0.5 + 0.5 * pulse),
                hoverinfo="skip", showlegend=False
            ))
            
            # X mark
            fig.add_trace(go.Scatter(
                x=[line[0][0], line[1][0]],
                y=[line[0][1], line[1][1]],
                mode="lines",
                line=dict(color=PALETTE.DANGER_RED, width=3),
                hoverinfo="skip", showlegend=False
            ))
        
        # Warning triangle (for critical state)
        triangle_size = 0.012
        triangle_y = indicator_y + 0.025
        
        fig.add_shape(
            type="path",
            path=f"M {cx},{triangle_y + triangle_size} "
                 f"L {cx - triangle_size},{triangle_y - triangle_size * 0.5} "
                 f"L {cx + triangle_size},{triangle_y - triangle_size * 0.5} Z",
            fillcolor=PALETTE.DANGER_RED,
            line=dict(color="#ffffff", width=1)
        )
        
        # Exclamation mark
        fig.add_annotation(
            x=cx, y=triangle_y - 0.002,
            text="<b>!</b>", showarrow=False,
            font=dict(size=8, color="white")
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 9. METRICS DISPLAY PANELS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Left metrics panel
    panel_w = 0.04
    panel_h = 0.06
    left_panel_x = cx - w/2 - 0.02
    panel_y = cy
    
    # Panel background
    fig.add_shape(
        type="rect",
        x0=left_panel_x - panel_w/2, y0=panel_y - panel_h/2,
        x1=left_panel_x + panel_w/2, y1=panel_y + panel_h/2,
        fillcolor="rgba(10, 15, 30, 0.9)",
        line=dict(color=colors.hologram_blue, width=1)
    )
    
    # Panel header
    fig.add_shape(
        type="rect",
        x0=left_panel_x - panel_w/2, y0=panel_y + panel_h/2 - 0.012,
        x1=left_panel_x + panel_w/2, y1=panel_y + panel_h/2,
        fillcolor=_hex_to_rgba(colors.hologram_blue, 0.3),
        line=dict(width=0)
    )
    
    fig.add_annotation(
        x=left_panel_x, y=panel_y + panel_h/2 - 0.006,
        text="<b>σ CAL</b>", showarrow=False,
        font=dict(size=6, color=colors.hologram_blue)
    )
    
    fig.add_annotation(
        x=left_panel_x, y=panel_y,
        text=f"<b>{sigma_calibrated:.4f}</b>", showarrow=False,
        font=dict(family="Courier New", size=8, color=colors.accent)
    )
    
    fig.add_annotation(
        x=left_panel_x, y=panel_y - 0.018,
        text=f"ΔV: {safety_margin:.2f}", showarrow=False,
        font=dict(size=6, color="rgba(255,255,255,0.5)")
    )
    
    # Right metrics panel
    right_panel_x = cx + w/2 + 0.02
    
    fig.add_shape(
        type="rect",
        x0=right_panel_x - panel_w/2, y0=panel_y - panel_h/2,
        x1=right_panel_x + panel_w/2, y1=panel_y + panel_h/2,
        fillcolor="rgba(10, 15, 30, 0.9)",
        line=dict(color=colors.hologram_purple, width=1)
    )
    
    fig.add_shape(
        type="rect",
        x0=right_panel_x - panel_w/2, y0=panel_y + panel_h/2 - 0.012,
        x1=right_panel_x + panel_w/2, y1=panel_y + panel_h/2,
        fillcolor=_hex_to_rgba(colors.hologram_purple, 0.3),
        line=dict(width=0)
    )
    
    fig.add_annotation(
        x=right_panel_x, y=panel_y + panel_h/2 - 0.006,
        text="<b>QP SOLVE</b>", showarrow=False,
        font=dict(size=6, color=colors.hologram_purple)
    )
    
    fig.add_annotation(
        x=right_panel_x, y=panel_y,
        text=f"<b>{qp_solve_time*1000:.2f}</b>", showarrow=False,
        font=dict(family="Courier New", size=8, color="#d8b4fe")
    )
    
    fig.add_annotation(
        x=right_panel_x, y=panel_y - 0.018,
        text="ms", showarrow=False,
        font=dict(size=6, color="rgba(255,255,255,0.5)")
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 10. INTERVENTION STRENGTH METER
    # ═══════════════════════════════════════════════════════════════════════════
    
    if cbf_active or not is_safe:
        meter_x = cx
        meter_y = cy + h/2 - 0.02
        meter_w = w * 0.6
        meter_h = 0.008
        
        # Meter background
        fig.add_shape(
            type="rect",
            x0=meter_x - meter_w/2, y0=meter_y - meter_h/2,
            x1=meter_x + meter_w/2, y1=meter_y + meter_h/2,
            fillcolor="rgba(30, 30, 50, 0.8)",
            line=dict(color="rgba(100,100,120,0.5)", width=1)
        )
        
        # Meter fill
        fill_ratio = min(1.0, intervention_strength)
        
        # Gradient segments
        segments = 20
        for s in range(int(segments * fill_ratio)):
            seg_x0 = meter_x - meter_w/2 + (meter_w / segments) * s
            seg_x1 = seg_x0 + (meter_w / segments) * 0.8
            
            # Color gradient from green to red
            seg_ratio = s / segments
            if seg_ratio < 0.5:
                seg_color = PALETTE.MATRIX_GREEN
            elif seg_ratio < 0.75:
                seg_color = PALETTE.WARNING_AMBER
            else:
                seg_color = PALETTE.DANGER_RED
            
            fig.add_shape(
                type="rect",
                x0=seg_x0 + 0.001, y0=meter_y - meter_h/2 + 0.001,
                x1=seg_x1, y1=meter_y + meter_h/2 - 0.001,
                fillcolor=seg_color,
                line=dict(width=0)
            )
        
        # Meter label
        fig.add_annotation(
            x=meter_x, y=meter_y + 0.012,
            text=f"<b>INTERVENTION: {intervention_strength*100:.0f}%</b>",
            showarrow=False,
            font=dict(size=6, color=colors.primary)
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 11. HOLOGRAPHIC PROJECTION RAYS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Projection rays from platform to shield
    ray_count = 8
    for r in range(ray_count):
        angle = (r / ray_count + animation_frame * 0.3) * math.pi * 2
        
        ray_base_x = cx + platform_radius * 0.6 * math.cos(angle)
        ray_base_y = platform_y + platform_radius * 0.15 * math.sin(angle)
        
        # Ray target on shield
        ray_target_y = cy - h * 0.1
        ray_target_x = cx + w * 0.2 * math.cos(angle)
        
        # Ray with gradient opacity
        ray_alpha = 0.15 * colors.energy_intensity
        
        fig.add_trace(go.Scatter(
            x=[ray_base_x, ray_target_x],
            y=[ray_base_y, ray_target_y],
            mode="lines",
            line=dict(color=colors.hologram_blue, width=1),
            opacity=ray_alpha,
            hoverinfo="skip", showlegend=False
        ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 12. THREAT VISUALIZATION (If threats provided)
    # ═══════════════════════════════════════════════════════════════════════════
    
    if threat_sources:
        for tx, ty, t_intensity in threat_sources:
            # Threat indicator
            for g in range(3):
                threat_alpha = 0.4 * t_intensity * (1 - g * 0.3)
                threat_size = 15 + g * 10
                
                fig.add_trace(go.Scatter(
                    x=[tx], y=[ty],
                    mode="markers",
                    marker=dict(
                        size=threat_size,
                        color=PALETTE.DANGER_RED,
                        opacity=threat_alpha,
                        symbol="x"
                    ),
                    hoverinfo="skip", showlegend=False
                ))
            
            # Threat connection to shield
            fig.add_trace(go.Scatter(
                x=[tx, cx], y=[ty, cy],
                mode="lines",
                line=dict(color=PALETTE.DANGER_RED, width=1, dash="dot"),
                opacity=0.3 * t_intensity,
                hoverinfo="skip", showlegend=False
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 13. INTERACTIVE HOVER & LABELS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Invisible hover target
    fig.add_trace(go.Scatter(
        x=[cx], y=[cy],
        mode="markers",
        marker=dict(size=90, color="rgba(0,0,0,0)"),
        hovertemplate=(
            f"<b style='color:{colors.primary}; font-size: 16px'>🛡️ U-CBF SAFETY FILTER</b><br>"
            "<span style='color:#555'>━━━━━━━━━━━━━━━━━━━━━━━━</span><br><br>"
            f"<b>📊 Barrier Function h(x):</b>  <span style='color:{gauge_color}'><b>{barrier_value:.4f}</b></span><br>"
            f"<b>📏 Safety Margin:</b>  <span style='color:#64B5F6'>{safety_margin:.2f} V</span><br>"
            f"<b>🎯 σ Calibrated:</b>  <span style='color:#a78bfa'>{sigma_calibrated:.4f}</span><br><br>"
            f"<b>⚡ Intervention:</b>  <span style='color:{colors.primary}'>"
            f"{'ACTIVE' if cbf_active else 'STANDBY'}</span><br>"
            f"<b>🔒 Constraint:</b>  <span style='color:{'#22c55e' if is_safe else '#ef4444'}'>"
            f"{'SATISFIED ✓' if is_safe else 'VIOLATED ✗'}</span><br><br>"
            f"<b>⏱️ QP Solve Time:</b>  <span style='color:#d8b4fe'>{qp_solve_time*1000:.3f} ms</span><br>"
            f"<b>💪 Intervention Strength:</b>  <span style='color:#fbbf24'>{intervention_strength*100:.1f}%</span><br>"
            f"<b>🔧 Algorithm:</b>  QP-based Unified CBF<br>"
            "<extra></extra>"
        ),
        showlegend=False
    ))
    
    # Main title - shortened to prevent truncation
    fig.add_annotation(
        x=cx, y=cy + h/2 + 0.055,
        text="<b>🛡️ U-CBF</b>", showarrow=False,
        font=dict(family=THEME.font_family, size=THEME.label_size,  # Slightly smaller
                 color=colors.primary),
        bgcolor="rgba(0,0,0,0.7)", borderpad=4,
        bordercolor=colors.primary, borderwidth=2
    )
    
    if show_details:
        # ═══ DETAILED METRICS DISPLAY (EXPANDED for thesis defense) ═══
        detail_y = cy - h/2 - 0.055  # Slightly lower for spacing

        # Background for details (WIDER and TALLER for 3-line display)
        fig.add_shape(
            type="rect",
            x0=cx - 0.085, y0=detail_y - 0.035,  # Much wider: 0.17 vs 0.14
            x1=cx + 0.085, y1=detail_y + 0.015,  # Taller for 3 lines
            fillcolor="rgba(0,0,0,0.7)",
            line=dict(color="rgba(100,100,120,0.4)", width=1)
        )

        # Split metrics into 3 separate lines for readability
        # Line 1: Barrier value (most important)
        fig.add_annotation(
            x=cx, y=detail_y + 0.005,
            text=f"<b>h(x) = {barrier_value:.3f}</b>",
            showarrow=False,
            font=dict(family=THEME.font_mono, size=11, color=PALETTE.MATRIX_GREEN)  # Was 8pt
        )
        # Line 2: Safety margin
        fig.add_annotation(
            x=cx, y=detail_y - 0.012,
            text=f"<b>Δ = {safety_margin:.1f}V</b>",
            showarrow=False,
            font=dict(family=THEME.font_mono, size=10, color=PALETTE.NEON_CYAN)
        )
        # Line 3: Sigma calibrated
        fig.add_annotation(
            x=cx, y=detail_y - 0.027,
            text=f"<b>σ = {sigma_calibrated:.3f}</b>",
            showarrow=False,
            font=dict(family=THEME.font_mono, size=10, color="#a78bfa")  # Purple for uncertainty
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _create_shield_path_advanced(cx: float, cy: float, w: float, h: float) -> str:
    """Create advanced SVG path for premium shield shape with better curves."""
    top_y = cy + h * 0.42
    shoulder_y = cy + h * 0.28
    mid_y = cy - h * 0.1
    bottom_y = cy - h * 0.5
    
    left_x = cx - w / 2
    right_x = cx + w / 2
    
    # More refined bezier curves for smoother shape
    return (
        f"M {cx},{bottom_y} "
        f"C {cx - w*0.25},{mid_y - h*0.05} {left_x + w*0.05},{shoulder_y - h*0.2} {left_x},{shoulder_y} "
        f"C {left_x},{shoulder_y + h*0.08} {left_x},{top_y - h*0.05} {cx - w*0.22},{top_y} "
        f"L {cx + w*0.22},{top_y} "
        f"C {right_x},{top_y - h*0.05} {right_x},{shoulder_y + h*0.08} {right_x},{shoulder_y} "
        f"C {right_x - w*0.05},{shoulder_y - h*0.2} {cx + w*0.25},{mid_y - h*0.05} {cx},{bottom_y} Z"
    )


def _create_shield_highlight_path(cx: float, cy: float, w: float, h: float) -> str:
    """Create highlight path for top-left rim lighting effect."""
    top_y = cy + h * 0.42
    shoulder_y = cy + h * 0.28
    left_x = cx - w / 2
    
    return (
        f"M {cx - w*0.22},{top_y} "
        f"C {left_x},{top_y - h*0.05} {left_x},{shoulder_y + h*0.08} {left_x},{shoulder_y} "
        f"L {left_x + w*0.05},{shoulder_y + h*0.02} "
        f"C {left_x + w*0.05},{shoulder_y + h*0.1} {left_x + w*0.05},{top_y - h*0.03} {cx - w*0.18},{top_y - h*0.02} "
        f"Z"
    )


def _create_hexagon_path(cx: float, cy: float, radius: float) -> str:
    """Create hexagon SVG path."""
    points = []
    for i in range(6):
        angle = i * math.pi / 3 - math.pi / 6
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append(f"{x},{y}")
    return f"M {points[0]} L {' L '.join(points[1:])} Z"


def _draw_arc_segment(
    fig: "go.Figure",
    cx: float,
    cy: float,
    radius: float,
    start_angle: float,
    end_angle: float,
    color: str,
    width: float,
) -> None:
    """Draw an arc segment."""
    n_points = 30
    xs, ys = [], []
    for i in range(n_points + 1):
        angle = start_angle + (end_angle - start_angle) * (i / n_points)
        xs.append(cx + radius * math.cos(angle))
        ys.append(cy + radius * math.sin(angle))
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines",
        line=dict(color=color, width=width),
        hoverinfo="skip", showlegend=False
    ))

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3D LOAD - PHOTOREALISTIC RENDERING (Ultra Enhanced Version)                 ║
# ║  Features: PBR Materials, Ambient Occlusion, Subsurface Scattering,         ║
# ║            Volumetric Lighting, Procedural Textures, Weather Effects         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_load_3d_ultra(fig: "go.Figure", values: Dict, show_values: bool, 
                          time_of_day: float = 0.5, weather: str = "clear") -> None:
    """
    Render ultra-realistic 3D residential load with advanced visual effects.
    
    Args:
        fig: Plotly figure object
        values: Dictionary containing load values
        show_values: Whether to display value annotations
        time_of_day: 0.0 (midnight) to 1.0 (next midnight), 0.5 = noon
        weather: "clear", "cloudy", "rainy", "night"
    """
    cx, cy = LAYOUT.LOAD
    w, h = LAYOUT.LOAD_W, LAYOUT.LOAD_H
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DYNAMIC STATE CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    p_load = values.get("p_load", 0.0)
    q_load = values.get("q_load", 0.0)  # Reactive power for additional realism
    load_ratio = min(1.0, max(0.0, p_load / 60.0))
    power_factor = values.get("pf", 0.95)
    
    # Time-based lighting calculations
    sun_angle = (time_of_day - 0.25) * 2 * 3.14159  # Peak at noon
    sun_intensity = max(0, math.sin(sun_angle)) if weather != "night" else 0
    is_night = time_of_day < 0.25 or time_of_day > 0.75 or weather == "night"
    
    # Weather modifiers
    weather_multipliers = {
        "clear": {"ambient": 1.0, "shadow": 1.0, "reflection": 0.8},
        "cloudy": {"ambient": 0.7, "shadow": 0.4, "reflection": 0.3},
        "rainy": {"ambient": 0.5, "shadow": 0.2, "reflection": 1.2},
        "night": {"ambient": 0.15, "shadow": 0.1, "reflection": 0.5}
    }
    wx = weather_multipliers.get(weather, weather_multipliers["clear"])

    # ═══════════════════════════════════════════════════════════════════════════
    # ARCHITECTURAL DIMENSIONS
    # ═══════════════════════════════════════════════════════════════════════════
    body_h = h * 0.62
    roof_h = h * 0.38
    foundation_h = h * 0.04
    body_bottom = cy - h / 2 + foundation_h
    body_top = body_bottom + body_h
    
    # 3D Isometric projection parameters
    depth_x = 0.018
    depth_y = -0.012
    depth_factor = 1.0
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADVANCED COLOR PALETTE (PBR-inspired)
    # ═══════════════════════════════════════════════════════════════════════════
    class MaterialColors:
        # Wall materials with weathering
        wall_base = "#3a3a55"
        wall_lit = _adjust_brightness("#3a3a55", 1.2 * sun_intensity + 0.3)
        wall_shadow = _adjust_brightness("#2a2a40", 0.7 * wx["shadow"])
        wall_ambient = "#1a1a30"
        
        # Roof materials (terracotta tiles)
        roof_lit = _adjust_brightness("#C96830", 1.1 * sun_intensity + 0.4)
        roof_mid = "#A85525"
        roof_shadow = "#7A3D18"
        roof_edge = "#5A2D10"
        
        # Trim and accents
        trim_primary = PALETTE.SOLAR_ORANGE
        trim_metallic = "#D4A574"
        
        # Foundation
        foundation = "#4a4a5a"
        foundation_dark = "#3a3a4a"
        
        # Glass materials
        glass_base = "#1a2030"
        glass_reflection = "rgba(180, 200, 255, 0.4)"
        glass_tint = "rgba(100, 150, 200, 0.2)"
        
        # Interior glow (load-dependent)
        interior_warm = f"rgba(255, {200 - int(load_ratio * 50)}, {120 - int(load_ratio * 40)}, {0.3 + load_ratio * 0.5})"
        interior_cool = "rgba(200, 220, 255, 0.2)"

    colors = MaterialColors()

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER FUNCTIONS FOR ADVANCED RENDERING
    # ═══════════════════════════════════════════════════════════════════════════
    def _add_gradient_rect(x0, y0, x1, y1, colors_list, direction="vertical", steps=8):
        """Simulate gradient fill with multiple overlapping rectangles."""
        for i in range(steps):
            ratio = i / steps
            if direction == "vertical":
                sy0 = y0 + (y1 - y0) * ratio
                sy1 = y0 + (y1 - y0) * (ratio + 1/steps)
                fig.add_shape(type="rect", x0=x0, y0=sy0, x1=x1, y1=sy1,
                    fillcolor=_interpolate_color(colors_list[0], colors_list[1], ratio),
                    line=dict(width=0), layer="below")
            else:
                sx0 = x0 + (x1 - x0) * ratio
                sx1 = x0 + (x1 - x0) * (ratio + 1/steps)
                fig.add_shape(type="rect", x0=sx0, y0=y0, x1=sx1, y1=y1,
                    fillcolor=_interpolate_color(colors_list[0], colors_list[1], ratio),
                    line=dict(width=0), layer="below")

    def _add_ambient_occlusion(x0, y0, x1, y1, corner="all", intensity=0.3):
        """Add ambient occlusion shadows to corners and edges."""
        ao_steps = 5
        ao_size = 0.008
        for i in range(ao_steps):
            alpha = intensity * (1 - i/ao_steps) * wx["shadow"]
            offset = ao_size * (i/ao_steps)
            if corner in ["all", "bottom"]:
                fig.add_shape(type="rect", 
                    x0=x0+offset, y0=y0, x1=x1-offset, y1=y0+offset,
                    fillcolor=f"rgba(0,0,0,{alpha})", line=dict(width=0))
            if corner in ["all", "left"]:
                fig.add_shape(type="rect",
                    x0=x0, y0=y0+offset, x1=x0+offset, y1=y1-offset,
                    fillcolor=f"rgba(0,0,0,{alpha*0.5})", line=dict(width=0))

    def _add_specular_highlight(x, y, w, h, angle=45, intensity=0.3):
        """Add specular highlight based on light direction."""
        if sun_intensity < 0.1:
            return
        hl_w = w * 0.3
        hl_h = h * 0.1
        offset_x = w * 0.1 * math.cos(math.radians(angle))
        offset_y = h * 0.3
        fig.add_shape(type="rect",
            x0=x - hl_w/2 + offset_x, y0=y + offset_y,
            x1=x + hl_w/2 + offset_x, y1=y + offset_y + hl_h,
            fillcolor=f"rgba(255,255,255,{intensity * sun_intensity})",
            line=dict(width=0))

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. ENVIRONMENTAL GROUND PLANE & SHADOWS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # --- Ground texture hint ---
    ground_y = body_bottom - foundation_h - 0.01
    for i in range(3):
        fig.add_shape(type="rect",
            x0=cx - w*0.8 - i*0.01, y0=ground_y - 0.005 - i*0.003,
            x1=cx + w*0.8 + depth_x + i*0.01, y1=ground_y + 0.002,
            fillcolor=f"rgba(40, 45, 35, {0.15 - i*0.04})",
            line=dict(width=0), layer="below")

    # --- Multi-layer soft shadow (Gaussian approximation) ---
    shadow_layers = 12
    shadow_offset_x = depth_x * 1.5 * (1 - sun_intensity * 0.5)
    shadow_offset_y = depth_y * 1.2
    
    for i in range(shadow_layers):
        alpha = (0.25 - i * 0.02) * wx["shadow"]
        expand = i * 0.004
        blur_offset = i * 0.002
        
        fig.add_shape(type="rect",
            x0=cx - w/2 - expand + shadow_offset_x + blur_offset,
            y0=ground_y - expand*0.5 + shadow_offset_y,
            x1=cx + w/2 + expand + shadow_offset_x + blur_offset + depth_x,
            y1=ground_y + 0.008 + shadow_offset_y,
            fillcolor=f"rgba(0, 0, 0, {alpha})",
            line=dict(width=0), layer="below")

    # --- Contact shadow (crisp edge where building meets ground) ---
    fig.add_shape(type="rect",
        x0=cx - w/2, y0=ground_y,
        x1=cx + w/2 + depth_x * 0.5, y1=ground_y + 0.006,
        fillcolor=f"rgba(0, 0, 0, {0.5 * wx['shadow']})",
        line=dict(width=0), layer="below")

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. FOUNDATION (Concrete with weathering)
    # ═══════════════════════════════════════════════════════════════════════════
    fnd_bottom = body_bottom - foundation_h
    
    # Foundation 3D side
    path_fnd_side = f"""M {cx+w/2},{fnd_bottom} 
                        L {cx+w/2+depth_x},{fnd_bottom+depth_y} 
                        L {cx+w/2+depth_x},{body_bottom+depth_y} 
                        L {cx+w/2},{body_bottom} Z"""
    fig.add_shape(type="path", path=path_fnd_side, 
        fillcolor=colors.foundation_dark, line=dict(width=0))
    
    # Foundation front face with subtle texture
    fig.add_shape(type="rect",
        x0=cx-w/2, y0=fnd_bottom, x1=cx+w/2, y1=body_bottom,
        fillcolor=colors.foundation, line=dict(color="#3a3a4a", width=1))
    
    # Concrete weathering lines
    for i in range(3):
        fy = fnd_bottom + foundation_h * (i + 1) / 4
        fig.add_shape(type="line",
            x0=cx-w/2, y0=fy, x1=cx+w/2, y1=fy,
            line=dict(color="rgba(0,0,0,0.15)", width=0.5))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. MAIN BUILDING BODY (Advanced Materials)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # --- Right Side Face (Shadowed) ---
    path_side = f"""M {cx+w/2},{body_bottom} 
                    L {cx+w/2+depth_x},{body_bottom+depth_y} 
                    L {cx+w/2+depth_x},{body_top+depth_y} 
                    L {cx+w/2},{body_top} Z"""
    fig.add_shape(type="path", path=path_side, 
        fillcolor=colors.wall_shadow, line=dict(color="#151525", width=1))
    
    # Side face vertical texture lines
    for i in range(4):
        ratio = (i + 1) / 5
        sx = cx + w/2 + depth_x * ratio
        sy_bottom = body_bottom + depth_y * ratio
        sy_top = body_top + depth_y * ratio
        fig.add_trace(go.Scatter(
            x=[sx, sx], y=[sy_bottom, sy_top],
            mode="lines", line=dict(color="rgba(0,0,0,0.1)", width=0.5),
            hoverinfo="skip", showlegend=False))

    # --- Front Face Base ---
    fig.add_shape(type="rect",
        x0=cx-w/2, y0=body_bottom, x1=cx+w/2, y1=body_top,
        fillcolor=colors.wall_base, line=dict(width=0))
    
    # --- Vertical Gradient Overlay (Atmospheric perspective) ---
    gradient_steps = 10
    for i in range(gradient_steps):
        ratio = i / gradient_steps
        gy0 = body_bottom + body_h * ratio
        gy1 = body_bottom + body_h * (ratio + 1/gradient_steps)
        # Lighter at top (sky reflection), darker at bottom (ground occlusion)
        brightness = 0.85 + ratio * 0.15
        fig.add_shape(type="rect",
            x0=cx-w/2, y0=gy0, x1=cx+w/2, y1=gy1,
            fillcolor=f"rgba(255,255,255,{(ratio * 0.08) * sun_intensity})",
            line=dict(width=0))

    # --- Horizontal Siding with Realistic Depth ---
    siding_count = 16
    siding_height = body_h / siding_count
    for i in range(siding_count):
        sy = body_bottom + siding_height * i
        
        # Main groove shadow
        fig.add_shape(type="line",
            x0=cx-w/2+0.001, y0=sy, x1=cx+w/2-0.001, y1=sy,
            line=dict(color=f"rgba(0,0,0,{0.25 * wx['shadow']})", width=1.5))
        
        # Highlight below groove (catch light)
        if i > 0:
            fig.add_shape(type="line",
                x0=cx-w/2+0.001, y0=sy+0.0015, x1=cx+w/2-0.001, y1=sy+0.0015,
                line=dict(color=f"rgba(255,255,255,{0.08 * sun_intensity})", width=0.5))
        
        # Subtle color variation per board (weathering)
        if i % 3 == 0:
            fig.add_shape(type="rect",
                x0=cx-w/2, y0=sy, x1=cx+w/2, y1=sy+siding_height,
                fillcolor="rgba(0,0,0,0.03)", line=dict(width=0))

    # --- Edge Highlights (Rim Lighting) ---
    # Left edge (lit by sun)
    rim_intensity = 0.35 * sun_intensity + 0.1
    fig.add_shape(type="line",
        x0=cx-w/2, y0=body_bottom, x1=cx-w/2, y1=body_top,
        line=dict(color=f"rgba(255,255,255,{rim_intensity})", width=2.5))
    
    # Top edge highlight
    fig.add_shape(type="line",
        x0=cx-w/2, y0=body_top, x1=cx+w/2, y1=body_top,
        line=dict(color=f"rgba(255,255,255,{rim_intensity * 0.5})", width=1))

    # --- Corner Ambient Occlusion ---
    _add_ambient_occlusion(cx-w/2, body_bottom, cx+w/2, body_top, "bottom", 0.2)

    # --- Accent Trim Border ---
    fig.add_shape(type="rect",
        x0=cx-w/2, y0=body_bottom, x1=cx+w/2, y1=body_top,
        fillcolor="rgba(0,0,0,0)", 
        line=dict(color=colors.trim_primary, width=2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. REALISTIC ROOF SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════
    roof_peak_y = body_top + roof_h
    roof_overhang = 0.008
    
    # --- Roof Side Face (Darkest) ---
    path_roof_side = f"""M {cx+w/2},{body_top} 
                         L {cx+w/2+depth_x},{body_top+depth_y} 
                         L {cx+depth_x},{roof_peak_y+depth_y} 
                         L {cx},{roof_peak_y} Z"""
    fig.add_shape(type="path", path=path_roof_side, 
        fillcolor=colors.roof_edge, line=dict(width=0))

    # --- Right Roof Slope (Shadow side) ---
    path_roof_right = f"""M {cx},{body_top} 
                          L {cx},{roof_peak_y} 
                          L {cx+w/2+roof_overhang},{body_top} Z"""
    fig.add_shape(type="path", path=path_roof_right, 
        fillcolor=colors.roof_shadow, line=dict(color=colors.roof_edge, width=1))
    
    # Shadow gradient on right slope
    fig.add_shape(type="path", path=path_roof_right,
        fillcolor="rgba(0,0,0,0.15)", line=dict(width=0))

    # --- Left Roof Slope (Lit side) ---
    path_roof_left = f"""M {cx-w/2-roof_overhang},{body_top} 
                         L {cx},{roof_peak_y} 
                         L {cx},{body_top} Z"""
    fig.add_shape(type="path", path=path_roof_left, 
        fillcolor=colors.roof_lit, line=dict(color=colors.roof_mid, width=1))
    
    # Highlight gradient on left slope
    for i in range(5):
        ratio = i / 5
        alpha = (0.15 - ratio * 0.03) * sun_intensity
        hy = body_top + roof_h * (1 - ratio)
        hx_left = cx - (w/2 + roof_overhang) * ratio
        fig.add_trace(go.Scatter(
            x=[hx_left, cx], y=[hy, hy],
            mode="lines", line=dict(color=f"rgba(255,255,255,{alpha})", width=2),
            hoverinfo="skip", showlegend=False))

    # --- Roof Tile Texture (Both slopes) ---
    tile_rows = 8
    for i in range(1, tile_rows):
        ratio = i / tile_rows
        tile_y = body_top + roof_h * ratio
        
        # Left slope tile lines
        left_x = cx - (w/2 + roof_overhang) * (1 - ratio)
        fig.add_trace(go.Scatter(
            x=[left_x, cx], y=[tile_y, tile_y],
            mode="lines", line=dict(color=f"rgba(0,0,0,{0.12 * wx['shadow']})", width=1),
            hoverinfo="skip", showlegend=False))
        
        # Right slope tile lines (darker)
        right_x = cx + (w/2 + roof_overhang) * (1 - ratio)
        fig.add_trace(go.Scatter(
            x=[cx, right_x], y=[tile_y, tile_y],
            mode="lines", line=dict(color=f"rgba(0,0,0,{0.2 * wx['shadow']})", width=1),
            hoverinfo="skip", showlegend=False))
        
        # Tile edge highlights (left slope only)
        if i < tile_rows - 1:
            fig.add_trace(go.Scatter(
                x=[left_x + 0.002, cx], y=[tile_y + 0.002, tile_y + 0.002],
                mode="lines", line=dict(color=f"rgba(255,200,150,{0.1 * sun_intensity})", width=0.5),
                hoverinfo="skip", showlegend=False))

    # --- Roof Ridge (Cap tiles) ---
    fig.add_trace(go.Scatter(
        x=[cx-w/2-roof_overhang, cx, cx+w/2+roof_overhang],
        y=[body_top, roof_peak_y, body_top],
        mode="lines", line=dict(color=colors.trim_primary, width=3),
        hoverinfo="skip", showlegend=False))
    
    # Ridge highlight
    fig.add_trace(go.Scatter(
        x=[cx-w/2-roof_overhang+0.002, cx],
        y=[body_top+0.003, roof_peak_y+0.002],
        mode="lines", line=dict(color=f"rgba(255,255,255,{0.4 * sun_intensity})", width=1.5),
        hoverinfo="skip", showlegend=False))

    # --- Roof Overhang Shadow on Wall ---
    fig.add_shape(type="rect",
        x0=cx-w/2, y0=body_top-0.008, x1=cx+w/2, y1=body_top,
        fillcolor=f"rgba(0,0,0,{0.25 * wx['shadow']})", line=dict(width=0))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. DETAILED CHIMNEY WITH SMOKE EFFECT
    # ═══════════════════════════════════════════════════════════════════════════
    ch_x = cx + w * 0.22
    ch_w = 0.022
    ch_h = 0.05
    # Calculate chimney base on roof slope
    ch_roof_ratio = 0.35
    ch_base_y = body_top + roof_h * ch_roof_ratio

    # Chimney 3D back face
    fig.add_shape(type="rect",
        x0=ch_x+ch_w, y0=ch_base_y,
        x1=ch_x+ch_w+depth_x*0.7, y1=ch_base_y+ch_h+depth_y*0.7,
        fillcolor="#252535", line=dict(width=0))
    
    # Chimney top face (3D)
    path_ch_top = f"""M {ch_x},{ch_base_y+ch_h} 
                      L {ch_x+depth_x*0.7},{ch_base_y+ch_h+depth_y*0.7}
                      L {ch_x+ch_w+depth_x*0.7},{ch_base_y+ch_h+depth_y*0.7}
                      L {ch_x+ch_w},{ch_base_y+ch_h} Z"""
    fig.add_shape(type="path", path=path_ch_top, 
        fillcolor="#555565", line=dict(width=0))

    # Chimney front face
    fig.add_shape(type="rect",
        x0=ch_x, y0=ch_base_y, x1=ch_x+ch_w, y1=ch_base_y+ch_h,
        fillcolor="#454555", line=dict(color="#353545", width=1))

    # Brick pattern
    brick_rows = 5
    brick_cols = 2
    for row in range(brick_rows):
        by = ch_base_y + (ch_h / brick_rows) * row
        offset = 0 if row % 2 == 0 else ch_w / (brick_cols * 2)
        
        # Horizontal mortar line
        fig.add_shape(type="line",
            x0=ch_x, y0=by, x1=ch_x+ch_w, y1=by,
            line=dict(color="rgba(80,80,90,0.5)", width=0.5))
        
        # Vertical mortar lines
        for col in range(brick_cols):
            bx = ch_x + offset + (ch_w / brick_cols) * col
            if ch_x < bx < ch_x + ch_w:
                fig.add_shape(type="line",
                    x0=bx, y0=by, x1=bx, y1=by + ch_h/brick_rows,
                    line=dict(color="rgba(80,80,90,0.4)", width=0.5))

    # Chimney cap (concrete)
    cap_overhang = 0.003
    fig.add_shape(type="rect",
        x0=ch_x-cap_overhang, y0=ch_base_y+ch_h,
        x1=ch_x+ch_w+cap_overhang+depth_x*0.7, y1=ch_base_y+ch_h+0.006,
        fillcolor="#606070", line=dict(color="#505060", width=0.5))
    
    # Chimney flue (dark hole)
    fig.add_shape(type="rect",
        x0=ch_x+0.004, y0=ch_base_y+ch_h+0.002,
        x1=ch_x+ch_w-0.002+depth_x*0.4, y1=ch_base_y+ch_h+0.005,
        fillcolor="#101015", line=dict(width=0))

    # --- Smoke Effect (Load-dependent, visible when heating is on) ---
    if load_ratio > 0.3 and not is_night:
        smoke_intensity = (load_ratio - 0.3) * 0.5
        smoke_particles = 6
        for i in range(smoke_particles):
            smoke_y = ch_base_y + ch_h + 0.01 + i * 0.008
            smoke_x = ch_x + ch_w/2 + math.sin(i * 1.2) * 0.005 + (i * 0.002)
            smoke_size = 4 + i * 1.5
            smoke_alpha = smoke_intensity * (1 - i/smoke_particles) * 0.4
            
            fig.add_trace(go.Scatter(
                x=[smoke_x], y=[smoke_y], mode="markers",
                marker=dict(
                    size=smoke_size,
                    color=f"rgba(200, 200, 210, {smoke_alpha})",
                    line=dict(width=0)
                ),
                hoverinfo="skip", showlegend=False))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. PHOTOREALISTIC WINDOWS
    # ═══════════════════════════════════════════════════════════════════════════
    win_w = 0.026
    win_h = 0.028
    win_gap_x = 0.018
    win_gap_y = 0.016
    win_start_x = cx - (win_w + win_gap_x) / 2
    win_start_y = body_bottom + 0.035
    
    # Calculate interior glow based on load and time
    if is_night:
        interior_glow_base = 0.6 + load_ratio * 0.3
    else:
        interior_glow_base = 0.1 + load_ratio * 0.2
    
    for row in range(2):
        for col in range(2):
            wx_pos = win_start_x + col * (win_w + win_gap_x)
            wy_pos = win_start_y + row * (win_h + win_gap_y)
            
            # --- Window Depth Shadow (Inset) ---
            inset_depth = 0.004
            fig.add_shape(type="rect",
                x0=wx_pos-inset_depth, y0=wy_pos-inset_depth,
                x1=wx_pos+win_w+inset_depth, y1=wy_pos+win_h+inset_depth,
                fillcolor=f"rgba(0,0,0,{0.4 * wx['shadow']})", line=dict(width=0))

            # --- Window Frame (Wood/PVC) ---
            frame_width = 0.003
            fig.add_shape(type="rect",
                x0=wx_pos-frame_width, y0=wy_pos-frame_width,
                x1=wx_pos+win_w+frame_width, y1=wy_pos+win_h+frame_width,
                fillcolor=colors.wall_base, line=dict(color=colors.trim_primary, width=1.5))
            
            # Frame inner shadow (top and right = light source opposite)
            fig.add_shape(type="rect",
                x0=wx_pos+win_w-0.002, y0=wy_pos,
                x1=wx_pos+win_w, y1=wy_pos+win_h,
                fillcolor="rgba(0,0,0,0.3)", line=dict(width=0))
            fig.add_shape(type="rect",
                x0=wx_pos, y0=wy_pos+win_h-0.002,
                x1=wx_pos+win_w, y1=wy_pos+win_h,
                fillcolor="rgba(0,0,0,0.25)", line=dict(width=0))

            # --- Glass Pane Layers ---
            glass_inset = 0.002
            gx0 = wx_pos + glass_inset
            gy0 = wy_pos + glass_inset
            gx1 = wx_pos + win_w - glass_inset
            gy1 = wy_pos + win_h - glass_inset
            
            # Base glass (dark with tint)
            fig.add_shape(type="rect",
                x0=gx0, y0=gy0, x1=gx1, y1=gy1,
                fillcolor=colors.glass_base, line=dict(width=0))
            
            # Interior glow (radial gradient simulation)
            glow_layers = 4
            for g in range(glow_layers):
                g_ratio = g / glow_layers
                g_inset = 0.003 + g * 0.002
                g_alpha = interior_glow_base * (1 - g_ratio * 0.6)
                
                # Vary color temperature based on load
                if load_ratio > 0.6:
                    glow_r, glow_g, glow_b = 255, 180, 100  # Warm (high load)
                elif load_ratio > 0.3:
                    glow_r, glow_g, glow_b = 255, 210, 150  # Medium warm
                else:
                    glow_r, glow_g, glow_b = 220, 220, 200  # Cool white
                
                fig.add_shape(type="rect",
                    x0=gx0+g_inset, y0=gy0+g_inset,
                    x1=gx1-g_inset, y1=gy1-g_inset,
                    fillcolor=f"rgba({glow_r},{glow_g},{glow_b},{g_alpha})",
                    line=dict(width=0))
            
            # --- Glass Reflections ---
            # Sky reflection (diagonal, top-left to bottom-right)
            ref_path = f"""M {gx0},{gy0+win_h*0.4}
                           L {gx0+win_w*0.35},{gy1}
                           L {gx0},{gy1} Z"""
            fig.add_shape(type="path", path=ref_path,
                fillcolor=f"rgba(180,200,255,{0.35 * sun_intensity * wx['reflection']})",
                line=dict(width=0))
            
            # Secondary reflection (smaller, sharper)
            ref2_path = f"""M {gx0+win_w*0.1},{gy0+win_h*0.2}
                            L {gx0+win_w*0.25},{gy0+win_h*0.5}
                            L {gx0+win_w*0.1},{gy0+win_h*0.5} Z"""
            fig.add_shape(type="path", path=ref2_path,
                fillcolor=f"rgba(255,255,255,{0.2 * sun_intensity})",
                line=dict(width=0))
            
            # --- Window Mullions (Cross bars) ---
            mullion_color = colors.trim_primary
            mullion_width = 1.5
            
            # Horizontal mullion
            fig.add_trace(go.Scatter(
                x=[gx0, gx1], y=[gy0+win_h/2, gy0+win_h/2],
                mode="lines", line=dict(color=mullion_color, width=mullion_width),
                hoverinfo="skip", showlegend=False))
            
            # Vertical mullion
            fig.add_trace(go.Scatter(
                x=[gx0+win_w/2, gx0+win_w/2], y=[gy0, gy1],
                mode="lines", line=dict(color=mullion_color, width=mullion_width),
                hoverinfo="skip", showlegend=False))
            
            # Mullion shadows
            fig.add_trace(go.Scatter(
                x=[gx0+win_w/2+0.001, gx0+win_w/2+0.001], y=[gy0, gy1],
                mode="lines", line=dict(color="rgba(0,0,0,0.3)", width=1),
                hoverinfo="skip", showlegend=False))

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. DETAILED FRONT DOOR
    # ═══════════════════════════════════════════════════════════════════════════
    door_w = 0.028
    door_h = 0.055
    door_x = cx - door_w / 2
    door_y = body_bottom

    # --- Door Frame (Recessed Entry) ---
    frame_depth = 0.005
    frame_w = 0.004
    
    # Entry recess shadow
    fig.add_shape(type="rect",
        x0=door_x-frame_w-frame_depth, y0=door_y,
        x1=door_x+door_w+frame_w+frame_depth, y1=door_y+door_h+frame_w,
        fillcolor=f"rgba(0,0,0,{0.4 * wx['shadow']})", line=dict(width=0))
    
    # Door frame
    fig.add_shape(type="rect",
        x0=door_x-frame_w, y0=door_y,
        x1=door_x+door_w+frame_w, y1=door_y+door_h+frame_w,
        fillcolor=colors.trim_primary, line=dict(color="#8B4513", width=1))

    # --- Door Panel Base ---
    fig.add_shape(type="rect",
        x0=door_x, y0=door_y, x1=door_x+door_w, y1=door_y+door_h,
        fillcolor="#6B4423", line=dict(width=0))

    # Wood grain texture
    grain_lines = 8
    for i in range(grain_lines):
        gx = door_x + door_w * (i + 0.5) / grain_lines
        # Slight curve for wood grain
        wave = math.sin(i * 0.8) * 0.001
        fig.add_trace(go.Scatter(
            x=[gx+wave, gx-wave, gx+wave],
            y=[door_y+0.002, door_y+door_h/2, door_y+door_h-0.002],
            mode="lines", line=dict(color="rgba(90,55,20,0.3)", width=0.5),
            hoverinfo="skip", showlegend=False))

    # --- Door Panels (Raised) ---
    panel_inset = 0.004
    panel_gap = 0.003
    panel_h = (door_h - panel_gap * 3) / 2
    
    for i in range(2):
        py = door_y + panel_gap + i * (panel_h + panel_gap)
        
        # Panel shadow (recessed look)
        fig.add_shape(type="rect",
            x0=door_x+panel_inset-0.001, y0=py-0.001,
            x1=door_x+door_w-panel_inset+0.001, y1=py+panel_h+0.001,
            fillcolor="rgba(0,0,0,0.3)", line=dict(width=0))
        
        # Raised panel
        fig.add_shape(type="rect",
            x0=door_x+panel_inset, y0=py,
            x1=door_x+door_w-panel_inset, y1=py+panel_h,
            fillcolor="#7B5433", line=dict(color="#5B3413", width=0.5))
        
        # Panel highlight (top-left edges)
        fig.add_shape(type="line",
            x0=door_x+panel_inset, y0=py+panel_h,
            x1=door_x+door_w-panel_inset, y1=py+panel_h,
            line=dict(color="rgba(255,255,255,0.15)", width=1))
        fig.add_shape(type="line",
            x0=door_x+panel_inset, y0=py,
            x1=door_x+panel_inset, y1=py+panel_h,
            line=dict(color="rgba(255,255,255,0.1)", width=1))

    # --- Door Hardware (Handle & Lock) ---
    hw_x = door_x + door_w - 0.008
    hw_y = door_y + door_h * 0.52
    
    # Handle plate (brushed metal)
    plate_w = 0.006
    plate_h = 0.018
    fig.add_shape(type="rect",
        x0=hw_x-plate_w/2, y0=hw_y-plate_h/2,
        x1=hw_x+plate_w/2, y1=hw_y+plate_h/2,
        fillcolor="#C0B090", line=dict(color="#A09070", width=0.5))
    
    # Handle lever
    fig.add_trace(go.Scatter(
        x=[hw_x-plate_w/2, hw_x+plate_w/2+0.003],
        y=[hw_y, hw_y],
        mode="lines", line=dict(color="#D4C4A4", width=3),
        hoverinfo="skip", showlegend=False))
    
    # Handle specular highlight
    fig.add_trace(go.Scatter(
        x=[hw_x], y=[hw_y+0.001],
        mode="markers", marker=dict(size=3, color="#FFFFFF"),
        hoverinfo="skip", showlegend=False))
    
    # Lock cylinder
    lock_y = hw_y - plate_h/2 + 0.003
    fig.add_trace(go.Scatter(
        x=[hw_x], y=[lock_y],
        mode="markers", marker=dict(size=4, color="#8B8B7B", 
            line=dict(color="#6B6B5B", width=1)),
        hoverinfo="skip", showlegend=False))
    
    # Keyhole
    fig.add_trace(go.Scatter(
        x=[hw_x], y=[lock_y],
        mode="markers", marker=dict(size=1.5, color="#2B2B2B"),
        hoverinfo="skip", showlegend=False))

    # --- Door Threshold ---
    fig.add_shape(type="rect",
        x0=door_x-frame_w, y0=door_y-0.003,
        x1=door_x+door_w+frame_w, y1=door_y,
        fillcolor="#4A4A4A", line=dict(color="#3A3A3A", width=0.5))

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. ADVANCED SMART ENERGY METER
    # ═══════════════════════════════════════════════════════════════════════════
    meter_x = cx + w/2 + 0.035
    meter_w = 0.028
    meter_h = h * 0.65
    meter_y = cy - meter_h/2
    meter_depth = 0.01

    # --- Meter Housing (Industrial Metal) ---
    # Back/Side face
    path_meter_side = f"""M {meter_x+meter_w},{meter_y}
                          L {meter_x+meter_w+meter_depth},{meter_y+depth_y}
                          L {meter_x+meter_w+meter_depth},{meter_y+meter_h+depth_y}
                          L {meter_x+meter_w},{meter_y+meter_h} Z"""
    fig.add_shape(type="path", path=path_meter_side,
        fillcolor="#1a1a25", line=dict(width=0))
    
    # Top face
    path_meter_top = f"""M {meter_x},{meter_y+meter_h}
                         L {meter_x+meter_depth},{meter_y+meter_h+depth_y}
                         L {meter_x+meter_w+meter_depth},{meter_y+meter_h+depth_y}
                         L {meter_x+meter_w},{meter_y+meter_h} Z"""
    fig.add_shape(type="path", path=path_meter_top,
        fillcolor="#3a3a45", line=dict(width=0))

    # Front bezel (metallic gradient)
    fig.add_shape(type="rect",
        x0=meter_x, y0=meter_y, x1=meter_x+meter_w, y1=meter_y+meter_h,
        fillcolor="#2a2a35", line=dict(color="#4a4a55", width=2))
    
    # Metallic edge highlights
    fig.add_shape(type="line",
        x0=meter_x, y0=meter_y, x1=meter_x, y1=meter_y+meter_h,
        line=dict(color="rgba(255,255,255,0.2)", width=1.5))
    fig.add_shape(type="line",
        x0=meter_x, y0=meter_y+meter_h, x1=meter_x+meter_w, y1=meter_y+meter_h,
        line=dict(color="rgba(255,255,255,0.15)", width=1))

    # Manufacturer logo area
    fig.add_shape(type="rect",
        x0=meter_x+0.003, y0=meter_y+meter_h-0.015,
        x1=meter_x+meter_w-0.003, y1=meter_y+meter_h-0.005,
        fillcolor="#1a1a20", line=dict(color="#3a3a40", width=0.5))
    
    # Logo text placeholder
    fig.add_annotation(
        x=meter_x+meter_w/2, y=meter_y+meter_h-0.01,
        text="<b>GRID</b>", showarrow=False,
        font=dict(family="Arial Black", size=5, color="#5a5a65"))

    # --- Digital Display Screen ---
    screen_inset = 0.004
    screen_x = meter_x + screen_inset
    screen_y = meter_y + meter_h * 0.35
    screen_w = meter_w - screen_inset * 2
    screen_h = meter_h * 0.35

    # Screen bezel
    fig.add_shape(type="rect",
        x0=screen_x-0.002, y0=screen_y-0.002,
        x1=screen_x+screen_w+0.002, y1=screen_y+screen_h+0.002,
        fillcolor="#151520", line=dict(color="#252530", width=1))
    
    # LCD background (dark with slight glow)
    fig.add_shape(type="rect",
        x0=screen_x, y0=screen_y, x1=screen_x+screen_w, y1=screen_y+screen_h,
        fillcolor="#0a0a12", line=dict(width=0))
    
    # Screen backlight glow
    fig.add_shape(type="rect",
        x0=screen_x+0.001, y0=screen_y+0.001,
        x1=screen_x+screen_w-0.001, y1=screen_y+screen_h-0.001,
        fillcolor="rgba(0, 150, 136, 0.1)", line=dict(width=0))

    # Power reading display
    power_text = f"{p_load:.1f}"
    unit_text = "kW"
    
    fig.add_annotation(
        x=screen_x+screen_w/2, y=screen_y+screen_h*0.65,
        text=f"<b>{power_text}</b>", showarrow=False,
        font=dict(family="Courier New", size=11, color="#00E676"))
    
    fig.add_annotation(
        x=screen_x+screen_w/2, y=screen_y+screen_h*0.3,
        text=unit_text, showarrow=False,
        font=dict(family="Arial", size=7, color="#00E676"))

    # --- Load Level Bar Graph ---
    bar_x = meter_x + 0.005
    bar_w = meter_w - 0.01
    bar_y = meter_y + 0.008
    bar_h = meter_h * 0.25
    
    # Bar background
    fig.add_shape(type="rect",
        x0=bar_x, y0=bar_y, x1=bar_x+bar_w, y1=bar_y+bar_h,
        fillcolor="#0a0a12", line=dict(color="#252530", width=1))
    
    # Segmented bar display
    num_segments = 10
    segment_gap = 0.002
    segment_w = (bar_w - segment_gap * (num_segments + 1)) / num_segments
    active_segments = int(load_ratio * num_segments)
    
    for seg in range(num_segments):
        seg_x = bar_x + segment_gap + seg * (segment_w + segment_gap)
        
        # Determine segment color based on position
        if seg < num_segments * 0.5:
            seg_color_active = "#00E676"  # Green
        elif seg < num_segments * 0.75:
            seg_color_active = "#FFEB3B"  # Yellow
        else:
            seg_color_active = "#FF5722"  # Red/Orange
        
        if seg < active_segments:
            # Active segment with glow
            fig.add_shape(type="rect",
                x0=seg_x-0.001, y0=bar_y+segment_gap-0.001,
                x1=seg_x+segment_w+0.001, y1=bar_y+bar_h-segment_gap+0.001,
                fillcolor=seg_color_active, opacity=0.3, line=dict(width=0))
            
            fig.add_shape(type="rect",
                x0=seg_x, y0=bar_y+segment_gap,
                x1=seg_x+segment_w, y1=bar_y+bar_h-segment_gap,
                fillcolor=seg_color_active, line=dict(width=0))
        else:
            # Inactive segment
            fig.add_shape(type="rect",
                x0=seg_x, y0=bar_y+segment_gap,
                x1=seg_x+segment_w, y1=bar_y+bar_h-segment_gap,
                fillcolor="#1a1a20", line=dict(width=0))

    # --- Status LED Indicators ---
    led_y = meter_y + meter_h - 0.025
    led_positions = [
        (meter_x + 0.006, "#00E676", load_ratio > 0),      # Power (always on if load)
        (meter_x + 0.012, "#2196F3", True),                 # Communication
        (meter_x + 0.018, "#FF5722" if load_ratio > 0.8 else "#4a4a55", load_ratio > 0.8)  # Alert
    ]
    
    for led_x, led_color, is_active in led_positions:
        # LED glow
        if is_active:
            fig.add_trace(go.Scatter(
                x=[led_x], y=[led_y], mode="markers",
                marker=dict(size=8, color=led_color, opacity=0.3),
                hoverinfo="skip", showlegend=False))
        
        # LED body
        fig.add_trace(go.Scatter(
            x=[led_x], y=[led_y], mode="markers",
            marker=dict(size=4, color=led_color if is_active else "#2a2a30",
                       line=dict(color="#1a1a20", width=0.5)),
            hoverinfo="skip", showlegend=False))
        
        # LED highlight
        if is_active:
            fig.add_trace(go.Scatter(
                x=[led_x-0.0005], y=[led_y+0.001], mode="markers",
                marker=dict(size=1.5, color="rgba(255,255,255,0.6)"),
                hoverinfo="skip", showlegend=False))

    # --- Meter Glass Cover Reflection ---
    fig.add_shape(type="path",
        path=f"""M {meter_x+0.002},{meter_y+meter_h*0.6}
                 L {meter_x+meter_w*0.4},{meter_y+meter_h-0.003}
                 L {meter_x+0.002},{meter_y+meter_h-0.003} Z""",
        fillcolor="rgba(255,255,255,0.08)", line=dict(width=0))

    # --- Connection Cable ---
    cable_start_x = meter_x + meter_w/2
    cable_start_y = meter_y
    cable_end_x = cx + w/2 + 0.005
    cable_end_y = body_bottom + body_h * 0.7
    
    # Cable shadow
    fig.add_trace(go.Scatter(
        x=[cable_start_x+0.002, cable_end_x+0.002],
        y=[cable_start_y-0.002, cable_end_y-0.002],
        mode="lines", line=dict(color="rgba(0,0,0,0.3)", width=3),
        hoverinfo="skip", showlegend=False))
    
    # Main cable
    fig.add_trace(go.Scatter(
        x=[cable_start_x, cable_end_x],
        y=[cable_start_y, cable_end_y],
        mode="lines", line=dict(color="#2a2a35", width=2.5),
        hoverinfo="skip", showlegend=False))
    
    # Cable highlight
    fig.add_trace(go.Scatter(
        x=[cable_start_x-0.001, cable_end_x-0.001],
        y=[cable_start_y+0.001, cable_end_y+0.001],
        mode="lines", line=dict(color="rgba(255,255,255,0.1)", width=1),
        hoverinfo="skip", showlegend=False))

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. ENVIRONMENTAL DETAILS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # --- Porch Light (Active at night or high load) ---
    if is_night or load_ratio > 0.5:
        light_x = door_x + door_w + 0.008
        light_y = door_y + door_h - 0.01
        light_intensity = 0.8 if is_night else 0.4
        
        # Light fixture
        fig.add_trace(go.Scatter(
            x=[light_x], y=[light_y], mode="markers",
            marker=dict(size=6, color="#3a3a45", 
                       line=dict(color="#2a2a35", width=1)),
            hoverinfo="skip", showlegend=False))
        
        # Light glow layers
        for i in range(4):
            glow_size = 10 + i * 8
            glow_alpha = light_intensity * (0.3 - i * 0.07)
            fig.add_trace(go.Scatter(
                x=[light_x], y=[light_y], mode="markers",
                marker=dict(size=glow_size, 
                           color=f"rgba(255, 220, 150, {glow_alpha})"),
                hoverinfo="skip", showlegend=False))
        
        # Light bulb
        fig.add_trace(go.Scatter(
            x=[light_x], y=[light_y], mode="markers",
            marker=dict(size=4, color="#FFE4B5"),
            hoverinfo="skip", showlegend=False))

    # --- House Number ---
    house_num_x = door_x - 0.015
    house_num_y = door_y + door_h * 0.7
    fig.add_annotation(
        x=house_num_x, y=house_num_y,
        text="<b>42</b>", showarrow=False,
        font=dict(family="Georgia", size=8, color=colors.trim_primary),
        bgcolor="rgba(0,0,0,0.3)", borderpad=2)

    # --- Mailbox (Small detail) ---
    mb_x = cx - w/2 - 0.025
    mb_y = body_bottom + 0.02
    mb_w = 0.012
    mb_h = 0.015
    
    # Mailbox post
    fig.add_shape(type="rect",
        x0=mb_x+mb_w/2-0.002, y0=body_bottom-foundation_h,
        x1=mb_x+mb_w/2+0.002, y1=mb_y,
        fillcolor="#4a4a4a", line=dict(width=0))
    
    # Mailbox body
    fig.add_shape(type="rect",
        x0=mb_x, y0=mb_y, x1=mb_x+mb_w, y1=mb_y+mb_h,
        fillcolor="#3a5a4a", line=dict(color="#2a4a3a", width=1))
    
    # Mailbox flag
    flag_up = load_ratio > 0.7  # Flag up when high load (mail metaphor)
    flag_y = mb_y + mb_h - 0.003
    flag_angle = 0 if flag_up else 90
    
    fig.add_trace(go.Scatter(
        x=[mb_x+mb_w-0.002, mb_x+mb_w+0.006 if flag_up else mb_x+mb_w-0.002],
        y=[flag_y, flag_y+0.008 if flag_up else flag_y-0.006],
        mode="lines", line=dict(color="#FF5722", width=2),
        hoverinfo="skip", showlegend=False))

    # ═══════════════════════════════════════════════════════════════════════════
    # 10. WEATHER EFFECTS (Rainy condition)
    # ═══════════════════════════════════════════════════════════════════════════
    if weather == "rainy":
        # Rain streaks
        import random
        random.seed(42)  # Consistent rain pattern
        for _ in range(20):
            rain_x = cx + random.uniform(-w*0.8, w*0.8)
            rain_y = cy + random.uniform(-h*0.3, h*0.6)
            rain_len = random.uniform(0.008, 0.015)
            
            fig.add_trace(go.Scatter(
                x=[rain_x, rain_x+0.002], y=[rain_y, rain_y-rain_len],
                mode="lines", 
                line=dict(color="rgba(150,180,200,0.3)", width=1),
                hoverinfo="skip", showlegend=False))
        
        # Puddle reflections
        puddle_y = body_bottom - foundation_h - 0.015
        fig.add_shape(type="rect",
            x0=cx-w*0.3, y0=puddle_y-0.003,
            x1=cx+w*0.3, y1=puddle_y+0.003,
            fillcolor="rgba(100,120,140,0.3)", line=dict(width=0))

    # ═══════════════════════════════════════════════════════════════════════════
    # 11. INTERACTIVE HOVER & LABELS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Invisible hover target
    fig.add_trace(go.Scatter(
        x=[cx], y=[cy], mode="markers",
        marker=dict(size=80, color="rgba(0,0,0,0)"),
        hovertemplate=(
            f"<b style='color:{PALETTE.SOLAR_ORANGE}; font-size: 16px'>🏠 RESIDENTIAL LOAD</b><br>"
            "<span style='color:#555'>━━━━━━━━━━━━━━━━━━━</span><br><br>"
            f"<b>⚡ Active Power:</b>  <span style='color:#00E676; font-size:14px'><b>{p_load:.2f} kW</b></span><br>"
            f"<b>⚛ Reactive Power:</b>  <span style='color:#64B5F6'>{q_load:.2f} kVAR</span><br>"
            f"<b>📊 Power Factor:</b>  <span style='color:#FFB74D'>{power_factor:.2f}</span><br>"
            f"<b>📈 Load Level:</b>  <span style='color:#{'FF5722' if load_ratio > 0.8 else 'FFEB3B' if load_ratio > 0.5 else '00E676'}'>"
            f"{load_ratio*100:.0f}%</span><br><br>"
            f"<span style='color:#888'>Time: {'Night' if is_night else 'Day'} | Weather: {weather.title()}</span><br>"
            "<extra></extra>"
        ), showlegend=False))

    if show_values:
        # Title with enhanced styling
        fig.add_annotation(
            x=cx, y=roof_peak_y + 0.055,
            text="<b>⚡ LOAD</b>", showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.label_size+3, 
                     color=PALETTE.SOLAR_ORANGE),
            bgcolor="rgba(0,0,0,0.7)", borderpad=4,
            bordercolor=PALETTE.SOLAR_ORANGE, borderwidth=2)
        
        # Power value with drop shadow
        val_text = f"{p_load:.1f} kW"
        
        # Shadow
        fig.add_annotation(
            x=cx+0.002, y=body_bottom - foundation_h - 0.027,
            text=f"<b>{val_text}</b>", showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.value_size+1, 
                     color="rgba(0,0,0,0.6)"))
        
        # Main text
        fig.add_annotation(
            x=cx, y=body_bottom - foundation_h - 0.025,
            text=f"<b>{val_text}</b>", showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.value_size+1, 
                     color=PALETTE.SOLAR_ORANGE))
        
        # Load status indicator
        if load_ratio > 0.8:
            status_text = "⚠️ HIGH DEMAND"
            status_color = "#FF5722"
        elif load_ratio > 0.5:
            status_text = "📊 MODERATE"
            status_color = "#FFEB3B"
        else:
            status_text = "✓ NORMAL"
            status_color = "#00E676"
        
        fig.add_annotation(
            x=cx, y=body_bottom - foundation_h - 0.045,
            text=f"<b>{status_text}</b>", showarrow=False,
            font=dict(family=THEME.font_family, size=8, color=status_color),
            bgcolor="rgba(0,0,0,0.5)", borderpad=2)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _adjust_brightness(hex_color: str, factor: float) -> str:
    """Adjust the brightness of a hex color."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

def _interpolate_color(color1: str, color2: str, ratio: float) -> str:
    """Interpolate between two hex colors."""
    c1 = color1.lstrip('#')
    c2 = color2.lstrip('#')
    r1, g1, b1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
    r2, g2, b2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

import math  # Required for trigonometric calculations

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3D LOAD - ULTRA REALISTIC ISOMETRIC HOUSE                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_load_3d(fig: "go.Figure", values: Dict, show_values: bool) -> None:

    cx, cy = LAYOUT.LOAD
    w, h = LAYOUT.LOAD_W, LAYOUT.LOAD_H
    p_load = values.get("p_load", 0.0)

    body_h = h * 0.60
    roof_h = h * 0.40
    body_bottom = cy - h / 2
    body_top = body_bottom + body_h
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3D DEPTH PARAMETERS (STRONG ISOMETRIC EFFECT)
    # ═══════════════════════════════════════════════════════════════════════════
    dx = 0.025  # Décalage X fort pour 3D visible
    dy = -0.018  # Décalage Y fort pour 3D visible
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GROUND SHADOW (Soft drop shadow)
    # ═══════════════════════════════════════════════════════════════════════════
    for i in range(6):
        alpha = 0.12 - i * 0.018
        expand = i * 0.005
        fig.add_shape(
            type="rect",
            x0=cx - w/2 - expand + 0.01,
            y0=body_bottom - 0.02 - expand * 0.5,
            x1=cx + w/2 + expand + dx,
            y1=body_bottom + 0.003,
            fillcolor=f"rgba(0, 0, 0, {alpha})",
            line=dict(width=0),
            layer="below",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # 3D HOUSE - RIGHT SIDE WALL (Dark side)
    # ═══════════════════════════════════════════════════════════════════════════
    right_wall = (
        f"M {cx + w/2},{body_bottom} "
        f"L {cx + w/2 + dx},{body_bottom + dy} "
        f"L {cx + w/2 + dx},{body_top + dy} "
        f"L {cx + w/2},{body_top} Z"
    )
    fig.add_shape(
        type="path",
        path=right_wall,
        fillcolor="#1a0a00",  # Très sombre - côté ombre
        line=dict(color="#FF6B00", width=1.5),
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3D HOUSE - BOTTOM FACE (Ground connection)
    # ═══════════════════════════════════════════════════════════════════════════
    bottom_face = (
        f"M {cx - w/2},{body_bottom} "
        f"L {cx - w/2 + dx},{body_bottom + dy} "
        f"L {cx + w/2 + dx},{body_bottom + dy} "
        f"L {cx + w/2},{body_bottom} Z"
    )
    fig.add_shape(
        type="path",
        path=bottom_face,
        fillcolor="#0d0500",  # Encore plus sombre
        line=dict(color="#FF6B00", width=1),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN HOUSE BODY - FRONT FACE
    # ═══════════════════════════════════════════════════════════════════════════
    fig.add_shape(
        type="rect",
        x0=cx - w/2,
        y0=body_bottom,
        x1=cx + w/2,
        y1=body_top,
        fillcolor="#2d1810",  # Brun foncé chaud
        line=dict(color=PALETTE.SOLAR_ORANGE, width=2.5),
    )
    
    # Front face gradient highlight (lumière du haut-gauche)
    fig.add_shape(
        type="rect",
        x0=cx - w/2,
        y0=body_top - body_h * 0.25,
        x1=cx - w/2 + w * 0.12,
        y1=body_top,
        fillcolor="rgba(255, 150, 100, 0.08)",
        line=dict(width=0),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 3D ROOF - RIGHT SLOPE BACK (Creates depth)
    # ═══════════════════════════════════════════════════════════════════════════
    roof_right_back = (
        f"M {cx + w/2 + 0.02},{body_top} "
        f"L {cx + w/2 + 0.02 + dx},{body_top + dy} "
        f"L {cx + dx},{body_top + roof_h + dy} "
        f"L {cx},{body_top + roof_h} Z"
    )
    fig.add_shape(
        type="path",
        path=roof_right_back,
        fillcolor="#8B2500",  # Rouge brique sombre
        line=dict(color="#FF6B00", width=1),
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3D ROOF - TOP EDGE (Ridge depth)
    # ═══════════════════════════════════════════════════════════════════════════
    roof_top_edge = (
        f"M {cx},{body_top + roof_h} "
        f"L {cx + dx},{body_top + roof_h + dy} "
        f"L {cx + w/2 + 0.02 + dx},{body_top + dy} "
        f"L {cx + w/2 + 0.02},{body_top} Z"
    )
    # Already covered by roof_right_back

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN ROOF - LEFT SLOPE (Lit side - bright)
    # ═══════════════════════════════════════════════════════════════════════════
    roof_left = (
        f"M {cx - w/2 - 0.02},{body_top} "
        f"L {cx},{body_top + roof_h} "
        f"L {cx},{body_top} Z"
    )
    fig.add_shape(
        type="path",
        path=roof_left,
        fillcolor=PALETTE.SOLAR_ORANGE,  # Orange vif - côté éclairé
        line=dict(color="#FFaa00", width=2),
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN ROOF - RIGHT SLOPE (Shadow side - darker)
    # ═══════════════════════════════════════════════════════════════════════════
    roof_right = (
        f"M {cx},{body_top} "
        f"L {cx},{body_top + roof_h} "
        f"L {cx + w/2 + 0.02},{body_top} Z"
    )
    fig.add_shape(
        type="path",
        path=roof_right,
        fillcolor="#CC5500",  # Orange plus sombre - côté ombre
        line=dict(color=PALETTE.SOLAR_ORANGE, width=2),
    )
    
    # Roof ridge line (highlight)
    fig.add_trace(
        go.Scatter(
            x=[cx - w/2 - 0.02, cx],
            y=[body_top, body_top + roof_h],
            mode="lines",
            line=dict(color="rgba(255, 255, 200, 0.4)", width=2),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CHIMNEY 3D
    # ═══════════════════════════════════════════════════════════════════════════
    chim_x = cx + w * 0.22
    chim_w, chim_h = 0.016, 0.04
    chim_base = body_top + roof_h * 0.35
    
    # Chimney right side
    chim_side = (
        f"M {chim_x + chim_w},{chim_base} "
        f"L {chim_x + chim_w + 0.006},{chim_base - 0.004} "
        f"L {chim_x + chim_w + 0.006},{chim_base + chim_h - 0.004} "
        f"L {chim_x + chim_w},{chim_base + chim_h} Z"
    )
    fig.add_shape(type="path", path=chim_side, fillcolor="#1a1a2e", line=dict(width=0))
    
    # Chimney front
    fig.add_shape(
        type="rect",
        x0=chim_x, y0=chim_base,
        x1=chim_x + chim_w, y1=chim_base + chim_h,
        fillcolor="#3d3d5c",
        line=dict(color=PALETTE.STELLAR_GRAY, width=1),
    )
    
    # Chimney cap
    fig.add_shape(
        type="rect",
        x0=chim_x - 0.003, y0=chim_base + chim_h,
        x1=chim_x + chim_w + 0.006, y1=chim_base + chim_h + 0.008,
        fillcolor="#5a5a7a",
        line=dict(color=PALETTE.STELLAR_GRAY, width=1),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 3D WINDOWS with glow, frames, and reflections
    # ═══════════════════════════════════════════════════════════════════════════
    win_size = 0.024
    win_gap = 0.014
    win_rows, win_cols = 2, 2
    start_y = body_bottom + 0.025
    
    for row in range(win_rows):
        for col in range(win_cols):
            wx = cx + (col - 0.5) * (win_size + win_gap)
            wy = start_y + row * (win_size + win_gap)
            
            # Window glow (warm light from inside)
            for g in range(4):
                ga = 0.2 - g * 0.045
                ge = g * 0.005
                fig.add_shape(
                    type="rect",
                    x0=wx - win_size/2 - ge, y0=wy - ge,
                    x1=wx + win_size/2 + ge, y1=wy + win_size + ge,
                    fillcolor=f"rgba(255, 200, 80, {ga})",
                    line=dict(width=0),
                )
            
            # Window recess (3D depth)
            fig.add_shape(
                type="rect",
                x0=wx - win_size/2 - 0.004, y0=wy - 0.004,
                x1=wx + win_size/2 + 0.004, y1=wy + win_size + 0.004,
                fillcolor="#0d0500",
                line=dict(color=PALETTE.SOLAR_ORANGE, width=1.5),
            )
            
            # Window glass
            fig.add_shape(
                type="rect",
                x0=wx - win_size/2, y0=wy,
                x1=wx + win_size/2, y1=wy + win_size,
                fillcolor=PALETTE.FUSION_YELLOW,
                line=dict(width=0),
            )
            
            # Window cross muntins
            fig.add_trace(go.Scatter(
                x=[wx - win_size/2, wx + win_size/2], y=[wy + win_size/2, wy + win_size/2],
                mode="lines", line=dict(color="#8B4513", width=2),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=[wx, wx], y=[wy, wy + win_size],
                mode="lines", line=dict(color="#8B4513", width=2),
                showlegend=False, hoverinfo="skip",
            ))
            
            # Window reflection (top-left highlight)
            fig.add_shape(
                type="rect",
                x0=wx - win_size/2 + 0.002, y0=wy + win_size * 0.55,
                x1=wx - win_size/2 + win_size * 0.35, y1=wy + win_size - 0.002,
                fillcolor="rgba(255, 255, 255, 0.35)",
                line=dict(width=0),
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # 3D ENERGY METER (Highly detailed)
    # ═══════════════════════════════════════════════════════════════════════════
    m_x = cx + w/2 + 0.03
    m_h = h * 0.65
    m_w = 0.022
    m_bottom = cy - m_h/2
    m_dx, m_dy = 0.008, -0.006

    # Meter shadow
    fig.add_shape(
        type="rect",
        x0=m_x + 0.01, y0=m_bottom - 0.015,
        x1=m_x + m_w + 0.015, y1=m_bottom + m_h - 0.01,
        fillcolor="rgba(0, 0, 0, 0.35)",
        line=dict(width=0),
        layer="below",
    )
    
    # Meter right side (3D)
    meter_side = (
        f"M {m_x + m_w},{m_bottom} "
        f"L {m_x + m_w + m_dx},{m_bottom + m_dy} "
        f"L {m_x + m_w + m_dx},{m_bottom + m_h + m_dy} "
        f"L {m_x + m_w},{m_bottom + m_h} Z"
    )
    fig.add_shape(type="path", path=meter_side, fillcolor="#1a1a2e", line=dict(color="#4a4a6a", width=1))
    
    # Meter bottom (3D)
    meter_bot = (
        f"M {m_x},{m_bottom} "
        f"L {m_x + m_dx},{m_bottom + m_dy} "
        f"L {m_x + m_w + m_dx},{m_bottom + m_dy} "
        f"L {m_x + m_w},{m_bottom} Z"
    )
    fig.add_shape(type="path", path=meter_bot, fillcolor="#0f0f1a", line=dict(color="#4a4a6a", width=1))

    # Meter body front
    fig.add_shape(
        type="rect",
        x0=m_x, y0=m_bottom,
        x1=m_x + m_w, y1=m_bottom + m_h,
        fillcolor="#0a0a12",
        line=dict(color=PALETTE.STELLAR_GRAY, width=2),
    )
    
    # Meter inner bezel
    fig.add_shape(
        type="rect",
        x0=m_x + 0.003, y0=m_bottom + 0.003,
        x1=m_x + m_w - 0.003, y1=m_bottom + m_h - 0.003,
        fillcolor="#050508",
        line=dict(color="#2a2a40", width=1),
    )

    # Load fill
    load_fill = min(1.0, p_load / 60.0)
    fill_h = (m_h - 0.008) * load_fill
    
    # Fill glow
    for g in range(3):
        ga = 0.35 - g * 0.1
        fig.add_shape(
            type="rect",
            x0=m_x + 0.004 - g*0.001, y0=m_bottom + 0.004,
            x1=m_x + m_w - 0.004 + g*0.001, y1=m_bottom + 0.004 + fill_h,
            fillcolor=f"rgba(255, 120, 0, {ga})",
            line=dict(width=0),
        )
    
    # Main fill
    fig.add_shape(
        type="rect",
        x0=m_x + 0.005, y0=m_bottom + 0.005,
        x1=m_x + m_w - 0.005, y1=m_bottom + 0.005 + fill_h,
        fillcolor=PALETTE.SOLAR_ORANGE,
        line=dict(width=0),
    )
    
    # Fill glossy highlight
    fig.add_shape(
        type="rect",
        x0=m_x + 0.005, y0=m_bottom + 0.005,
        x1=m_x + 0.009, y1=m_bottom + 0.005 + fill_h,
        fillcolor="rgba(255, 255, 255, 0.25)",
        line=dict(width=0),
    )
    
    # Scale marks
    for i in range(7):
        mark_y = m_bottom + 0.005 + (m_h - 0.01) * i / 6
        fig.add_trace(go.Scatter(
            x=[m_x + m_w - 0.004, m_x + m_w - 0.008],
            y=[mark_y, mark_y],
            mode="lines", line=dict(color=PALETTE.STELLAR_GRAY, width=1),
            showlegend=False, hoverinfo="skip",
        ))

    # ═══════════════════════════════════════════════════════════════════════════
    # HOVER ZONE
    # ═══════════════════════════════════════════════════════════════════════════
    fig.add_trace(
        go.Scatter(
            x=[cx], y=[cy],
            mode="markers",
            marker=dict(size=55, color="rgba(0,0,0,0)"),
            hovertemplate=(
                f"<b style='color:{PALETTE.SOLAR_ORANGE}'>🏠 LOAD CONSUMPTION</b><br>"
                "─────────────────<br>"
                f"<b>Active Power:</b> {p_load:.2f} kW<br>"
                f"<b>Power Factor:</b> 0.95<br>"
                f"<b>Type:</b> Residential<br>"
                f"<b>Demand Response:</b> Available<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # LABELS
    # ═══════════════════════════════════════════════════════════════════════════
    if show_values:
        # LOAD label with glow
        fig.add_annotation(
            x=cx, y=body_top + roof_h + 0.05,
            text="<b>LOAD</b>",
            showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.label_size + 1, color="rgba(255, 140, 0, 0.4)"),
        )
        fig.add_annotation(
            x=cx, y=body_top + roof_h + 0.045,
            text="<b>LOAD</b>",
            showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.label_size, color=PALETTE.SOLAR_ORANGE),
        )
        
        # Value with shadow
        fig.add_annotation(
            x=cx + 0.003, y=body_bottom - 0.047,
            text=f"<b style='font-size:20px'>{p_load:.1f}</b> kW",
            showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.value_size, color="rgba(0, 0, 0, 0.6)"),
        )
        fig.add_annotation(
            x=cx, y=body_bottom - 0.045,
            text=f"<b style='font-size:20px'>{p_load:.1f}</b> kW",
            showarrow=False,
            font=dict(family=THEME.font_family, size=THEME.value_size, color=PALETTE.SOLAR_ORANGE),
        )
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  UTILITY GRID - CLEAN MINIMALIST DESIGN                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_grid_3d(fig: "go.Figure", values: Dict, show_values: bool) -> None:
    """
    Render clean, minimalist utility grid component.
    Simple design optimized for readability and performance.
    """
    cx, cy = LAYOUT.GRID
    w, h = LAYOUT.GRID_W, LAYOUT.GRID_H

    # Extract grid state
    p_grid = values.get("p_grid", 0.0)
    tariff = values.get("tariff", 0.19)
    voltage = values.get("voltage", 230)
    frequency = values.get("frequency", 50.0)

    # ═══ STATE-BASED STYLING ═══
    if p_grid > 0.5:
        primary_color = PALETTE.GRID_BLUE
        accent_color = PALETTE.NEON_CYAN
        direction = "IMPORT"
        direction_icon = "↓"
    elif p_grid < -0.5:
        primary_color = PALETTE.MATRIX_GREEN
        accent_color = PALETTE.SAFE_EMERALD
        direction = "EXPORT"
        direction_icon = "↑"
    else:
        primary_color = PALETTE.STELLAR_GRAY
        accent_color = "#5A6A7A"
        direction = "IDLE"
        direction_icon = "○"

    # ═══ MAIN TRANSFORMER BODY ═══
    body_w = w * 1.2
    body_h = h * 1.4

    # Outer glow (subtle)
    fig.add_shape(
        type="rect",
        x0=cx - body_w/2 - 0.008,
        y0=cy - body_h/2 - 0.008,
        x1=cx + body_w/2 + 0.008,
        y1=cy + body_h/2 + 0.008,
        fillcolor=f"rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.15)",
        line=dict(width=0),
        layer="below",
    )

    # Main body - dark panel
    fig.add_shape(
        type="rect",
        x0=cx - body_w/2,
        y0=cy - body_h/2,
        x1=cx + body_w/2,
        y1=cy + body_h/2,
        fillcolor=PALETTE.COSMIC_DARK,
        line=dict(color=primary_color, width=2.5),
    )

    # Top accent bar
    fig.add_shape(
        type="rect",
        x0=cx - body_w/2,
        y0=cy + body_h/2 - 0.012,
        x1=cx + body_w/2,
        y1=cy + body_h/2,
        fillcolor=primary_color,
        line=dict(width=0),
    )

    # ═══ GRID SYMBOL (simplified power lines) ═══
    line_color = accent_color if p_grid != 0 else PALETTE.STELLAR_GRAY

    # Three vertical lines (power transmission symbol)
    for offset in [-0.025, 0, 0.025]:
        fig.add_shape(
            type="line",
            x0=cx + offset,
            y0=cy + 0.015,
            x1=cx + offset,
            y1=cy + body_h/2 - 0.020,
            line=dict(color=line_color, width=2.5),
        )

    # Horizontal crossbar
    fig.add_shape(
        type="line",
        x0=cx - 0.035,
        y0=cy + body_h/2 - 0.025,
        x1=cx + 0.035,
        y1=cy + body_h/2 - 0.025,
        line=dict(color=line_color, width=2),
    )

    # ═══ STATUS INDICATOR LIGHT ═══
    indicator_y = cy - body_h/2 + 0.020
    fig.add_shape(
        type="circle",
        x0=cx - 0.012,
        y0=indicator_y - 0.010,
        x1=cx + 0.012,
        y1=indicator_y + 0.010,
        fillcolor=primary_color,
        line=dict(color="white", width=1),
    )

    # ═══ COMPONENT LABEL ═══
    fig.add_annotation(
        x=cx,
        y=cy + body_h/2 + 0.045,
        text=f"<b>⚡ UTILITY GRID</b>",
        showarrow=False,
        font=dict(
            family=THEME.font_family,
            size=THEME.label_size,
            color=primary_color,
        ),
        bgcolor=PALETTE.DEEP_SPACE,
        bordercolor=primary_color,
        borderwidth=1.5,
        borderpad=4,
    )

    # ═══ DIRECTION INDICATOR ═══
    fig.add_annotation(
        x=cx,
        y=cy - 0.010,
        text=f"<b>{direction_icon}</b>",
        showarrow=False,
        font=dict(
            family=THEME.font_mono,
            size=24,
            color=accent_color,
        ),
    )

    # ═══ POWER VALUE ═══
    if show_values:
        power_text = f"{abs(p_grid):.2f}" if abs(p_grid) < 10 else f"{abs(p_grid):.1f}"
        fig.add_annotation(
            x=cx,
            y=cy - body_h/2 - 0.040,
            text=f"<b>{direction}</b>",
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=14,
                color=primary_color,
            ),
        )
        fig.add_annotation(
            x=cx,
            y=cy - body_h/2 - 0.075,
            text=f"<b>{power_text} kW</b>",
            showarrow=False,
            font=dict(
                family=THEME.font_mono,
                size=THEME.value_size,
                color=accent_color,
            ),
        )

    # ═══ HOVER INFO ═══
    fig.add_trace(
        go.Scatter(
            x=[cx],
            y=[cy],
            mode="markers",
            marker=dict(size=50, color="rgba(0,0,0,0)"),
            hovertemplate=(
                f"<b>⚡ UTILITY GRID</b><br>"
                f"<b>Status:</b> {direction}<br>"
                f"<b>Power:</b> {abs(p_grid):.2f} kW<br>"
                f"<b>Tariff:</b> {tariff:.3f} TND/kWh<br>"
                f"<extra></extra>"
            ),
            showlegend=False,
        )
    )
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STATIC POWER FLOW (GLOW LINES)                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_power_flow_static(fig: "go.Figure", values: Dict) -> None:
    p_pv = values.get("p_pv", 0.0)
    p_battery = values.get("p_battery", 0.0)
    p_grid = values.get("p_grid", 0.0)
    p_load = values.get("p_load", 0.0)

    bus_y = LAYOUT.BUS_Y

    if p_pv > 1.0:
        _draw_power_line(
            fig,
            LAYOUT.SOLAR[0],
            LAYOUT.SOLAR[1] - LAYOUT.SOLAR_H / 2 - 0.03,
            LAYOUT.SOLAR[0],
            bus_y + LAYOUT.BUS_H / 2 + 0.02,
            p_pv,
            PALETTE.SOLAR_GOLD,
        )

    bx, by = LAYOUT.BATTERY
    if abs(p_battery) > 0.5:
        color = (
            PALETTE.MATRIX_GREEN
            if p_battery > 0
            else PALETTE.DANGER_RED
        )
        if p_battery > 0:
            _draw_power_line(
                fig,
                bx,
                bus_y - LAYOUT.BUS_H / 2 - 0.02,
                bx,
                by + LAYOUT.BATTERY_H / 2 + 0.03,
                abs(p_battery),
                color,
            )
        else:
            _draw_power_line(
                fig,
                bx,
                by + LAYOUT.BATTERY_H / 2 + 0.03,
                bx,
                bus_y - LAYOUT.BUS_H / 2 - 0.02,
                abs(p_battery),
                color,
            )

    if p_load > 1.0:
        lx, ly = LAYOUT.LOAD
        _draw_power_line(
            fig,
            lx,
            bus_y - LAYOUT.BUS_H / 2 - 0.02,
            lx,
            ly + LAYOUT.LOAD_H / 2 + 0.03,
            p_load,
            PALETTE.SOLAR_ORANGE,
        )

    gx, gy = LAYOUT.GRID
    if abs(p_grid) > 0.5:
        color = PALETTE.GRID_BLUE if p_grid > 0 else PALETTE.GRID_EXPORT
        if p_grid > 0:
            _draw_power_line(
                fig,
                gx,
                gy + LAYOUT.GRID_H / 2 + 0.03,
                bx,
                by - LAYOUT.BATTERY_H / 2 - 0.03,
                abs(p_grid),
                color,
            )
        else:
            _draw_power_line(
                fig,
                bx,
                by - LAYOUT.BATTERY_H / 2 - 0.03,
                gx,
                gy + LAYOUT.GRID_H / 2 + 0.03,
                abs(p_grid),
                color,
            )


def _draw_power_line(
    fig: "go.Figure",
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    power: float,
    color: str,
) -> None:
    thickness = max(2.0, min(10.0, 2.0 + power / 8.0))
    fig.add_shape(
        type="line",
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line=dict(color=_hex_to_rgba(color, 0.3), width=thickness + 6.0),
        layer="below",
    )
    fig.add_shape(
        type="line",
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line=dict(color=color, width=thickness),
    )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  BEZIER SAMPLING FOR PARTICLE FLOWS                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _sample_bezier_segment(
    start: Tuple[float, float],
    end: Tuple[float, float],
    curvature: float = 0.0,
    n_points: int = 80,
) -> Tuple[List[float], List[float]]:
    """
    Sample a quadratic Bézier path between start and end.

    curvature:
        0.0 = straight line
        >0 = bulge to one side, <0 = bulge to opposite side
        magnitude is relative to path length.
    """
    x0, y0 = start
    x1, y1 = end
    if n_points < 2:
        return [x0, x1], [y0, y1]

    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy) or 1.0

    if abs(curvature) < 1e-6:
        xs = [x0 + dx * (i / (n_points - 1)) for i in range(n_points)]
        ys = [y0 + dy * (i / (n_points - 1)) for i in range(n_points)]
        return xs, ys

    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    nx, ny = -dy / dist, dx / dist  # Perpendicular direction
    offset = curvature * dist
    cx, cy = mx + nx * offset, my + ny * offset

    xs: List[float] = []
    ys: List[float] = []
    for i in range(n_points):
        t = i / (n_points - 1)
        one_t = 1.0 - t
        bx = one_t * one_t * x0 + 2.0 * one_t * t * cx + t * t * x1
        by = one_t * one_t * y0 + 2.0 * one_t * t * cy + t * t * y1
        xs.append(bx)
        ys.append(by)
    return xs, ys


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ANIMATED PARTICLE FLOW (ELECTRONS)                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _add_particle_animation(
    fig: "go.Figure",
    values: Dict,
    particle_density: int,
) -> None:
    """
    Add animated particles flowing along Bezier power lines.

    Particles follow curved paths with head–tail gradient and
    size modulation → cinematic plasma stream effect.
    """
    p_pv = values.get("p_pv", 0.0)
    p_battery = values.get("p_battery", 0.0)
    p_grid = values.get("p_grid", 0.0)
    p_load = values.get("p_load", 0.0)

    flows: List[Dict[str, Any]] = []
    bus_y = LAYOUT.BUS_Y

    # PV → Bus (gentle curve, centered)
    if p_pv > 1.0:
        flows.append(
            dict(
                start=(
                    LAYOUT.SOLAR[0],
                    LAYOUT.SOLAR[1] - LAYOUT.SOLAR_H / 2 - 0.03,
                ),
                end=(
                    LAYOUT.SOLAR[0],
                    bus_y + LAYOUT.BUS_H / 2 + 0.02,
                ),
                color=PALETTE.SOLAR_GOLD,
                power=p_pv,
                curvature=0.02,
            )
        )

    # Battery flows
    bx, by = LAYOUT.BATTERY
    if p_battery > 0.5:  # Charging
        flows.append(
            dict(
                start=(bx, bus_y - LAYOUT.BUS_H / 2 - 0.02),
                end=(bx, by + LAYOUT.BATTERY_H / 2 + 0.03),
                color=PALETTE.MATRIX_GREEN,
                power=abs(p_battery),
                curvature=-0.10,
            )
        )
    elif p_battery < -0.5:  # Discharging
        flows.append(
            dict(
                start=(bx, by + LAYOUT.BATTERY_H / 2 + 0.03),
                end=(bx, bus_y - LAYOUT.BUS_H / 2 - 0.02),
                color=PALETTE.DANGER_RED,
                power=abs(p_battery),
                curvature=0.10,
            )
        )

    # Load flow
    if p_load > 1.0:
        lx, ly = LAYOUT.LOAD
        flows.append(
            dict(
                start=(lx, bus_y - LAYOUT.BUS_H / 2 - 0.02),
                end=(lx, ly + LAYOUT.LOAD_H / 2 + 0.03),
                color=PALETTE.SOLAR_ORANGE,
                power=p_load,
                curvature=0.10,
            )
        )

    # Grid flows
    gx, gy = LAYOUT.GRID
    if p_grid > 0.5:  # Import
        flows.append(
            dict(
                start=(gx, gy + LAYOUT.GRID_H / 2 + 0.03),
                end=(bx, by - LAYOUT.BATTERY_H / 2 - 0.03),
                color=PALETTE.GRID_BLUE,
                power=abs(p_grid),
                curvature=0.30,
            )
        )
    elif p_grid < -0.5:  # Export
        flows.append(
            dict(
                start=(bx, by - LAYOUT.BATTERY_H / 2 - 0.03),
                end=(gx, gy + LAYOUT.GRID_H / 2 + 0.03),
                color=PALETTE.GRID_EXPORT,
                power=abs(p_grid),
                curvature=-0.30,
            )
        )

    if not flows:
        return

    n_frames = 32
    frames: List[go.Frame] = []

    for frame_idx in range(n_frames):
        frame_traces: List[go.Scatter] = []
        for flow in flows:
            start = flow["start"]
            end = flow["end"]
            curvature = flow.get("curvature", 0.0)
            base_color = flow["color"]
            power = max(1e-3, float(flow["power"]))

            path_x, path_y = _sample_bezier_segment(
                start, end, curvature=curvature, n_points=120
            )
            N = len(path_x)

            power_norm = min(1.0, max(0.05, power / 40.0))
            n_particles = max(4, int(particle_density * power_norm * 1.4))
            base_size = 4 + 5 * power_norm
            speed = 0.25 + 0.9 * power_norm

            xs: List[float] = []
            ys: List[float] = []
            sizes: List[float] = []
            colors: List[str] = []

            for p_idx in range(n_particles):
                base_t = p_idx / n_particles
                t = (frame_idx / n_frames * speed + base_t) % 1.0
                idx = min(N - 1, int(t * (N - 1)))

                xs.append(path_x[idx])
                ys.append(path_y[idx])

                size = base_size * (0.8 + 0.7 * math.sin(math.pi * base_t))
                sizes.append(size)

                alpha = 0.25 + 0.65 * (0.3 + 0.7 * base_t)
                colors.append(_hex_to_rgba(base_color, alpha))

            frame_traces.append(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="markers",
                    marker=dict(
                        size=sizes,
                        color=colors,
                        symbol="circle",
                        line=dict(width=0),
                    ),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        frames.append(go.Frame(data=frame_traces, name=str(frame_idx)))

    # Initial traces (frame 0 preview)
    for flow in flows:
        start = flow["start"]
        end = flow["end"]
        curvature = flow.get("curvature", 0.0)
        base_color = flow["color"]
        power = max(1e-3, float(flow["power"]))

        path_x, path_y = _sample_bezier_segment(start, end, curvature, 120)
        N = len(path_x)
        power_norm = min(1.0, max(0.05, power / 40.0))
        n_particles = max(4, int(particle_density * power_norm * 1.4))
        base_size = 4 + 5 * power_norm

        xs: List[float] = []
        ys: List[float] = []
        sizes: List[float] = []
        colors: List[str] = []

        for p_idx in range(n_particles):
            base_t = p_idx / n_particles
            idx = min(N - 1, int(base_t * (N - 1)))
            xs.append(path_x[idx])
            ys.append(path_y[idx])
            size = base_size * (0.8 + 0.7 * math.sin(math.pi * base_t))
            sizes.append(size)
            alpha = 0.25 + 0.65 * (0.3 + 0.7 * base_t)
            colors.append(_hex_to_rgba(base_color, alpha))

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=colors,
                    symbol="circle",
                    line=dict(width=0),
                ),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig.frames = frames



# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STATUS HUD                                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _render_status_hud(fig: "go.Figure", values: Dict) -> None:
    """
    GRAND FORMAT HUD - Thesis Defense Edition.
    Clean, readable status indicators for back-of-room visibility.
    Uses paper-relative coordinates for reliable positioning.
    """
    voltage = values.get("voltage", 230.0)
    frequency = values.get("frequency", 50.0)
    soc = values.get("soc", 0.5)
    is_safe = values.get("is_safe", True)
    cbf_active = values.get("cbf_active", False)
    barrier = values.get("barrier_value", 0.0)

    # ═══ GRAND FORMAT HUD - 4 key metrics (clean layout) ═══
    metrics = [
        dict(
            xref=0.12,
            label="VOLTAGE",
            value=f"{voltage:.1f}V",
            ok=220.0 <= voltage <= 240.0,
        ),
        dict(
            xref=0.37,
            label="FREQUENCY",
            value=f"{frequency:.2f}Hz",
            ok=49.5 <= frequency <= 50.5,
        ),
        dict(
            xref=0.62,
            label="BATTERY",
            value=f"{soc*100:.0f}%",
            ok=0.2 <= soc <= 0.9,
        ),
        dict(
            xref=0.87,
            label="STATUS",
            value="SAFE" if is_safe else "ALERT",
            ok=is_safe,
        ),
    ]

    for m in metrics:
        color = PALETTE.MATRIX_GREEN if m["ok"] else PALETTE.DANGER_RED

        # ═══ PANEL BACKGROUND ═══
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=m["xref"] - 0.11,
            y0=-0.02,
            x1=m["xref"] + 0.11,
            y1=0.14,
            fillcolor=PALETTE.COSMIC_DARK,
            line=dict(color=color, width=2.5),
            layer="below",
        )

        # ═══ TOP ACCENT BAR ═══
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=m["xref"] - 0.11,
            y0=0.12,
            x1=m["xref"] + 0.11,
            y1=0.14,
            fillcolor=color,
            line=dict(width=0),
        )

        # ═══ LABEL (READABLE SIZE) ═══
        fig.add_annotation(
            xref="paper", yref="paper",
            x=m["xref"],
            y=0.10,
            text=f"<b>{m['label']}</b>",
            showarrow=False,
            font=dict(
                family=THEME.font_family,
                size=14,
                color=PALETTE.STELLAR_GRAY,
            ),
        )

        # ═══ VALUE (MASSIVE - BACK OF ROOM) ═══
        fig.add_annotation(
            xref="paper", yref="paper",
            x=m["xref"],
            y=0.04,
            text=f"<b>{m['value']}</b>",
            showarrow=False,
            font=dict(
                family=THEME.font_mono,
                size=24,
                color=color,
            ),
        )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  BUS HOVER (AGGREGATE POWER SUMMARY)                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _add_bus_hover(fig: "go.Figure", values: Dict) -> None:
    """Add an invisible hover target over the bus with aggregate power summary."""
    x_bus = (LAYOUT.BUS_X_START + LAYOUT.BUS_X_END) / 2.0
    y_bus = LAYOUT.BUS_Y

    p_pv = values.get("p_pv", 0.0)
    p_batt = values.get("p_battery", 0.0)
    p_grid = values.get("p_grid", 0.0)
    p_load = values.get("p_load", 0.0)
    net = p_pv + p_grid + p_batt - p_load

    fig.add_trace(
        go.Scatter(
            x=[x_bus],
            y=[y_bus],
            mode="markers",
            marker=dict(size=80, color="rgba(0,0,0,0)"),
            hovertemplate=(
                "<b>◆ POWER BUS SUMMARY ◆</b><br>"
                "─────────────────────<br>"
                f"<b>PV → Bus:</b> {p_pv:.2f} kW<br>"
                f"<b>Battery:</b> {p_batt:.2f} kW<br>"
                f"<b>Grid:</b> {p_grid:.2f} kW<br>"
                f"<b>Load:</b> {p_load:.2f} kW<br>"
                "─────────────────────<br>"
                f"<b>Net Balance:</b> {net:.2f} kW "
                f"({'Surplus' if net >= 0 else 'Deficit'})<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STANDALONE WIDGETS (BATTERY GAUGE & CBF STATUS)                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def create_battery_gauge(
    soc: float,
    is_charging: bool = False,
    theme: str = "dark",
) -> "go.Figure":
    """Standalone battery gauge widget."""
    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly is required")

    pal = LIGHT_THEME if theme == "light" else PALETTE
    bg_color = pal.DEEP_SPACE
    text_color = "#2C3E50" if theme == "light" else "white"

    if soc >= 0.6:
        fill_color = pal.BATTERY_FULL
    elif soc >= 0.3:
        fill_color = pal.BATTERY_MID
    elif soc >= 0.15:
        fill_color = pal.BATTERY_LOW
    else:
        fill_color = pal.BATTERY_CRITICAL

    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=soc * 100.0,
            number={"suffix": "%", "font": {"size": 32, "color": text_color}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": pal.STELLAR_GRAY,
                },
                "bar": {"color": fill_color, "thickness": 0.7},
                "bgcolor": pal.NEBULA_GRAY,
                "borderwidth": 2,
                "bordercolor": pal.STELLAR_GRAY,
                "steps": [
                    {"range": [0, 20], "color": _hex_to_rgba(pal.BATTERY_CRITICAL, 0.2)},
                    {"range": [20, 40], "color": _hex_to_rgba(pal.BATTERY_LOW, 0.2)},
                    {"range": [40, 70], "color": _hex_to_rgba(pal.BATTERY_MID, 0.2)},
                    {"range": [70, 100], "color": _hex_to_rgba(pal.BATTERY_FULL, 0.2)},
                ],
                "threshold": {
                    "line": {"color": pal.DANGER_RED, "width": 4},
                    "thickness": 0.75,
                    "value": 20,
                },
            },
            title={
                "text": f"{'⚡ Charging' if is_charging else '🔋 Battery SOC'}",
                "font": {"size": 14, "color": text_color},
            },
        )
    )

    fig.update_layout(
        paper_bgcolor=bg_color,
        font={"color": text_color},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def create_cbf_status_indicator(
    cbf_active: bool,
    barrier_value: float,
    safety_margin: float,
    theme: str = "dark",
) -> "go.Figure":
    """Standalone U‑CBF status indicator widget."""
    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly is required")

    pal = LIGHT_THEME if theme == "light" else PALETTE
    bg_color = pal.DEEP_SPACE
    text_color = "#2C3E50" if theme == "light" else "white"

    is_safe = barrier_value > 0
    if not is_safe:
        status_color = pal.DANGER_RED
        status_text = "⚠️ VIOLATION"
    elif cbf_active:
        status_color = pal.WARNING_AMBER
        status_text = "⚡ ACTIVE"
    else:
        status_color = pal.MATRIX_GREEN
        status_text = "✓ NOMINAL"

    fig = go.Figure()
    max_barrier = 50.0

    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=barrier_value,
            number={"font": {"size": 28, "color": text_color}},
            delta={
                "reference": 0,
                "increasing": {"color": pal.MATRIX_GREEN},
                "decreasing": {"color": pal.DANGER_RED},
            },
            gauge={
                "axis": {
                    "range": [-10, max_barrier],
                    "tickwidth": 1,
                    "tickcolor": pal.STELLAR_GRAY,
                },
                "bar": {"color": status_color, "thickness": 0.6},
                "bgcolor": pal.NEBULA_GRAY,
                "borderwidth": 2,
                "bordercolor": pal.STELLAR_GRAY,
                "threshold": {
                    "line": {"color": pal.DANGER_RED, "width": 4},
                    "thickness": 0.75,
                    "value": 0,
                },
            },
            title={
                "text": f"🛡️ U-CBF: {status_text}",
                "font": {"size": 14, "color": status_color},
            },
        )
    )

    fig.update_layout(
        paper_bgcolor=bg_color,
        font={"color": text_color},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[
            dict(
                x=0.5,
                y=0.15,
                xref="paper",
                yref="paper",
                text=f"h(x) = {barrier_value:.2f} | Δ = {safety_margin:.1f}V",
                showarrow=False,
                font=dict(size=11, color=pal.STELLAR_GRAY),
            )
        ],
    )
    return fig


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DEMO / TEST                                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    """Generate demo visualizations for manual inspection."""
    if not PLOTLY_AVAILABLE:
        raise SystemExit("Plotly not available; install plotly to run the demo.")

    print("╔" + "═" * 58 + "╗")
    print("║  MICROGRID SCHEMATIC - HYPERCINEMATIC EDITION v4.0        ║")
    print("║  Turing Prize 2026 Candidate                              ║")
    print("╚" + "═" * 58 + "╝")

    scenarios = [
        {
            "name": "01_nominal_operation",
            "state": {
                "p_pv": 42.5,
                "p_battery": -8.3,
                "p_grid": 12.1,
                "p_load": 46.3,
                "soc": 0.72,
                "voltage": 233.5,
                "frequency": 50.02,
                "cbf_active": False,
                "is_safe": True,
                "barrier_value": 38.7,
                "safety_margin": 6.5,
                "irradiance": 920,
            },
        },
        {
            "name": "02_cbf_intervention",
            "state": {
                "p_pv": 52.0,
                "p_battery": 10.5,
                "p_grid": -18.5,
                "p_load": 24.0,
                "soc": 0.88,
                "voltage": 239.2,
                "frequency": 50.18,
                "cbf_active": True,
                "is_safe": True,
                "barrier_value": 2.8,
                "safety_margin": 0.8,
                "irradiance": 1050,
            },
        },
        {
            "name": "03_constraint_violation",
            "state": {
                "p_pv": 55.0,
                "p_battery": 15.0,
                "p_grid": -25.0,
                "p_load": 15.0,
                "soc": 0.95,
                "voltage": 244.0,
                "frequency": 50.35,
                "cbf_active": True,
                "is_safe": False,
                "barrier_value": -4.2,
                "safety_margin": -4.0,
                "irradiance": 1100,
            },
        },
        {
            "name": "04_night_operation",
            "state": {
                "p_pv": 0.0,
                "p_battery": -22.0,
                "p_grid": 0.0,
                "p_load": 22.0,
                "soc": 0.45,
                "voltage": 228.5,
                "frequency": 49.98,
                "cbf_active": False,
                "is_safe": True,
                "barrier_value": 48.5,
                "safety_margin": 11.5,
                "irradiance": 0,
            },
        },
        {
            "name": "05_low_battery_warning",
            "state": {
                "p_pv": 5.0,
                "p_battery": -15.0,
                "p_grid": 25.0,
                "p_load": 45.0,
                "soc": 0.12,
                "voltage": 226.0,
                "frequency": 49.92,
                "cbf_active": False,
                "is_safe": True,
                "barrier_value": 32.0,
                "safety_margin": 4.0,
                "irradiance": 120,
            },
        },
    ]

    for scenario in scenarios:
        print(f"\n→ Generating: {scenario['name']}.html")
        fig = create_microgrid_schematic(
            state=scenario["state"],
            show_animations=True,
            theme="dark",
            show_cbf_details=True,
            particle_density=14,
        )
        fig.write_html(
            f"schematic_{scenario['name']}.html",
            include_plotlyjs="cdn",
            full_html=True,
        )

    print("\n" + "═" * 60)
    print("  ✓ All visualizations generated successfully!")
    print("  Open HTML files and click '▶ LIVE' to see animations!")
    print("═" * 60)