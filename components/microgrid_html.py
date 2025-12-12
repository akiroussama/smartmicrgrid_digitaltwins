import streamlit as st
import streamlit.components.v1 as components

def render_microgrid_html(state):
    """
    Render the microgrid schematic using the 'Cyberpunk' SVG/HTML style.
    Aligned with the 'Standard' Bus Topology from microgrid_schematic.py.
    """
    
    # 1. Extract State
    p_pv = state.get('p_pv', 0.0)
    p_batt = state.get('p_battery', 0.0)
    p_grid = state.get('p_grid', 0.0)
    p_load = state.get('p_load', 0.0)
    soc = state.get('soc', 0.5)
    
    barrier = state.get('barrier_value', 1.0)
    is_safe = state.get('is_safe', True)
    cbf_active = state.get('cbf_active', False)

    # 2. Styling Vars
    col_cyan = "#49d9ff"
    col_pink = "#ff4b75"
    col_green = "#57ffd8"
    col_gold = "#FBBF24"
    col_orange = "#F97316"
    
    # Scale animations (inverse duration)
    def get_dur(val):
        v = abs(val)
        if v < 0.1: return "0s"
        factor = min(v / 50.0, 1.0)
        return f"{3.0 - factor*2.5:.2f}s"

    dur_sol = get_dur(p_pv)
    dur_load = get_dur(p_load)
    dur_batt = get_dur(p_batt)
    dur_grid = get_dur(p_grid)

    batt_fill = soc 

    # 3. HTML Layout (Bus Topology)
    # Canvas: 1000 x 500
    # Solar: Top Center (500, 80) attached to Bus
    # Bus: Horizontal Rail (Y=200) from 100 to 900
    # Battery: Left (200, 350) attached to Bus
    # Grid: Far Left (100, 350) ? Or Below Battery?
    # Let's match SpacedLayout roughly:
    # Solar Top (500, 80)
    # Bus (Y=220)
    # Grid (Left, 150, 350)
    # Battery (Mid-Left, 350, 350)
    # CBF (Center, 500, 350)
    # Load (Right, 800, 350)

    html_code = f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
