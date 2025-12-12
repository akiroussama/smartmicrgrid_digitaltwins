"""
Microgrid Digital Twin - Scientific Light Premium Edition
========================================================

Hyper-realistic scientific control-panel styling:
- Glassmorphism (true backdrop blur + border gradients)
- Tactile cards (hover lift + specular sweep)
- Optical-fiber conduits (glowing core + moving energy packets, GPU-friendly)
- Higher fidelity "schematic" SVG icons
- Responsive sizing inside Streamlit iframe

Author: (refactor) December 2025
"""

from __future__ import annotations
import math
from typing import Dict, Optional, Any
import streamlit as st
import streamlit.components.v1 as components

NEON_SCHEMATIC_VERSION = "2.0.0"


# ------------------------------ Helpers ------------------------------

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _flow_intensity(power_kw: float, max_kw: float = 40.0) -> float:
    """0..1 intensity used for glow/opacity/speed."""
    return _clamp01(abs(power_kw) / max_kw)


def _flow_duration(intensity: float) -> float:
    """
    Duration (seconds). Higher intensity => faster.
    Keep in a comfortable range for 60fps GPU animations.
    """
    # 2.2s (low) -> 0.9s (high)
    return 2.2 - 1.3 * _clamp01(intensity)


def _fmt_signed(x: float, digits: int = 1) -> str:
    s = f"{x:.{digits}f}"
    return f"+{s}" if x >= 0 else s


# ------------------------------ Premium SVG Icons ------------------------------

def get_solar_svg_premium(power: float) -> str:
    active = power > 0.5
    accent = "#f59e0b"
    stroke = accent if active else "#94a3b8"
    sun_op = "1" if active else "0"
    glow = "filter: drop-shadow(0 10px 18px rgba(245,158,11,.22)) drop-shadow(0 0 10px rgba(245,158,11,.25));" if active else ""

    return f"""
<svg viewBox="0 0 120 120" width="86" height="86" xmlns="http://www.w3.org/2000/svg" style="{glow}">
  <defs>
    <linearGradient id="sp_frame" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e2e8f0"/>
      <stop offset="1" stop-color="#94a3b8"/>
    </linearGradient>
    <linearGradient id="sp_glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b3b76"/>
      <stop offset="1" stop-color="#1d6fe2"/>
    </linearGradient>
    <linearGradient id="sp_reflect" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="rgba(255,255,255,.55)"/>
      <stop offset="1" stop-color="rgba(255,255,255,0)"/>
    </linearGradient>
  </defs>

  <!-- Sun (subtle, premium) -->
  <g opacity="{sun_op}">
    <circle cx="94" cy="26" r="10" fill="#ffd166"/>
    <g stroke="#f59e0b" stroke-width="2" stroke-linecap="round" opacity="0.9">
      <line x1="94" y1="10" x2="94" y2="4"/>
      <line x1="94" y1="48" x2="94" y2="54"/>
      <line x1="78" y1="26" x2="72" y2="26"/>
      <line x1="110" y1="26" x2="116" y2="26"/>
      <line x1="83" y1="15" x2="79" y2="11"/>
      <line x1="105" y1="37" x2="109" y2="41"/>
      <line x1="83" y1="37" x2="79" y2="41"/>
      <line x1="105" y1="15" x2="109" y2="11"/>
    </g>
  </g>

  <!-- Mount -->
  <path d="M48 92 L44 108 H76 L72 92" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"/>
  <path d="M60 78 V92" stroke="#64748b" stroke-width="3" stroke-linecap="round"/>

  <!-- Panel -->
  <g>
    <rect x="16" y="32" width="88" height="52" rx="8" fill="url(#sp_frame)" opacity="0.95"/>
    <rect x="20" y="36" width="80" height="44" rx="6" fill="url(#sp_glass)" stroke="{stroke}" stroke-width="2"/>

    <!-- Cells -->
    <g opacity="0.9" stroke="rgba(224,242,254,.65)" stroke-width="1">
      <path d="M20 50 H100" />
      <path d="M20 64 H100" />
      <path d="M46.6 36 V80" />
      <path d="M73.3 36 V80" />
    </g>

    <!-- Specular reflection -->
    <path d="M22 78 L55 36 H72 L39 78 Z" fill="url(#sp_reflect)" opacity="0.22"/>
  </g>
</svg>
"""


