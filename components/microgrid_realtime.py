"""
Microgrid Digital Twin - Scientific Light Edition
=================================================

Clean, modern scientific theme with animated energy flows using pure HTML/CSS.
No Plotly - uses CSS animations for smooth real-time updates.

Fix (Dec 2025):
- Restores missing/broken vertical "energy flow" animations by porting the
  working conduit logic from microgrid_realtime.py:
  .fiber-conduit + .energy-flow + .particles + @keyframes

Constraint honored:
- Keeps the existing "Scientific Light Premium" card/bus aesthetic unchanged.
- Only replaces the connecting wires/animations.

Author: Oussama AKIR
Date: December 2025
"""

import streamlit as st
from typing import Dict, Optional, Any

# Version for cache invalidation
NEON_SCHEMATIC_VERSION = "1.2.0"


def inject_neon_styles():
    """
    Optional: Inject styles into Streamlit DOM (NOT used by components.html iframe).
    Kept for compatibility; the actual rendering uses inline CSS inside the iframe.
    """
    st.markdown(
        """
    <style>
        /* (Optional global styles; iframe uses its own CSS) */
    </style>
    """,
        unsafe_allow_html=True,
    )


def get_solar_svg(power: float) -> str:
    """Generate Solar Panel SVG icon."""
    active = power > 0.5
    color = "#f59e0b" if active else "#94a3b8"
    glow = "filter: drop-shadow(0 0 4px rgba(245, 158, 11, 0.5));" if active else ""

    return f"""
    <svg viewBox="0 0 100 100" width="90" height="90" fill="none" style="{glow}" xmlns="http://www.w3.org/2000/svg">
        {"<circle cx='82' cy='18' r='10' fill='#F1C40F' />" if active else ""}
        <path d="M40 85 L35 95 H65 L60 85" fill="none" stroke="#555555" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="50" y1="65" x2="50" y2="85" stroke="#555555" stroke-width="3" />
        <rect x="10" y="30" width="80" height="50" rx="4" ry="4" fill="#7F8C8D" stroke="{color}" stroke-width="2"/>
        <rect x="13" y="33" width="74" height="44" rx="1" ry="1" fill="#0056b3" />
        <line x1="13" y1="55" x2="87" y2="55" stroke="#4da6ff" stroke-width="1" />
        <line x1="37.6" y1="33" x2="37.6" y2="77" stroke="#4da6ff" stroke-width="1" />
        <line x1="62.3" y1="33" x2="62.3" y2="77" stroke="#4da6ff" stroke-width="1" />
        <path d="M13 77 L40 33 L55 33 L28 77 Z" fill="white" fill-opacity="0.15" />
    </svg>
    """


def get_battery_svg(soc: float, charging: bool) -> str:
    """Generate Battery SVG icon with fill level."""
    if soc > 0.6:
        color = "#22c55e"
    elif soc > 0.3:
        color = "#eab308"
    else:
        color = "#ef4444"

    fill_width = max(2, soc * 76)
    glow = f"filter: drop-shadow(0 0 4px {color});"
    bolt_opacity = "1" if charging else "0"

    return f"""
    <svg viewBox="0 0 100 50" width="100" height="50" fill="none" style="{glow}">
        <rect x="5" y="10" width="80" height="30" rx="4" fill="#f8fafc" stroke="{color}" stroke-width="2"/>
        <rect x="85" y="17" width="8" height="16" rx="2" fill="{color}"/>
        <rect x="9" y="14" width="{fill_width}" height="22" rx="2" fill="{color}" opacity="0.8"/>
        <path d="M45 12 L38 25 H44 L42 38 L55 23 H48 L50 12 Z" fill="{color}" opacity="{bolt_opacity}"/>
    </svg>
    """


def get_cbf_svg(is_safe: bool, cbf_active: bool) -> str:
    """Generate U-CBF Shield SVG icon."""
    if not is_safe:
        color = "#ef4444"
        inner_color = "#fee2e2"
    elif cbf_active:
        color = "#f59e0b"
        inner_color = "#fef3c7"
    else:
        color = "#0ea5e9"
        inner_color = "#e0f2fe"

    glow = f"filter: drop-shadow(0 0 4px {color});"

    return f"""
    <svg viewBox="0 0 80 90" width="70" height="78" fill="none" style="{glow}">
        <path d="M40 5 L75 20 L75 50 C75 70 40 85 40 85 C40 85 5 70 5 50 L5 20 Z"
              fill="{inner_color}" stroke="{color}" stroke-width="2"/>
        <path d="M40 15 L65 27 L65 48 C65 62 40 75 40 75 C40 75 15 62 15 48 L15 27 Z"
              fill="{color}" opacity="0.2"/>
        <text x="40" y="52" text-anchor="middle" fill="{color}" font-size="18" font-weight="bold"
              font-family="monospace">CBF</text>
    </svg>
    """


