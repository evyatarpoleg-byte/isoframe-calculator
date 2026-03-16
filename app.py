import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Pro - Fixed Layout", layout="wide")

def get_arc_points(cx, cy, r, start_deg, end_deg):
    """Generates smooth arc coordinates between two angles."""
    angles = np.deg2rad(np.linspace(start_deg, end_deg, 20))
    return cx + r * np.cos(angles), cy + r * np.sin(angles)

def draw_layout(shape, dims, gaps, panel_w, corner_panels):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Corner Radius logic
    main_arc_len = corner_panels * panel_w
    radius = (main_arc_len * 2) / np.pi
    
    sys_x, sys_y = [], []
    wall_x, wall_y = [], []
    total_len = 0

    if shape == "S - Straight":
        l = dims[0]
        g = gaps[0]
        wall_x, wall_y = [0, l], [g, g]
        
        if g > 0.05:
            # Start Closure: From (0, g) to (g, 0)
            ax_s, ay_s = get_arc_points(g, g, g, 180, 270)
            sys_x.extend(ax_s); sys_y.extend(ay_s)
            # Main Line: From (g, 0) to (l-g, 0)
            sys_x.extend([g, l - g]); sys_y.extend([0, 0])
            # End Closure: From (l-g, 0) to (l, g)
            ax_e, ay_e = get_arc_points(l - g, g, g, 270, 360)
            sys_x.extend(ax_e); sys_y.extend(ay_e)
            total_len = (np.pi * g) + (l - 2*g)
        else:
            sys_x, sys_y = [0, l], [0, 0]
            total_len = l

    elif shape == "L - Shaped":
        w, d = dims
        ga, gb = gaps
        wall_x, wall_y = [0, w, w], [0, 0, -d]
        
        # 1. Start Closure at Wall A (horizontal wall)
        if ga > 0.05:
            ax1, ay1 = get_arc_points(ga, 0, ga, 90, 180) # Arc from wall down
            sys_x.extend(ax1[::-1]); sys_y.extend(ay1[::-1])
            total_len += (np.pi * ga) / 2
        
        # 2. Straight Side A
        sys_x.append(max(ga, 0)); sys_y.append(-ga)
        sys_x.append(w - radius - gb); sys_y.append(-ga)
        total_len += (w - radius - gb - max(ga, 0))

        # 3. Main Corner
        ax_c, ay_c = get_arc_points(w - radius - gb, -ga - radius, radius, 90, 0)
        sys_x.extend(ax_c); sys_y.extend(ay_c)
        total_len += main_arc_len

        # 4. Straight Side B
        sys_x.append(w - gb); sys_y.append(-d + gb if gb > 0.05 else -d)
        total_len += (d - radius - ga - (gb if gb > 0.05 else 0))

        # 5. End Closure at Wall B (vertical wall)
        if gb > 0.05:
            ax2, ay2 = get_arc_points(w, -d + gb, gb, 180, 270)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len += (np.pi * gb) / 2

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        ga, gb, gc = gaps
        wall_x, wall_y = [0, 0, back, back], [side_a, 0, 0, side_c]
        
        # 1. Start Closure (Top Left)
        if ga > 0.05:
            ax1, ay1 = get_arc_points(0, side_a - ga, ga, 90, 0)
            sys_x.extend(ax1[::-1]); sys_y.extend(ay1[::-1])
            total_len += (np.pi * ga) / 2
        
        # 2. Left Wall Straight
        sys_x.append(ga); sys_y.append(side_a - ga if ga > 0.05 else side_a)
        sys_x.append(ga); sys_y.append(radius + gb)
        total_len += (side_a - radius - gb - (ga if ga > 0.05 else 0))

        # 3. Corner 1 (Bottom Left)
        ax_c1, ay_c1 = get_arc_points(ga + radius, radius + gb, radius, 180, 270)
        sys_x.extend(ax_c1); sys_y.extend(ay_c1)
        total_len += main_arc_len

        # 4. Back Wall Straight
        sys_x.append(back - radius - gc); sys_y.append(gb)
        total_len += (back - 2*radius - ga - gc)

        # 5. Corner 2 (Bottom Right)
        ax_c2, ay_c2 = get_arc_points(back - radius - gc, radius + gb, radius, 270, 360)
        sys_x.extend(ax_c2); sys_y.extend(ay_c2)
        total_len += main_arc_len

        # 6. Right Wall Straight
        sys_x.append(back - gc); sys_y.append(side_c - gc if gc > 0.05 else side_c)
        total_len += (side_c - radius - gb - (gc if gc > 0.05 else 0))

        # 7. End Closure (Top Right)
        if gc > 0.05:
            ax2, ay2 = get_arc_points(back, side_c - gc, gc, 180, 90)
            sys_x.extend(ax2[::-1]); sys_y.extend(ay2[::-1])
            total_len += (np.pi * gc) / 2

    # Plotting
    ax.plot(wall_x, wall_y, color='#BDBDBD', lw=2, ls='--', label="Booth Wall")
    ax.plot(sys_x, sys_y, color='#2e7d32', lw=5, solid_capstyle='round', label="ISOframe (Closed)")
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
    
    return fig, total_len

# --- UI Layout ---
st.title("📏 ISOframe Wave Pro - Wall Closure")

with st.sidebar:
    st.header("Settings")
    panel_w = 0.8
    corner_p = st.number_input("Panels per 90° curve", 1.5, 5.0, 2.0, 0.1)
    shape = st.selectbox("Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    
    dims, gaps = [], []
    if shape == "S - Straight":
        dims = [st.number_input("Length (m)", 1.0, 20.0, 8.0)]
        gaps = [st.slider("Wall Gap (m)", 0.0, 1.0, 0.2)]
    elif shape == "L - Shaped":
        dims = [st.number_input("Wall Width (m)", 1.5, 20.0, 4.0), st.number_input("Wall Depth (m)", 1.5, 20.0, 2.5)]
        gaps = [st.slider("Gap from Width Wall (A)", 0.0, 1.0, 0.2), st.slider("Gap from Depth Wall (B)", 0.0, 1.0, 0.2)]
    else:
        dims = [st.number_input("Left Wall (A)", 1.5, 10.0, 2.0), st.number_input("Back Wall (B)", 3.0, 20.0, 4.0), st.number_input("Right Wall (C)", 1.5, 10.0, 2.0)]
        gaps = [st.slider("Gap Left", 0.0, 1.0, 0.2), st.slider("Gap Back", 0.0, 1.0, 0.2), st.slider("Gap Right", 0.0, 1.0, 0.2)]

fig, total_len = draw_layout(shape, dims, gaps, panel_w, corner_p)
panels = np.ceil(round(total_len, 4) / panel_w)

c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Total Panels", int(panels))
    st.write(f"**Total Path:** {total_len:.2f}m")
    st.info("System automatically curves back to the wall at both ends if a gap exists.")
with c2:
    st.pyplot(fig)