def get_battery_svg_premium(soc: float, charging: bool) -> str:
    soc = _clamp01(soc)
    if soc > 0.6:
        accent = "#22c55e"
    elif soc > 0.3:
        accent = "#eab308"
    else:
        accent = "#ef4444"

    fill_w = 84 * soc
    bolt_op = "1" if charging else "0"

    glow = f"filter: drop-shadow(0 10px 18px rgba(2,6,23,.10)) drop-shadow(0 0 10px {accent}33);"

    return f"""
<svg viewBox="0 0 140 70" width="104" height="52" xmlns="http://www.w3.org/2000/svg" style="{glow}">
  <defs>
    <linearGradient id="bat_shell" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="rgba(255,255,255,.95)"/>
      <stop offset="1" stop-color="rgba(241,245,249,.92)"/>
    </linearGradient>
    <linearGradient id="bat_fill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}"/>
      <stop offset="1" stop-color="rgba(224,242,254,.95)"/>
    </linearGradient>
  </defs>

  <!-- Body -->
  <rect x="12" y="18" width="102" height="38" rx="10" fill="url(#bat_shell)" stroke="rgba(15,23,42,.22)" stroke-width="2"/>
  <!-- Terminal -->
  <rect x="114" y="30" width="14" height="14" rx="4" fill="rgba(148,163,184,.8)" stroke="rgba(15,23,42,.18)"/>

  <!-- Inner cavity -->
  <rect x="18" y="24" width="90" height="26" rx="7" fill="rgba(2,6,23,.05)" stroke="rgba(2,6,23,.06)"/>

  <!-- Fill -->
  <rect x="18" y="24" width="{fill_w:.2f}" height="26" rx="7" fill="{accent}" opacity="0.9"/>
  <rect x="18" y="24" width="{fill_w:.2f}" height="26" rx="7" fill="url(#bat_fill)" opacity="0.45"/>

  <!-- Tick marks -->
  <g stroke="rgba(2,6,23,.10)" stroke-width="1">
    <line x1="36" y1="24" x2="36" y2="50"/>
    <line x1="54" y1="24" x2="54" y2="50"/>
    <line x1="72" y1="24" x2="72" y2="50"/>
    <line x1="90" y1="24" x2="90" y2="50"/>
  </g>

  <!-- Charge bolt -->
  <path d="M70 20 L58 40 H68 L62 60 L84 36 H73 L80 20 Z"
        fill="{accent}" opacity="{bolt_op}"/>
</svg>
"""


def get_cbf_svg_premium(is_safe: bool, cbf_active: bool) -> str:
    if not is_safe:
        accent = "#ef4444"
        fill = "rgba(254,226,226,.92)"
    elif cbf_active:
        accent = "#f59e0b"
        fill = "rgba(254,243,199,.92)"
    else:
        accent = "#0ea5e9"
        fill = "rgba(224,242,254,.92)"

    glow = f"filter: drop-shadow(0 10px 18px rgba(2,6,23,.10)) drop-shadow(0 0 12px {accent}33);"

    return f"""
<svg viewBox="0 0 120 140" width="78" height="82" xmlns="http://www.w3.org/2000/svg" style="{glow}">
  <defs>
    <linearGradient id="shield_grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{fill}"/>
      <stop offset="1" stop-color="rgba(255,255,255,.75)"/>
    </linearGradient>
  </defs>

  <path d="M60 10 L108 30 V74 C108 104 60 128 60 128 C60 128 12 104 12 74 V30 Z"
        fill="url(#shield_grad)" stroke="{accent}" stroke-width="3" />

  <!-- Inner panel -->
  <path d="M60 26 L94 40 V72 C94 92 60 110 60 110 C60 110 26 92 26 72 V40 Z"
        fill="{accent}" opacity="0.10"/>

  <!-- Circuit lines -->
  <g stroke="{accent}" stroke-width="2" opacity="0.55" stroke-linecap="round">
    <path d="M46 54 H74"/>
    <path d="M46 86 H74"/>
  </g>

  <text x="60" y="78" text-anchor="middle"
        font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
        font-size="18" font-weight="900" fill="{accent}" letter-spacing="2">
    U‑CBF
  </text>
</svg>
"""