def get_load_svg(power: float) -> str:
    """Generate Load/House SVG icon."""
    active = power > 0.5
    color = "#ef4444" if active else "#94a3b8"
    glow = "filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.4));" if active else ""

    return f"""
    <svg viewBox="0 0 90 80" width="80" height="71" fill="none" style="{glow}">
        <path d="M45 5 L85 35 L85 75 L5 75 L5 35 Z" fill="#f8fafc" stroke="{color}" stroke-width="2"/>
        <rect x="35" y="45" width="20" height="30" fill="{color}" opacity="0.2"/>
        <rect x="15" y="45" width="15" height="12" fill="{color}" opacity="0.3"/>
        <rect x="60" y="45" width="15" height="12" fill="{color}" opacity="0.3"/>
        {"<circle cx='45' cy='55' r='4' fill='#fbbf24'/>" if active else ""}
    </svg>
    """


def get_grid_svg(importing: bool, power: float) -> str:
    """Generate Grid/Transmission Tower SVG icon."""
    active = abs(power) > 0.5
    color = "#3b82f6" if importing else "#8b5cf6"
    if not active:
        color = "#94a3b8"
    glow = f"filter: drop-shadow(0 0 4px {color});" if active else ""

    return f"""
    <svg viewBox="0 0 80 90" width="70" height="78" fill="none" style="{glow}">
        <path d="M40 5 L55 25 L50 25 L55 45 L48 45 L55 85 L25 85 L32 45 L25 45 L30 25 L25 25 Z"
              fill="#f8fafc" stroke="{color}" stroke-width="2"/>
        <line x1="25" y1="65" x2="55" y2="65" stroke="{color}" stroke-width="1.5"/>
        <line x1="28" y1="50" x2="52" y2="50" stroke="{color}" stroke-width="1.5"/>
        <line x1="32" y1="35" x2="48" y2="35" stroke="{color}" stroke-width="1.5"/>
        <circle cx="40" cy="15" r="6" fill="{color}" opacity="0.8"/>
    </svg>
    """