<style>
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        /* Force dark background for the component card so neon works */
        background: transparent; 
        font-family: 'Rajdhani', sans-serif;
        overflow: hidden;
    }}
    .dashboard {{
        width: 100%;
        max-width: 1000px;
        /* Dark Card Background */
        background: #080a10;
        background-image: radial-gradient(circle at 50% 0%, #1a2035, #080a10 60%);
        border-radius: 24px;
        padding: 20px;
        position: relative;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2), inset 0 0 0 1px rgba(255,255,255,0.08);
    }}
    
    /* Grid Pattern Overlay */
    .grid {{
        position: absolute;
        inset: 10px;
        border-radius: 18px;
        background-image:
            linear-gradient(rgba(73, 217, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(73, 217, 255, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        z-index: 0;
        pointer-events: none;
    }}
    
    /* Header */
    .header {{
        position: absolute;
        top: 20px;
        left: 30px;
        z-index: 10;
    }}
    
    svg {{
        position: relative;
        z-index: 2;
        width: 100%;
        height: auto;
    }}
    
    /* Rails & Flows */
    .rail {{
        stroke: rgba(255,255,255,0.08);
        stroke-width: 12;
        stroke-linecap: round;
        fill: none;
    }}
    .bus-bar {{
        stroke: #f97316;
        stroke-width: 16;
        stroke-linecap: round;
        filter: drop-shadow(0 0 8px rgba(249, 115, 22, 0.4));
        opacity: 0.8;
    }}
    .flow {{
        stroke-dasharray: 12 12;
        stroke-linecap: round;
        stroke-width: 6;
        animation: dash linear infinite;
        fill: none;
        filter: drop-shadow(0 0 5px currentColor);
    }}
    @keyframes dash {{
        to {{ stroke-dashoffset: -240; }}
    }}
    
    .dir-normal {{ animation-direction: normal; }}
    .dir-reverse {{ animation-direction: reverse; }}
    
    /* Nodes */
    .node-card {{
        fill: rgba(15, 23, 42, 0.9);
        stroke: rgba(255,255,255,0.1);
        stroke-width: 1;
        rx: 12;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
    }}
    
    text {{
        font-family: 'Rajdhani', sans-serif;
        text-anchor: middle;
    }}
    
    .lbl {{ fill: #94a3b8; font-size: 12px; letter-spacing: 1px; font-weight: 600; }}
    .val {{ fill: white; font-family: 'Orbitron', sans-serif; font-size: 20px; font-weight: 600; }}
    .sub {{ fill: #64748b; font-size: 10px; }}
    
    /* Battery Liquid */
    .battery-fill {{ fill: url(#batGrad); transition: height 0.5s; }}

</style>
</head>
<body>
<div class="dashboard">
    <div class="grid"></div>
    <div class="header">
        <div style="color:white; font-family:'Orbitron'; font-size:20px; letter-spacing:2px;">MICROGRID<span style="color:#49d9ff">TWIN</span></div>
        <div style="color:#64748b; font-size:10px; letter-spacing:3px; margin-top:4px;">REAL-TIME MONITOR</div>
    </div>
    
    <svg viewBox="0 0 1000 500">
        <defs>
            <linearGradient id="batGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#059669" /> 
                <stop offset="100%" stop-color="#34d399" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        <!-- ================= BUS BAR ================= -->
        <!-- Horizontal Rail Y=220 -->
        <line x1="150" y1="220" x2="850" y2="220" class="bus-bar" />
        <text x="880" y="225" fill="#f97316" font-size="12" style="text-anchor:start;">230V BUS</text>

        <!-- ================= WIRES & FLOWS ================= -->

        <!-- 1. SOLAR (Top) -> Bus -->
        <path class="rail" d="M 500 130 L 500 220" />
        <path class="flow dir-normal" d="M 500 130 L 500 220" stroke="{col_gold}" 
              style="animation-duration:{dur_sol}; display:{'none' if p_pv < 0.1 else 'block'};" />
              
        <!-- 2. BATTERY (Bottom Left) -> Bus -->
        <!-- Pos: 300, 310. Path Up. -->
        <path class="rail" d="M 300 310 L 300 220" />
        <!-- Discharge (>0) = Up (To Bus). Charge (<0) = Down. -->
        <!-- Path defined Up (310->220). So Normal = Up = Discharge. -->
        <path class="flow {'dir-normal' if p_batt > 0 else 'dir-reverse'}" d="M 300 310 L 300 220" stroke="{col_green}" 
              style="animation-duration:{dur_batt}; display:{'none' if abs(p_batt) < 0.1 else 'block'};" />
              
        <!-- 3. GRID (Bottom Far Left) -> Bus -->
        <!-- Pos: 150, 310. Path Up. -->
        <path class="rail" d="M 150 310 L 150 220" />
        <!-- Import (>0) = To Bus (Up). Export (<0) = From Bus. -->
        <path class="flow {'dir-normal' if p_grid > 0 else 'dir-reverse'}" d="M 150 310 L 150 220" stroke="{col_cyan}" 
              style="animation-duration:{dur_grid}; display:{'none' if abs(p_grid) < 0.1 else 'block'};" />
              
        <!-- 4. LOAD (Bottom Right) -> Bus -->
        <!-- Pos: 750, 310. Path Up. -->
        <path class="rail" d="M 750 310 L 750 220" />
        <!-- Load Consumes = From Bus (Down). Path is Up. So Reverse. -->
        <path class="flow dir-reverse" d="M 750 310 L 750 220" stroke="{col_pink}" 
              style="animation-duration:{dur_load}; display:{'none' if p_load < 0.1 else 'block'};" />
        
        <!-- ================= COMPONENTS ================= -->

        <!-- SOLAR (Top Center) -->
        <g transform="translate(425, 40)">
            <rect class="node-card" width="150" height="90" />
            <text x="75" y="25" class="lbl">SOLAR PV</text>
            <text x="75" y="55" class="val" fill="{col_gold}">{p_pv:.1f}</text>
            <text x="75" y="75" class="sub">{p_pv/50*100:.0f}% CAP</text>
            <circle cx="20" cy="20" r="5" fill="{col_gold}" />
        </g>
        
        <!-- GRID (Bottom Left) -->
        <g transform="translate(75, 310)">
            <rect class="node-card" width="150" height="90" stroke="{col_cyan}" stroke-width="2" />
            <text x="75" y="25" class="lbl">MAIN GRID</text>
            <text x="75" y="55" class="val" fill="{col_cyan}">{abs(p_grid):.1f}</text>
            <text x="75" y="75" class="sub">{'IMPORT' if p_grid > 0 else 'EXPORT'}</text>
        </g>
        
        <!-- BATTERY (Bottom Mid-Left) -->
        <g transform="translate(250, 310)">
            <rect class="node-card" width="140" height="110" />
            <!-- Battery Icon -->
            <rect x="50" y="45" width="40" height="50" rx="4" fill="#1e293b" stroke="#334155" />
            <rect x="65" y="40" width="10" height="6" fill="#334155" />
            <rect class="battery-fill" x="52" y="{47 + (1-batt_fill)*46}" width="36" height="{46 * batt_fill}" rx="2" />
            
            <text x="70" y="25" class="lbl">BATTERY</text>
            <text x="70" y="105" class="val" font-size="16" fill="{col_green}">{int(soc*100)}%</text>
        </g>
        
        <!-- CBF (Bottom Center) -->
        <!-- Floating Shield -->
        <g transform="translate(460, 260)">
             <path d="M 40 0 L 70 20 L 70 60 L 40 80 L 10 60 L 10 20 Z" 
                   fill="rgba(0,0,0,0.6)" stroke="{col_orange if cbf_active else col_cyan}" 
                   stroke-width="{3 if cbf_active else 1}" />
             <text x="40" y="45" font-size="24" fill="{col_orange if cbf_active else col_cyan}">
                {'!' if cbf_active else '✓'}
             </text>
             <text x="40" y="95" class="sub" fill="#64748b">SAFETY</text>
             <text x="40" y="110" class="sub" font-family="monospace">h={barrier:.1f}</text>
        </g>
        
        <!-- LOAD (Bottom Right) -->
        <g transform="translate(675, 310)">
             <rect class="node-card" width="150" height="90" stroke="{col_pink}" stroke-width="2" />
             <text x="75" y="25" class="lbl">LOAD</text>
             <text x="75" y="55" class="val" fill="{col_pink}">{p_load:.1f}</text>
             <text x="75" y="75" class="sub">DEMAND</text>
        </g>

    </svg>
</div>
</body>
</html>
    """
    
    components.html(html_code, height=500, scrolling=False)