def get_load_svg_premium(power: float) -> str:
    active = power > 0.5
    accent = "#ef4444"
    stroke = accent if active else "#94a3b8"
    glow = "filter: drop-shadow(0 10px 18px rgba(239,68,68,.18)) drop-shadow(0 0 10px rgba(239,68,68,.20));" if active else ""

    return f"""
<svg viewBox="0 0 140 120" width="86" height="74" xmlns="http://www.w3.org/2000/svg" style="{glow}">
  <defs>
    <linearGradient id="home_shell" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="rgba(255,255,255,.95)"/>
      <stop offset="1" stop-color="rgba(241,245,249,.92)"/>
    </linearGradient>
  </defs>

  <!-- Roof -->
  <path d="M20 54 L70 18 L120 54" fill="none" stroke="{stroke}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- House body -->
  <rect x="30" y="54" width="80" height="50" rx="10" fill="url(#home_shell)" stroke="rgba(15,23,42,.22)" stroke-width="2"/>

  <!-- Door -->
  <rect x="64" y="70" width="16" height="34" rx="6" fill="{accent}" opacity="0.16"/>
  <circle cx="76" cy="88" r="2.5" fill="{accent}" opacity="{1 if active else 0}"/>

  <!-- Windows -->
  <g fill="{accent}" opacity="0.14">
    <rect x="40" y="68" width="16" height="14" rx="4"/>
    <rect x="84" y="68" width="16" height="14" rx="4"/>
  </g>

  <!-- Consumption indicator -->
  <g opacity="{1 if active else 0}">
    <path d="M18 90 C34 78, 50 102, 66 90" stroke="{accent}" stroke-width="3" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""


def get_grid_svg_premium(importing: bool, power: float) -> str:
    active = abs(power) > 0.5
    accent = "#3b82f6" if importing else "#8b5cf6"
    stroke = accent if active else "#94a3b8"
    glow = f"filter: drop-shadow(0 10px 18px rgba(2,6,23,.10)) drop-shadow(0 0 12px {accent}33);" if active else ""

    return f"""
<svg viewBox="0 0 140 160" width="76" height="86" xmlns="http://www.w3.org/2000/svg" style="{glow}">
  <defs>
    <linearGradient id="tower_metal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#94a3b8"/>
      <stop offset="0.5" stop-color="#e2e8f0"/>
      <stop offset="1" stop-color="#94a3b8"/>
    </linearGradient>
    <filter id="arc-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Detailed Lattice Tower -->
  <g stroke="url(#tower_metal)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <!-- Main Legs -->
    <path d="M45 148 L65 20 L85 148" stroke-width="2"/>
    
    <!-- Crossarms -->
    <path d="M35 50 H95 L65 20 Z" fill="rgba(203,213,225,0.1)"/> <!-- Top wire holder -->
    <path d="M25 75 H105 L115 75 M25 75 L15 75" /> <!-- Middle Arm -->
    <path d="M35 100 H95" /> <!-- Bottom Arm -->

    <!-- Lattice cross-bracing (Zig-zag) -->
    <path d="M50 120 L80 120 M48 135 L82 135" opacity="0.5"/>
    <path d="M47 130 L65 40 L83 130" opacity="0.3"/>
    
    <!-- Insulator Strings (Glassy) -->
    <g stroke="rgba(56,189,248,0.6)" stroke-width="2">
       <line x1="20" y1="75" x2="20" y2="95" />
       <line x1="110" y1="75" x2="110" y2="95" />
       
       <!-- Wire connection points -->
       <circle cx="20" cy="95" r="1.5" fill="white"/>
       <circle cx="110" cy="95" r="1.5" fill="white"/>
    </g>
  </g>

  <!-- Active Power Arcs (The "WOW" effect) -->
  <g opacity="{1 if active else 0}" filter="url(#arc-glow)">
    <!-- Electric Arcs between tower and air -->
    <path d="M20 95 Q 10 110, 20 125" stroke="{accent}" stroke-width="1.5" fill="none" class="dash" stroke-dasharray="4 2"/>
    <path d="M110 95 Q 120 110, 110 125" stroke="{accent}" stroke-width="1.5" fill="none" class="dash" stroke-dasharray="4 2"/>
    
    <!-- Central Glow Core -->
    <circle cx="65" cy="55" r="6" fill="{accent}" opacity="0.4">
       <animate attributeName="r" values="6;8;6" dur="3s" repeatCount="indefinite"/>
       <animate attributeName="opacity" values="0.4;0.1;0.4" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- Direction Indicator (Holographic Arrow) -->
  <g transform="translate(65, 110)" opacity="{0.9 if active else 0}">
     <path d="M0 -15 L-6 -5 H-2 V8 H2 V-5 H6 Z" fill="{accent}" stroke="white" stroke-width="0.5">
       <animateTransform attributeName="transform" type="translate" values="0 0; 0 -4; 0 0" dur="2s" repeatCount="indefinite"/>
     </path>
  </g>