def render_neon_microgrid(state: Optional[Dict[str, Any]] = None) -> None:
    """
    Render the neon-style microgrid digital twin.

    Args:
        state: Dictionary with system state values
    """
    import streamlit.components.v1 as components

    if state is None:
        state = {}

    # Extract values with defaults
    p_pv = float(state.get("p_pv", 25.0))
    p_battery = float(state.get("p_battery", -5.0))
    p_grid = float(state.get("p_grid", 10.0))
    p_load = float(state.get("p_load", 30.0))
    soc = float(state.get("soc", 0.65))
    voltage = float(state.get("voltage", 230.0))
    frequency = float(state.get("frequency", 50.0))
    cbf_active = bool(state.get("cbf_active", False))
    is_safe = bool(state.get("is_safe", True))
    barrier_value = float(state.get("barrier_value", 0.05))

    # Derived states
    is_charging = p_battery > 0.0
    is_importing = p_grid > 0.0
    net_power = p_pv + p_battery + p_grid - p_load

    # Activity flags
    pv_active = p_pv > 0.5
    load_active = p_load > 0.5
    batt_active = abs(p_battery) > 0.5
    grid_active = abs(p_grid) > 0.5
    cbf_link_active = cbf_active or (not is_safe)

    # Status colors
    pv_status = ("GENERATING", "#22c55e") if pv_active else ("OFFLINE", "#94a3b8")

    if is_charging and batt_active:
        batt_status = ("CHARGING", "#22c55e")
    elif p_battery < -0.5:
        batt_status = ("DISCHARGING", "#ef4444")
    else:
        batt_status = ("STANDBY", "#94a3b8")

    if not is_safe:
        cbf_status = ("VIOLATION!", "#ef4444")
        cbf_class = "danger"
    elif cbf_active:
        cbf_status = ("ACTIVE", "#f59e0b")
        cbf_class = "warning"
    else:
        cbf_status = ("NOMINAL", "#22c55e")
        cbf_class = "active"

    load_status = ("CONSUMING", "#ef4444") if load_active else ("IDLE", "#94a3b8")
    grid_status = ("IMPORTING", "#3b82f6") if is_importing else ("EXPORTING", "#8b5cf6")

    # ─────────────────────────────────────────────────────────────────────────
    # Fiber conduit generator (ported from microgrid_realtime.py logic)
    # - Uses .fiber-conduit .energy-flow .particles .particle + keyframes
    # - Direction: flow-down / flow-up
    # - Speed + intensity: react to power magnitude
    # ─────────────────────────────────────────────────────────────────────────
    particle_spans = "".join('<span class="particle"></span>' for _ in range(6))

    def conduit_html(
        active: bool,
        direction: str,
        color: str,
        power_kw: float,
        max_kw: float = 30.0,
        idle_opacity: float = 0.55,
    ) -> str:
        mag = abs(power_kw)
        intensity = min(1.0, mag / max_kw) if active else 0.0
        # Higher intensity => faster (shorter duration)
        speed = max(0.55, 1.80 - 1.05 * intensity)

        cls = "fiber-conduit"
        if active:
            cls += f" flowing {direction}"

        return f"""
            <div class="{cls}"
                 style="--flow-color: {color};
                        --flow-speed: {speed:.2f}s;
                        --flow-intensity: {intensity:.3f};
                        --idle-opacity: {idle_opacity};">
                <div class="energy-flow"></div>
                <div class="particles">{particle_spans}</div>
            </div>
        """

    # CBF "link" is conceptual; give it a pseudo power to scale intensity
    cbf_pseudo_power = 10.0 if (not is_safe) else (6.0 if cbf_active else 0.0)

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Rajdhani', sans-serif;
            overflow-x: hidden;
            overflow-y: auto;
            height: auto;
            min-height: 100%;
        }}

        .microgrid-container {{
            background: transparent;
            border-radius: 0;
            padding: 10px 8px;
            margin: 0;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            gap: 8px;
        }}

        .microgrid-title {{
            text-align: center;
            color: #0f172a;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 6px 0;
            background: linear-gradient(90deg, transparent, rgba(14,165,233,0.08), transparent);
            border-radius: 4px;
        }}

        .microgrid-subtitle {{
            text-align: center;
            color: #475569;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            padding: 0 0 4px 0;
            text-transform: uppercase;
        }}

        .microgrid-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            align-items: center;
            padding: 0 5px;
        }}

        .microgrid-row-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
            align-items: center;
            padding: 0 5px;
        }}

        /* Cards (unchanged aesthetic) */
        .neon-card {{
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 10px 8px;
            text-align: center;
            transition: all 0.3s ease;
            min-height: 130px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}

        .neon-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--card-color, #0ea5e9), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .neon-card.active::before {{
            opacity: 1;
        }}

        .neon-card.active {{
            border-color: var(--card-color, #0ea5e9);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                        0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        .neon-card.warning {{
            --card-color: #f59e0b;
            border-color: #fcd34d;
        }}

        .neon-card.danger {{
            --card-color: #ef4444;
            border-color: #fca5a5;
            animation: dangerPulse 1s ease-in-out infinite;
        }}

        @keyframes dangerPulse {{
            0%, 100% {{ border-color: #fca5a5; box-shadow: 0 0 0 rgba(239, 68, 68, 0); }}
            50% {{ border-color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }}
        }}

        .card-label {{
            font-family: 'Rajdhani', sans-serif;
            color: #64748b;
            font-size: 0.7rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .card-icon {{
            margin: 5px 0;
        }}

        .card-value {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.6rem;
            font-weight: bold;
            color: #1e293b;
            margin-top: 5px;
        }}

        .card-unit {{
            font-size: 0.8rem;
            color: #64748b;
            font-family: 'Rajdhani', sans-serif;
            font-weight: normal;
        }}

        .status-badge {{
            margin-top: 8px;
            font-size: 0.6rem;
            padding: 3px 8px;
            border-radius: 4px;
            background: #f1f5f9;
            font-family: 'Rajdhani', sans-serif;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border: 1px solid #e2e8f0;
            color: #475569;
            font-weight: 600;
        }}

        /* Layout container for conduits */
        .pipe-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-height: 30px;
        }}

        /* ═══════════════════════════════════════════════════════════════════════
           FIBER CONDUITS (ported from microgrid_realtime.py)
           Replaces broken/static .pipe-vertical implementation
           ═══════════════════════════════════════════════════════════════════════ */
        .fiber-conduit {{
            width: 10px;
            height: 100%;
            position: relative;
            margin: 0 auto;
            border-radius: 999px;
            overflow: hidden;
            background: linear-gradient(180deg, #e2e8f0, #cbd5e1);
            box-shadow:
                inset 0 0 0 1px rgba(148, 163, 184, 0.85),
                0 1px 2px rgba(15, 23, 42, 0.08);
            opacity: var(--idle-opacity, 0.55);
            contain: layout style paint;
        }}

        .fiber-conduit::before {{
            content: "";
            position: absolute;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
            width: 2px;
            height: 100%;
            background: linear-gradient(180deg, rgba(15,23,42,0.18), rgba(15,23,42,0.04));
            opacity: 0.9;
        }}

        .fiber-conduit.flowing {{
            opacity: 1;
        }}

        .fiber-conduit .energy-flow {{
            position: absolute;
            left: 0;
            right: 0;
            top: -65%;
            height: 65%;
            border-radius: inherit;
            background: linear-gradient(
                180deg,
                transparent 0%,
                rgba(255,255,255,0.35) 18%,
                var(--flow-color, #0ea5e9) 55%,
                rgba(255,255,255,0.35) 82%,
                transparent 100%
            );
            opacity: 0;
            filter: drop-shadow(0 0 calc(10px * var(--flow-intensity, 0)) var(--flow-color, #0ea5e9));
            will-change: transform, opacity;
        }}

        .fiber-conduit:not(.flowing) .energy-flow {{
            opacity: 0;
        }}

        .fiber-conduit.flowing .energy-flow {{
            opacity: calc(0.20 + 0.80 * var(--flow-intensity, 0.0));
        }}

        .fiber-conduit.flowing.flow-down .energy-flow {{
            animation: fiber-flow-down var(--flow-speed, 1.2s) linear infinite;
        }}

        .fiber-conduit.flowing.flow-up .energy-flow {{
            animation: fiber-flow-up var(--flow-speed, 1.2s) linear infinite;
        }}

        @keyframes fiber-flow-down {{
            0%   {{ transform: translateY(0); }}
            100% {{ transform: translateY(260%); }}
        }}

        @keyframes fiber-flow-up {{
            0%   {{ transform: translateY(260%); }}
            100% {{ transform: translateY(0); }}
        }}

        .fiber-conduit .particles {{
            position: absolute;
            inset: 0;
            pointer-events: none;
        }}

        .fiber-conduit .particle {{
            position: absolute;
            top: -12%;
            left: 50%;
            transform: translateX(-50%);
            width: 3px;
            height: 3px;
            border-radius: 999px;
            background: rgba(255,255,255,0.85);
            box-shadow: 0 0 8px var(--flow-color, #0ea5e9);
            opacity: 0;
            will-change: top, opacity;
        }}

        .fiber-conduit:not(.flowing) .particle {{
            opacity: 0;
            animation: none !important;
        }}

        .fiber-conduit.flowing.flow-down .particle {{
            animation: particle-down var(--flow-speed, 1.2s) linear infinite;
        }}

        .fiber-conduit.flowing.flow-up .particle {{
            animation: particle-up var(--flow-speed, 1.2s) linear infinite;
        }}

        @keyframes particle-down {{
            0%   {{ top: -12%; opacity: 0; }}
            10%  {{ opacity: calc(0.25 + 0.75 * var(--flow-intensity, 0.0)); }}
            90%  {{ opacity: calc(0.25 + 0.75 * var(--flow-intensity, 0.0)); }}
            100% {{ top: 112%; opacity: 0; }}
        }}

        @keyframes particle-up {{
            0%   {{ top: 112%; opacity: 0; }}
            10%  {{ opacity: calc(0.25 + 0.75 * var(--flow-intensity, 0.0)); }}
            90%  {{ opacity: calc(0.25 + 0.75 * var(--flow-intensity, 0.0)); }}
            100% {{ top: -12%; opacity: 0; }}
        }}

        .fiber-conduit .particle:nth-child(1) {{ left: 45%; animation-delay: 0s; }}
        .fiber-conduit .particle:nth-child(2) {{ left: 55%; animation-delay: 0.15s; }}
        .fiber-conduit .particle:nth-child(3) {{ left: 48%; animation-delay: 0.30s; }}
        .fiber-conduit .particle:nth-child(4) {{ left: 52%; animation-delay: 0.45s; }}
        .fiber-conduit .particle:nth-child(5) {{ left: 46%; animation-delay: 0.60s; }}
        .fiber-conduit .particle:nth-child(6) {{ left: 54%; animation-delay: 0.75s; }}

        /* AC Bus (unchanged) */
        .ac-bus {{
            width: 100%;
            height: 70px;
            margin: 4px 0;
            position: relative;
            z-index: 10;
            display: flex;
            justify-content: center;
            align-items: center;
            contain: layout style paint;
            background: transparent;
            box-shadow: none;
            border: none;
            overflow: visible;
        }}

        .ac-bus svg {{
            width: 100%;
            height: 100%;
            max-width: none;
            will-change: auto;
        }}

        @keyframes acbus-energy-flow {{
            from {{ stroke-dashoffset: 0; }}
            to {{ stroke-dashoffset: -160; }}
        }}

        @keyframes acbus-sparkle {{
            0%, 100% {{ opacity: 0.2; }}
            50% {{ opacity: 1; }}
        }}

        @keyframes acbus-led-pulse {{
            0%, 100% {{ opacity: 0.85; }}
            50% {{ opacity: 1; }}
        }}

        .ac-bus .energy-flow {{
            animation: acbus-energy-flow 2.5s linear infinite;
            will-change: stroke-dashoffset;
        }}

        .ac-bus .sparkle {{
            animation: acbus-sparkle 2s ease-in-out infinite;
        }}

        .ac-bus .acbus-led {{
            animation: acbus-led-pulse 2s ease-in-out infinite;
            transition: fill 0.3s ease;
        }}

        /* Status Bar (unchanged) */
        .status-bar {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 6px;
            padding: 6px 10px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}

        .status-item {{
            text-align: center;
        }}

        .status-item-label {{
            font-size: 0.6rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 2px;
        }}

        .status-item-value {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 1rem;
            font-weight: bold;
            color: #1e293b;
        }}

        /* ═══════════════════════════════════════════════════════════════════
           SMOOTH VALUE TRANSITIONS (for real-time updates without flicker)
           ═══════════════════════════════════════════════════════════════════ */
        .smooth-transition {{
            transition: all 0.4s ease-out;
        }}
        .card-value, .status-item-value, .status-badge {{
            transition: color 0.3s ease, opacity 0.3s ease;
        }}
    </style>
    </head>
    <body>
    <div class="microgrid-container">
        <div class="microgrid-title">Microgrid Digital Twin</div>
        <div class="microgrid-subtitle">U-CBF Safety-Certified Energy Management System</div>

        <!-- Row 1 -->
        <div class="microgrid-grid">
            <div class="neon-card {'active' if pv_active else ''}" style="--card-color: #f59e0b;">
                <div class="card-label">Solar PV</div>
                <div class="card-icon">{get_solar_svg(p_pv)}</div>
                <div class="card-value">{p_pv:.1f} <span class="card-unit">kW</span></div>
                <div class="status-badge" style="color: {pv_status[1]}">{pv_status[0]}</div>
            </div>

            <div class="neon-card {cbf_class}" style="--card-color: {'#ef4444' if not is_safe else '#0ea5e9'};">
                <div class="card-label">U-CBF Filter</div>
                <div class="card-icon">{get_cbf_svg(is_safe, cbf_active)}</div>
                <div class="card-value" style="font-size: 1.5rem;">h = {barrier_value:.3f}</div>
                <div class="status-badge" style="color: {cbf_status[1]}">{cbf_status[0]}</div>
            </div>

            <div class="neon-card {'active' if load_active else ''}" style="--card-color: #ef4444;">
                <div class="card-label">Load</div>
                <div class="card-icon">{get_load_svg(p_load)}</div>
                <div class="card-value">{p_load:.1f} <span class="card-unit">kW</span></div>
                <div class="status-badge" style="color: {load_status[1]}">{load_status[0]}</div>
            </div>
        </div>

        <!-- Vertical Connections (Top -> Bus) -->
        <div class="microgrid-grid" style="grid-template-rows: 40px; gap: 0; min-height: 40px; margin-top: -5px; margin-bottom: -5px;">
            <div class="pipe-container" style="min-height: 40px;">
                {conduit_html(pv_active, "flow-down", "#f59e0b", p_pv)}
            </div>

            <div class="pipe-container" style="min-height: 40px;">
                {conduit_html(
                    cbf_link_active,
                    "flow-down",
                    ("#ef4444" if not is_safe else "#0ea5e9"),
                    cbf_pseudo_power,
                    max_kw=10.0,
                    idle_opacity=(0.35 if not cbf_link_active else 0.55)
                )}
            </div>

            <div class="pipe-container" style="min-height: 40px;">
                {conduit_html(load_active, "flow-up", "#ef4444", p_load)}
            </div>
        </div>

        <!-- AC Bus (unchanged) -->
        <div class="ac-bus">
            <svg viewBox="0 0 1600 120" fill="none" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <filter id="acbus-glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="blur"/>
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                    <linearGradient id="acbus-cable" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stop-color="#1e293b"/>
                        <stop offset="50%" stop-color="#475569"/>
                        <stop offset="100%" stop-color="#1e293b"/>
                    </linearGradient>
                    <linearGradient id="acbus-energy" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stop-color="#0ea5e9"/>
                        <stop offset="50%" stop-color="#e0f2fe"/>
                        <stop offset="100%" stop-color="#0ea5e9"/>
                    </linearGradient>
                    <linearGradient id="acbus-box-grad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#1e293b"/>
                        <stop offset="100%" stop-color="#0f172a"/>
                    </linearGradient>
                    <path id="bus-path" d="M 0 60 H 1600"/>
                </defs>

                <use href="#bus-path" stroke="url(#acbus-cable)" stroke-width="32" stroke-linecap="round"/>
                <use href="#bus-path" stroke="#0f172a" stroke-width="36" stroke-linecap="round" opacity="0.3"/>
                <use href="#bus-path" stroke="#38bdf8" stroke-width="1" opacity="0.4" transform="translate(0,-8)"/>
                <use href="#bus-path" stroke="#38bdf8" stroke-width="1" opacity="0.4" transform="translate(0,8)"/>

                <use href="#bus-path" class="energy-flow" stroke="url(#acbus-energy)" stroke-width="4" filter="url(#acbus-glow)" stroke-dasharray="80 80"/>
                <use href="#bus-path" class="energy-flow" stroke="#ffffff" stroke-width="2" opacity="0.6" stroke-dasharray="20 140"/>

                <circle class="sparkle" cx="400" cy="60" r="2" fill="#38bdf8" style="animation-delay:0s"/>
                <circle class="sparkle" cx="800" cy="40" r="2.5" fill="#38bdf8" style="animation-delay:0.7s"/>
                <circle class="sparkle" cx="1200" cy="60" r="2" fill="#38bdf8" style="animation-delay:1.4s"/>

                <g transform="translate(800, 60)">
                    <rect x="-90" y="-26" width="180" height="52" rx="12" fill="#0f172a" stroke="#334155" stroke-width="2" filter="url(#acbus-glow)"/>
                    <rect x="-85" y="-21" width="170" height="42" rx="8" fill="url(#acbus-box-grad)" stroke="#1e293b"/>

                    <circle class="acbus-led" cx="-70" cy="0" r="4" fill="#22c55e" filter="url(#acbus-glow)"/>
                    <circle class="acbus-led" cx="70" cy="0" r="4" fill="#22c55e" filter="url(#acbus-glow)"/>

                    <text x="0" y="-4" text-anchor="middle" fill="#e2e8f0" font-family="monospace" font-size="12" font-weight="900" letter-spacing="2">◆ AC BUS ◆</text>
                    <line x1="-55" y1="4" x2="55" y2="4" stroke="#0ea5e9" stroke-width="1" opacity="0.5"/>
                    <text x="0" y="16" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="11" font-weight="bold">
                        {voltage:.0f}V | {frequency:.1f}Hz
                    </text>
                </g>

                <circle cx="40" cy="60" r="6" fill="#475569" stroke="#1e293b"/>
                <circle cx="40" cy="60" r="3" fill="#38bdf8"/>
                <circle cx="1560" cy="60" r="6" fill="#475569" stroke="#1e293b"/>
                <circle cx="1560" cy="60" r="3" fill="#38bdf8"/>
            </svg>
        </div>

        <!-- Vertical Connections (Bus -> Bottom) -->
        <div class="microgrid-row-2" style="grid-template-rows: 40px; gap: 0; min-height: 40px; margin-top: -5px; margin-bottom: -5px;">
            <div></div>

            <div class="pipe-container" style="min-height: 40px;">
                {conduit_html(
                    batt_active,
                    ("flow-down" if is_charging else "flow-up"),
                    ("#22c55e" if is_charging else "#3b82f6"),
                    p_battery
                )}
            </div>

            <div></div>

            <div class="pipe-container" style="min-height: 40px;">
                {conduit_html(
                    grid_active,
                    ("flow-up" if is_importing else "flow-down"),
                    ("#3b82f6" if is_importing else "#8b5cf6"),
                    p_grid
                )}
            </div>

            <div></div>
        </div>

        <!-- Row 2 -->
        <div class="microgrid-row-2">
            <div></div>

            <div class="neon-card {'active' if batt_active else ''}"
                 style="--card-color: {'#22c55e' if is_charging else '#3b82f6'};">
                <div class="card-label">Battery</div>
                <div class="card-icon">{get_battery_svg(soc, is_charging)}</div>
                <div class="card-value">{soc*100:.0f} <span class="card-unit">%</span></div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">
                    {'+' if p_battery > 0 else ''}{p_battery:.1f} kW
                </div>
                <div class="status-badge" style="color: {batt_status[1]}">{batt_status[0]}</div>
            </div>

            <div></div>

            <div class="neon-card {'active' if grid_active else ''}"
                 style="--card-color: {'#3b82f6' if is_importing else '#8b5cf6'};">
                <div class="card-label">Utility Grid</div>
                <div class="card-icon">{get_grid_svg(is_importing, p_grid)}</div>
                <div class="card-value">{abs(p_grid):.1f} <span class="card-unit">kW</span></div>
                <div class="status-badge" style="color: {'#3b82f6' if is_importing else '#8b5cf6'}">{grid_status[0]}</div>
            </div>

            <div></div>
        </div>

        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <div class="status-item-label">System</div>
                <div class="status-item-value" style="color: {'#22c55e' if is_safe else '#ef4444'};">
                    {'✓ SAFE' if is_safe else '⚠ ALERT'}
                </div>
            </div>
            <div class="status-item">
                <div class="status-item-label">Net Power</div>
                <div class="status-item-value" style="color: {'#22c55e' if net_power >= 0 else '#ef4444'};">
                    {'+' if net_power >= 0 else ''}{net_power:.1f} kW
                </div>
            </div>
            <div class="status-item">
                <div class="status-item-label">Barrier</div>
                <div class="status-item-value" style="color: {'#22c55e' if barrier_value > 0 else '#ef4444'};">
                    h = {barrier_value:.4f}
                </div>
            </div>
            <div class="status-item">
                <div class="status-item-label">Voltage</div>
                <div class="status-item-value" style="color: #0ea5e9;">{voltage:.1f}V</div>
            </div>
            <div class="status-item">
                <div class="status-item-label">Frequency</div>
                <div class="status-item-value" style="color: #0ea5e9;">{frequency:.2f}Hz</div>
            </div>
        </div>

    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         JAVASCRIPT: Real-time value updates via polling
         Updates values smoothly without recreating the iframe
         ═══════════════════════════════════════════════════════════════════════ -->
    <script>
        // Store current state for comparison
        let currentState = {{
            p_pv: {p_pv},
            p_battery: {p_battery},
            p_grid: {p_grid},
            p_load: {p_load},
            soc: {soc},
            voltage: {voltage},
            frequency: {frequency},
            cbf_active: {'true' if cbf_active else 'false'},
            is_safe: {'true' if is_safe else 'false'},
            barrier_value: {barrier_value}
        }};

        // Listen for state updates from Streamlit
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'stateUpdate') {{
                updateValues(event.data.state);
            }}
        }});

        function updateValues(state) {{
            // This function would update DOM elements if IDs were present
            // For now, the initial render shows current values
            currentState = state;
        }}
    </script>
    </body>
    </html>
    """

    components.html(full_html, height=580, scrolling=False)


# Quick test
if __name__ == "__main__":
    st.set_page_config(page_title="Neon Microgrid Test", layout="wide")

    test_state = {
        "p_pv": 25.0,
        "p_battery": 5.0,
        "p_grid": -10.0,
        "p_load": 20.0,
        "soc": 0.72,
        "voltage": 232.5,
        "frequency": 50.02,
        "cbf_active": False,
        "is_safe": True,
        "barrier_value": 0.045,
    }

    render_neon_microgrid(test_state)
