import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Pro - Auto-Closure", layout="wide")

def get_arc(start_xy, start_angle, turn_angle, radius):
    """Helper to generate arc coordinates"""
    t = np.linspace(start_angle, start_angle + turn_angle, 20)
    # Center of rotation
    cx = start_xy[0] - radius * np.cos(start_angle)
    cy = start_xy[1] - radius * np.sin(start_angle)
    x = cx + radius * np.cos(t)
    y = cy + radius * np.sin(t)
    return x, y

def draw_layout(shape, dims, gaps, panel_w, corner_panels):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Corner Radius logic
    main_arc_len = corner_panels * panel_w
    main_radius = (main_arc_len * 2) / np.pi
    
    sys_x, sys_y = [], []
    wall_x, wall_y = [], []
    added_len = 0

    if shape == "S - Straight":
        l = dims[0]
        g = gaps[0]
        wall_x, wall_y = [0, l], [g, g]
        # System main line
        sys_x, sys_y = [0, l], [0, 0]
        # Closures
        if g > 0.05:
            # Start closure
            tx, ty = get_arc([0,0], 0, np.pi/2, g)
            sys_x = np.concatenate([tx[::-1], sys_x])
            sys_y = np.concatenate([ty[::-1], sys_y])
            # End closure
            tx, ty = get_arc([l,0], 0, -np.pi/2, g)
            sys_x = np.concatenate([sys_x, tx])
            sys_y = np.concatenate([sys_y, ty])
            added_len += (np.pi * g) # Two quarter circles

    elif shape == "L - Shaped":
        w, d = dims
        ga, gb = gaps
        wall_x, wall_y = [0, w, w], [0, 0, -d]
        
        # Start Closure (Side A)
        if ga > 0.05:
            tx, ty = get_arc([0, -ga], -np.pi/2, -np.pi/2, ga)
            sys_x.extend(tx[::-1]); sys_y.extend(ty[::-1])
            added_len += (np.pi * ga) / 2
            
        # Segment A
        sys_x.extend([0, w - main_radius - gb])
        sys_y.extend([-ga, -ga])
        # Main Corner
        tx, ty = get_arc([w - main_radius - gb, -ga], np.pi/2, -np.pi/2, main_radius)
        sys_x.extend(tx); sys_y.extend(ty)
        # Segment B
        sys_x.append(w - gb); sys_y.append(-d + (gb if gb > 0.05 else 0))
        
        # End Closure (Side B)
        if gb > 0.05:
            tx, ty = get_arc([w-gb, -d], 0, np.pi/2, gb)
            sys_x.extend(tx); sys_y.extend(ty)
            added_len += (np.pi * gb) / 2

        added_len += (w - main_radius - gb) + main_arc_len + (d - main_radius - ga)

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        ga, gb, gc = gaps
        wall_x, wall_y = [0, 0, back, back], [side_a, 0, 0, side_c]
        
        # Start Closure (Side A)
        if ga > 0.05:
            tx, ty = get_arc([ga, side_a], 0, np.pi/2, ga)
            sys_x.extend(tx[::-1]); sys_y.extend(ty[::-1])
            added_len += (np.pi * ga) / 2
            
        # Left wall -> Corner 1 -> Back -> Corner 2 -> Right wall
        sys_x.extend([ga, ga]); sys_y.extend([side_a, main_radius + gb])
        t1x, t1y = get_arc([ga + main_radius, main_radius + gb], np.pi, -np.pi/2, main_radius)
        sys_x.extend(t1x[::-1]); sys_y.extend(t1y[::-1])
        
        sys_x.append(back - main_radius - gc); sys_y.append(gb)
        
        t2x, t2y = get_arc([back - main_radius - gc, main_radius + gb], -np.pi/2, -np.pi/2, main_radius)
        sys_x.extend(t2x); sys_y.extend(t2y)
        
        sys_x.append(back - gc); sys_y.append(side_c - (gc if gc > 0.05 else 0))

        # End Closure (Side C)
        if gc > 0.05:
            tx, ty = get_arc([back-gc, side_c], np.pi, -np.pi/2, gc)
            sys_x.extend(tx); sys_y.extend(ty)
            added_len += (np.pi * gc) / 2
            
        added_len += (side_a - main_radius - gb) + (back - 2*main_radius - ga - gc) + (side_c - main_radius - gb) + (2 * main_arc_len)

    # Drawing
    ax.plot(wall_x, wall_y, color='#BDBDBD', lw=2, ls='--', label="Booth Wall")
    ax.plot(sys_x, sys_y, color='#2e7d32', lw=5, solid_capstyle='round', label="ISOframe (Closed)")
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
    
    return fig, added_len

# --- UI ---
st.title("📏 ISOframe Wave Pro - Wall Closure")

with st.sidebar:
    st.header("Settings")
    panel_w = 0.8
    corner_p = st.number_input("Panels per 90° curve", 1.5, 5.0, 2.0, 0.1)
    
    shape = st.selectbox("Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    
    dims, gaps = [], []
    if shape == "S - Straight":
        dims = [st.number_input("Length", 1.0, 20.0, 8.0)]
        gaps = [st.slider("Wall Gap (m)", 0.0, 1.0, 0.2)]
    elif shape == "L - Shaped":
        dims = [st.number_input("Width (A)", 1.5, 20.0, 4.0), st.number_input("Depth (B)", 1.5, 20.0, 2.5)]
        gaps = [st.slider("Gap Wall A", 0.0, 1.0, 0.2), st.slider("Gap Wall B", 0.0, 1.0, 0.2)]
    else:
        dims = [st.number_input("Left (A)", 1.5, 10.0, 2.0), st.number_input("Back (B)", 3.0, 20.0, 4.0), st.number_input("Right (C)", 1.5, 10.0, 2.0)]
        gaps = [st.slider("Gap Left", 0.0, 1.0, 0.2), st.slider("Gap Back", 0.0, 1.0, 0.2), st.slider("Gap Right", 0.0, 1.0, 0.2)]

fig, total_len = draw_layout(shape, dims, gaps, panel_w, corner_p)
panels = np.ceil(round(total_len, 3) / panel_w)

c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Total Panels", int(panels))
    st.write(f"**Total Path:** {total_len:.2f}m")
    st.info("Closures are automatically added to ends where the gap > 0.05m to hide the back-end of the booth.")
with c2:
    st.pyplot(fig)