</svg>
"""


# ------------------------------ Renderer ------------------------------

def render_neon_microgrid(state: Optional[Dict[str, Any]] = None) -> None:
    """
    Render the Scientific Light Premium microgrid digital twin.

    state keys:
      p_pv, p_battery, p_grid, p_load [kW]
      soc [0..1]
      voltage [V], frequency [Hz]
      cbf_active [bool], is_safe [bool], barrier_value [float]
    """
    state = state or {}

    p_pv = float(state.get("p_pv", 25.0))
    p_battery = float(state.get("p_battery", -5.0))   # + charging (bus->batt), - discharging (batt->bus)
    p_grid = float(state.get("p_grid", 10.0))         # + importing (grid->bus), - exporting (bus->grid)
    p_load = float(state.get("p_load", 30.0))
    soc = float(state.get("soc", 0.65))
    voltage = float(state.get("voltage", 230.0))
    frequency = float(state.get("frequency", 50.0))
    cbf_active = bool(state.get("cbf_active", False))
    is_safe = bool(state.get("is_safe", True))
    barrier_value = float(state.get("barrier_value", 0.05))

    is_charging = p_battery > 0.5
    is_discharging = p_battery < -0.5
    is_importing = p_grid > 0.5
    net_power = p_pv + p_battery + p_grid - p_load

    # Status labels
    pv_status = ("GENERATING", "#b45309") if p_pv > 0.5 else ("OFFLINE", "#64748b")

    if is_charging:
        batt_status = ("CHARGING", "#15803d")
    elif is_discharging:
        batt_status = ("DISCHARGING", "#b91c1c")
    else:
        batt_status = ("STANDBY", "#64748b")

    if not is_safe:
        cbf_status = ("VIOLATION", "#b91c1c")
        cbf_class = "danger"
    elif cbf_active:
        cbf_status = ("ACTIVE", "#b45309")
        cbf_class = "warning"
    else:
        cbf_status = ("NOMINAL", "#15803d")
        cbf_class = "ok"

    load_status = ("CONSUMING", "#b91c1c") if p_load > 0.5 else ("IDLE", "#64748b")
    grid_status = ("IMPORTING", "#1d4ed8") if is_importing else ("EXPORTING", "#6d28d9")

    # Flow variables (intensity + duration + activation)
    pv_i = _flow_intensity(p_pv)
    load_i = _flow_intensity(p_load)
    batt_i = _flow_intensity(p_battery)
    grid_i = _flow_intensity(p_grid)

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg0: #f6f8fc;
      --bg1: #eef2ff;
      --ink: #0f172a;
      --muted: #475569;

      --glass: rgba(255,255,255,.62);
      --glass-strong: rgba(255,255,255,.78);
      --stroke: rgba(15,23,42,.14);
      --stroke2: rgba(15,23,42,.08);

      --shadow-lg: 0 24px 60px rgba(2,6,23,.10);
      --shadow-md: 0 14px 30px rgba(2,6,23,.10);
      --shadow-sm: 0 10px 18px rgba(2,6,23,.08);

      --blue: #0ea5e9;
      --blue2: #38bdf8;

      --radius-xl: 26px;
      --radius-lg: 18px;
      --radius-md: 14px;
    }}

    * {{ box-sizing: border-box; }}
    html, body {{
      height: 100%;
      margin: 0;
      background: #f8fafc;
      overflow: hidden;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      color: var(--ink);
    }}

    /* Stage background: subtle scientific grid + vignette + noise */
    .stage {{
      height: 100vh;
      width: 100%;
      display: grid;
      place-items: center;
      background: #f8fafc; /* MATCH DASHBOARD BACKGROUND */
      position: relative;
    }}
    .stage::before {{
      content: "";
      position: absolute; inset: 0;
      background: #f8fafc;
      opacity: 0;
      pointer-events: none;
      transform: translateZ(0);
    }}
    .stage::after {{
      content: "";
      position: absolute; inset: 0;
      background: #f8fafc;
      pointer-events: none;
    }}

    /* Main HUD panel */
    .hud {{
      width: 100%;
      height: 100vh;
      background: #f8fafc;
      backdrop-filter: none;
      -webkit-backdrop-filter: none;
      position: relative;
      overflow: hidden;
    }}

    /* Subtle inner highlight */
    .hud::before {{
      content: "";
      position: absolute; inset: 0;
      background: #f8fafc;
      pointer-events: none;
      opacity: 0;
    }}

    .hud-inner {{
      height: 100%;
      padding: clamp(14px, 2.2vw, 24px);
      display: flex;
      flex-direction: column;
      gap: clamp(10px, 1.4vw, 16px);
      position: relative;
    }}

    .header {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
    }}
    .title-block {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .title {{
      font-family: Orbitron, Inter, system-ui, sans-serif;
      letter-spacing: .22em;
      text-transform: uppercase;
      font-size: clamp(14px, 1.7vw, 20px);
      font-weight: 700;
      color: #0b1220;
    }}
    .subtitle {{
      font-size: 12px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: rgba(71,85,105,.92);
    }}

    .meta {{
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.58);
      border: 1px solid var(--stroke2);
      box-shadow: 0 10px 18px rgba(2,6,23,.06);
      backdrop-filter: blur(14px) saturate(160%);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      font-size: 12px;
      color: rgba(15,23,42,.82);
      font-family: "JetBrains Mono", ui-monospace, monospace;
    }}
    .dot {{
      width: 8px; height: 8px; border-radius: 999px;
      background: var(--blue);
      box-shadow: 0 0 0 4px rgba(14,165,233,.15), 0 0 16px rgba(14,165,233,.22);
    }}

    /* Layout grids */
    .grid-top {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: clamp(10px, 1.6vw, 18px);
      align-items: stretch;
    }}

    .grid-bot {{
      display: grid;
      grid-template-columns: 1fr 1.1fr 1fr 1.1fr 1fr;
      gap: clamp(8px, 1.2vw, 14px);
      align-items: stretch;
    }}

    /* Premium glass cards with gradient border */
    .card {{
      --accent: var(--blue);
      --accent-soft: rgba(14,165,233,.16);

      position: relative;
      z-index: 5;
      border-radius: var(--radius-lg);
      min-height: 160px;
      padding: 14px 14px 12px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.78), rgba(255,255,255,.54)) padding-box,
        linear-gradient(180deg, rgba(14,165,233,.35), rgba(15,23,42,.10)) border-box;
      border: 1px solid transparent;
      box-shadow: var(--shadow-md);
      backdrop-filter: blur(16px) saturate(160%);
      -webkit-backdrop-filter: blur(16px) saturate(160%);
      overflow: hidden;
      transform: translateZ(0);
      transition: transform .22s ease, box-shadow .22s ease, filter .22s ease;
    }}

    /* Inner glow and accent beam */
    .card::before {{
      content: "";
      position: absolute; inset: 0;
      background:
        radial-gradient(420px 180px at 50% 0%, rgba(255,255,255,.75), transparent 62%),
        radial-gradient(300px 160px at 20% 20%, var(--accent-soft), transparent 70%);
      opacity: .9;
      pointer-events: none;
    }}
    .card::after {{
      /* specular sweep on hover */
      content: "";
      position: absolute;
      top: -40%;
      left: -70%;
      width: 80%;
      height: 220%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent);
      transform: rotate(18deg) translate3d(0,0,0);
      opacity: 0;
      pointer-events: none;
      transition: opacity .25s ease, transform .45s ease;
    }}

    .card:hover {{
      transform: translateY(-2px) scale(1.01);
      box-shadow: 0 26px 60px rgba(2,6,23,.14);
    }}
    .card:hover::after {{
      opacity: 1;
      transform: rotate(18deg) translate3d(140%,0,0);
    }}

    .card.active {{
      filter: saturate(1.08);
    }}

    .card.danger {{
      --accent: #ef4444;
      --accent-soft: rgba(239,68,68,.16);
      animation: dangerPulse 1.15s ease-in-out infinite;
    }}
    .card.warning {{
      --accent: #f59e0b;
      --accent-soft: rgba(245,158,11,.16);
    }}
    .card.ok {{
      --accent: #22c55e;
      --accent-soft: rgba(34,197,94,.14);
    }}

    @keyframes dangerPulse {{
      0%,100% {{ box-shadow: 0 18px 44px rgba(2,6,23,.12); }}
      50%     {{ box-shadow: 0 18px 44px rgba(239,68,68,.18), 0 0 18px rgba(239,68,68,.12); }}
    }}

    .label {{
      font-size: 11px;
      letter-spacing: .18em;
      text-transform: uppercase;
      color: rgba(71,85,105,.92);
      font-weight: 600;
    }}

    .value {{
      font-family: Orbitron, Inter, system-ui, sans-serif;
      font-variant-numeric: tabular-nums;
      margin-top: 8px;
      font-size: 26px;
      font-weight: 700;
      color: rgba(15,23,42,.92);
    }}
    .unit {{
      font-family: Inter, system-ui, sans-serif;
      font-size: 12px;
      color: rgba(71,85,105,.9);
      font-weight: 600;
      margin-left: 4px;
    }}

    .status {{
      margin-top: 10px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.55);
      border: 1px solid rgba(15,23,42,.10);
      font-size: 11px;
      font-family: "JetBrains Mono", ui-monospace, monospace;
      letter-spacing: .10em;
      text-transform: uppercase;
      color: rgba(15,23,42,.78);
      width: fit-content;
    }}
    .status .s-dot {{
      width: 8px; height: 8px; border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent),
                  0 0 18px color-mix(in srgb, var(--accent) 22%, transparent);
    }}

    .icon-wrap {{
      margin-top: 6px;
      display: grid;
      place-items: center;
      height: 84px;
    }}

    /* Optical-fiber conduits */
    .wires {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: clamp(10px, 1.6vw, 18px);
      align-items: center;
      height: 64px;
      margin-top: -24px;
      margin-bottom: -24px;
      position: relative;
      z-index: 1;
    }}

    .wires-bot {{
      display: grid;
      grid-template-columns: 1fr 1.1fr 1fr 1.1fr 1fr;
      gap: clamp(8px, 1.2vw, 14px);
      align-items: center;
      height: 64px;
      margin-top: -24px;
      margin-bottom: -24px;
      position: relative;
      z-index: 1;
    }}

    .wire-slot {{
      display: grid;
      place-items: center;
      height: 100%;
    }}

    /* Simplified Robust Conduit Animation (like realtime.py) */
    .conduit {{
      width: 8px;
      height: 100%;
      background: #e2e8f0;
      border-radius: 4px;
      position: relative;
      overflow: hidden;
      margin: 0 auto;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .conduit-flow {{
      position: absolute;
      top: -50%;
      left: 0;
      width: 100%;
      height: 50%;
      background: linear-gradient(180deg, transparent, var(--c, #0ea5e9), transparent);
      opacity: 0;
      filter: drop-shadow(0 0 4px var(--c));
      will-change: top;
    }}

    .conduit.active .conduit-flow {{
      opacity: calc(0.3 + 0.7 * var(--i, 0.5));
      animation: flowDown 1.5s linear infinite;
    }}

    .conduit.dir-up.active .conduit-flow {{
      animation: flowUp 1.5s linear infinite;
    }}

    @keyframes flowDown {{
      0% {{ top: -50%; }}
      100% {{ top: 100%; }}
    }}
    @keyframes flowUp {{
      0% {{ top: 100%; }}
      100% {{ top: -50%; }}
    }}

    /* AC bus (premium glass rail with animated energy tracer) */
    .bus {{
      height: 92px;
      position: relative;
      z-index: 5;
      margin-top: -4px;
      margin-bottom: -2px;
      border-radius: 18px;
      display: grid;
      align-items: center;
      background: rgba(255,255,255,.48);
      border: 1px solid rgba(15,23,42,.10);
      box-shadow: var(--shadow-sm);
      backdrop-filter: blur(16px) saturate(160%);
      -webkit-backdrop-filter: blur(16px) saturate(160%);
      overflow: hidden;
    }}
    .bus::before {{
      content:"";
      position:absolute; inset: 0;
      background: linear-gradient(90deg, rgba(14,165,233,.08), transparent, rgba(99,102,241,.08));
      pointer-events:none;
    }}

    .bus svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    @keyframes dash {{
      from {{ stroke-dashoffset: 0; }}
      to   {{ stroke-dashoffset: -220; }}
    }}
    .dash {{
      animation: dash 2.6s linear infinite;
      will-change: stroke-dashoffset;
    }}

    /* Status bar */
    .statusbar {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      padding: 10px 12px;
      border-radius: 16px;
      background: rgba(255,255,255,.55);
      border: 1px solid rgba(15,23,42,.10);
      box-shadow: 0 10px 18px rgba(2,6,23,.06);
      backdrop-filter: blur(14px) saturate(160%);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
    }}
    .kv {{
      min-width: 150px;
      display: grid;
      gap: 3px;
    }}
    .k {{
      font-size: 11px;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: rgba(71,85,105,.9);
      font-weight: 600;
    }}
    .v {{
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 15px;
      font-weight: 700;
      color: rgba(15,23,42,.90);
    }}

    @media (max-width: 980px) {{
      .grid-top {{ grid-template-columns: 1fr; }}
      .wires {{ grid-template-columns: 1fr; height: 42px; }}
      .grid-bot {{ grid-template-columns: 1fr; }}
      .wires-bot {{ grid-template-columns: 1fr; height: 42px; }}
      .kv {{ min-width: 140px; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      .conduit::after, .dash {{ animation: none !important; }}
      .card {{ transition: none !important; }}
    }}
  </style>
</head>

<body>
  <div class="stage">
    <div class="hud">
      <div class="hud-inner">
        <!-- TOP ROW -->
        <div class="grid-top">

          <div class="card {'active' if p_pv > 0.5 else ''}" style="--accent:#f59e0b; --accent-soft: rgba(245,158,11,.14);">
            <div class="label">Solar PV</div>
            <div class="icon-wrap">{get_solar_svg_premium(p_pv)}</div>
            <div class="value">{p_pv:.1f}<span class="unit">kW</span></div>
            <div class="status" style="--accent:#f59e0b;">
              <span class="s-dot"></span><span style="color:{pv_status[1]};">{pv_status[0]}</span>
            </div>
          </div>

          <div class="card {cbf_class}" style="--accent:{'#ef4444' if not is_safe else ('#f59e0b' if cbf_active else '#0ea5e9')};">
            <div class="label">U‑CBF Filter</div>
            <div class="icon-wrap">{get_cbf_svg_premium(is_safe, cbf_active)}</div>
            <div class="value" style="font-size:22px;">h = {barrier_value:.3f}</div>
            <div class="status" style="--accent:{'#ef4444' if not is_safe else ('#f59e0b' if cbf_active else '#22c55e')};">
              <span class="s-dot"></span><span style="color:{cbf_status[1]};">{cbf_status[0]}</span>
            </div>
          </div>

          <div class="card {'active' if p_load > 0.5 else ''}" style="--accent:#ef4444; --accent-soft: rgba(239,68,68,.12);">
            <div class="label">Load</div>
            <div class="icon-wrap">{get_load_svg_premium(p_load)}</div>
            <div class="value">{p_load:.1f}<span class="unit">kW</span></div>
            <div class="status" style="--accent:#ef4444;">
              <span class="s-dot"></span><span style="color:{load_status[1]};">{load_status[0]}</span>
            </div>
          </div>

        </div>

        <!-- Top Conduits -->
      <div class="wires">
        <!-- Solar -->
        <div class="wire-slot">
          <div class="conduit dir-down {'active' if p_pv > 0.5 else ''}" style="--c: #f59e0b; --i: {pv_i}">
            <div class="conduit-flow"></div>
          </div>
        </div>
        <!-- CBF -->
        <div class="wire-slot">
          <div class="conduit dir-down {'active' if (cbf_active or not is_safe) else ''}"
               style="--c: {'#ef4444' if not is_safe else '#f59e0b' if cbf_active else '#0ea5e9'}; --i: {1.0 if not is_safe else 0.8 if cbf_active else 0.2}">
            <div class="conduit-flow"></div>
          </div>
        </div>
        <!-- Load -->
        <div class="wire-slot">
          <div class="conduit dir-up {'active' if p_load > 0.5 else ''}" style="--c: #ef4444; --i: {load_i}">
            <div class="conduit-flow"></div>
          </div>
        </div>
      </div>

        <!-- AC BUS -->
        <div class="bus">
          <svg viewBox="0 0 1600 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="rail" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stop-color="rgba(15,23,42,.25)"/>
                <stop offset="50" stop-color="rgba(15,23,42,.12)"/>
                <stop offset="100" stop-color="rgba(15,23,42,.25)"/>
              </linearGradient>
              <linearGradient id="energy" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stop-color="#0ea5e9"/>
                <stop offset="50" stop-color="rgba(224,242,254,.95)"/>
                <stop offset="100" stop-color="#0ea5e9"/>
              </linearGradient>
              <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="2" result="b"/>
                <feMerge>
                  <feMergeNode in="b"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <path id="p" d="M 60 60 H 1540"/>
            </defs>

            <!-- Rail -->
            <use href="#p" stroke="url(#rail)" stroke-width="30" stroke-linecap="round"/>
            <use href="#p" stroke="rgba(255,255,255,.35)" stroke-width="18" stroke-linecap="round"/>

            <!-- Energy tracer -->
            <use href="#p" class="dash" stroke="url(#energy)" stroke-width="4" stroke-linecap="round"
                 stroke-dasharray="90 130" filter="url(#glow)"/>
            <use href="#p" class="dash" stroke="rgba(255,255,255,.75)" stroke-width="2" stroke-linecap="round"
                 stroke-dasharray="18 202"/>

            <!-- Center tag -->
            <g transform="translate(800,60)">
              <rect x="-120" y="-22" width="240" height="44" rx="14"
                    fill="rgba(255,255,255,.55)" stroke="rgba(15,23,42,.14)" filter="url(#glow)"/>
              <text x="0" y="-2" text-anchor="middle"
                    font-family="JetBrains Mono, ui-monospace, monospace"
                    font-size="12" font-weight="800" letter-spacing="2"
                    fill="rgba(15,23,42,.78)">◆ AC BUS ◆</text>
              <text x="0" y="16" text-anchor="middle"
                    font-family="JetBrains Mono, ui-monospace, monospace"
                    font-size="12" font-weight="800"
                    fill="rgba(14,165,233,.95)">{voltage:.0f}V | {frequency:.2f}Hz</text>
            </g>

            <!-- End nodes -->
            <circle cx="60" cy="60" r="7" fill="rgba(15,23,42,.20)"/>
            <circle cx="60" cy="60" r="3" fill="rgba(14,165,233,.95)"/>
            <circle cx="1540" cy="60" r="7" fill="rgba(15,23,42,.20)"/>
            <circle cx="1540" cy="60" r="3" fill="rgba(14,165,233,.95)"/>
          </svg>
        </div>

        <!-- VERTICAL WIRES (BUS -> BOTTOM) -->
        <div class="wires-bot">
          <div></div>
          <!-- Battery -->
          <div class="wire-slot">
            <div class="conduit {'dir-down' if is_charging else 'dir-up'} {'active' if abs(p_battery) > 0.5 else ''}"
                 style="--c: {'#22c55e' if is_charging else '#22c55e'}; --i: {batt_i}">
              <div class="conduit-flow"></div>
            </div>
          </div>
          <div></div>
          <!-- Grid -->
          <div class="wire-slot">
            <div class="conduit {'dir-up' if is_importing else 'dir-down'} {'active' if abs(p_grid) > 0.5 else ''}"
                 style="--c: {'#1d4ed8' if is_importing else '#6d28d9'}; --i: {grid_i}">
              <div class="conduit-flow"></div>
            </div>
          </div>
          <div></div>
        </div>

        <!-- BOTTOM ROW -->
        <div class="grid-bot">
          <div></div>

          <div class="card {'active' if abs(p_battery) > 0.5 else ''}"
               style="--accent:#22c55e; --accent-soft: rgba(34,197,94,.12);">
            <div class="label">Battery</div>
            <div class="icon-wrap">{get_battery_svg_premium(soc, is_charging)}</div>
            <div class="value">{soc*100:.0f}<span class="unit">%</span></div>
            <div class="status" style="--accent:#22c55e;">
              <span class="s-dot"></span>
              <span style="color:{batt_status[1]};">{batt_status[0]}</span>
              <span style="opacity:.7;">|</span>
              <span style="opacity:.92;">{_fmt_signed(p_battery)} kW</span>
            </div>
          </div>

          <div></div>

          <div class="card {'active' if abs(p_grid) > 0.5 else ''}"
               style="--accent:{'#3b82f6' if is_importing else '#8b5cf6'};">
            <div class="label">Utility Grid</div>
            <div class="icon-wrap">{get_grid_svg_premium(is_importing, p_grid)}</div>
            <div class="value">{abs(p_grid):.1f}<span class="unit">kW</span></div>
            <div class="status" style="--accent:{'#3b82f6' if is_importing else '#8b5cf6'};">
              <span class="s-dot"></span><span style="color:{grid_status[1]};">{grid_status[0]}</span>
            </div>
          </div>

          <div></div>
        </div>

        <!-- STATUS BAR -->
        <div class="statusbar">
          <div class="kv">
            <div class="k">System</div>
            <div class="v" style="color:{'#15803d' if is_safe else '#b91c1c'};">
              {"SAFE" if is_safe else "ALERT"}
            </div>
          </div>

          <div class="kv">
            <div class="k">Net Power</div>
            <div class="v" style="color:{'#15803d' if net_power >= 0 else '#b91c1c'};">
              {_fmt_signed(net_power)} kW
            </div>
          </div>

          <div class="kv">
            <div class="k">Barrier</div>
            <div class="v" style="color:{'#15803d' if barrier_value > 0 else '#b91c1c'};">
              h = {barrier_value:.4f}
            </div>
          </div>

          <div class="kv">
            <div class="k">Voltage</div>
            <div class="v" style="color:rgba(14,165,233,.95);">
              {voltage:.1f} V
            </div>
          </div>

          <div class="kv">
            <div class="k">Frequency</div>
            <div class="v" style="color:rgba(14,165,233,.95);">
              {frequency:.2f} Hz
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</body>
</html>
"""

    # A bit taller than before to support the new HUD proportions
    components.html(html, height=800, scrolling=False)


# ------------------------------ Quick test ------------------------------

if __name__ == "__main__":
    st.set_page_config(page_title="Microgrid Twin — Scientific Light Premium", layout="wide")

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