import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Professional Calculator", layout="wide")

def draw_layout(shape, dims, gaps, panel_w, corner_panels):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # ISOframe Math
    # Arc length is determined by how many panels you dedicate to the 90-degree curve
    arc_len = corner_panels * panel_w
    # Radius = (Arc length * 2) / Pi
    radius = (arc_len * 2) / np.pi
    
    wall_x, wall_y = [], []
    sys_x, sys_y = [], []
    total_len = 0

    if shape == "S - Straight":
        l = dims[0]
        g1 = gaps[0]
        # Wall
        wall_x = [0, l]
        wall_y = [g1, g1]
        # System
        sys_x = [0, l]
        sys_y = [0, 0]
        total_len = l
        
    elif shape == "L - Shaped":
        w, d = dims
        ga, gb = gaps # ga is gap from Side A, gb is gap from Side B
        
        # Wall (The outer corner)
        wall_x = [0, w, w]
        wall_y = [0, 0, -d]
        
        # System (Offset inward by the specific gaps)
        # 1. Horizontal segment (Along Side A)
        # Ends before the corner starts. Corner start is radius + gap from the other wall.
        sys_x.extend([0, w - radius - gb])
        sys_y.extend([-ga, -ga])
        
        # 2. Corner (Center is at w-radius-gb, -radius-ga)
        t = np.linspace(np.pi/2, 0, 20)
        sys_x.extend((w - radius - gb) + radius * np.cos(t))
        sys_y.extend((-radius - ga) + radius * np.sin(t))
        
        # 3. Vertical segment (Along Side B)
        sys_x.append(w - gb)
        sys_y.append(-d)
        
        total_len = (w - radius - gb) + arc_len + (d - radius - ga)

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        ga, g_back, gc = gaps # Gaps from side walls and back wall
        
        # Wall
        wall_x = [0, 0, back, back]
        wall_y = [side_a, 0, 0, side_c]
        
        # System
        # 1. Left Vertical
        sys_x.extend([ga, ga])
        sys_y.extend([side_a, radius + g_back])
        
        # 2. Bottom Left Corner
        t = np.linspace(np.pi, 1.5 * np.pi, 20)
        sys_x.extend((radius + ga) + radius * np.cos(t))
        sys_y.extend((radius + g_back) + radius * np.sin(t))
        
        # 3. Horizontal Back
        sys_x.append(back - radius - gc)
        sys_y.append(g_back)
        
        # 4. Bottom Right Corner
        t = np.linspace(1.5 * np.pi, 2 * np.pi, 20)
        sys_x.extend((back - radius - gc) + radius * np.cos(t))
        sys_y.extend((radius + g_back) + radius * np.sin(t))
        
        # 5. Right Vertical
        sys_x.append(back - gc)
        sys_y.append(side_c)
        
        total_len = (side_a - radius - g_back) + arc_len + (back - 2*radius - ga - gc) + arc_len + (side_c - radius - g_back)

    # Plot Wall
    ax.plot(wall_x, wall_y, color='#BDBDBD', linewidth=3, label="Booth Back Wall", linestyle='--')
    # Plot System
    ax.plot(sys_x, sys_y, color='#2e7d32', linewidth=6, solid_capstyle='round', label="ISOframe Wave")
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
    
    return fig, total_len

# --- UI Setup ---
st.title("📏 ISOframe Wave Layout Pro")

with st.sidebar:
    st.header("1. System Settings")
    panel_w = 0.8 # 800mm
    corner_panels = st.number_input("Panels used for 90° curve", min_value=1.5, max_value=5.0, value=2.0, step=0.1)
    
    st.header("2. Booth Dimensions")
    shape = st.selectbox("Wall Shape", ["S - Straight", "L - Shaped", "U - Shaped"])

    gaps = []
    if shape == "S - Straight":
        l = st.number_input("Wall Length (m)", min_value=0.8, value=8.0)
        dims = [l]
        gaps.append(st.slider("Distance from Wall (m)", 0.0, 1.0, 0.1))
        
    elif shape == "L - Shaped":
        w = st.number_input("Wall Side A Width (m)", min_value=1.5, value=4.0)
        d = st.number_input("Wall Side B Depth (m)", min_value=1.5, value=2.5)
        dims = [w, d]
        st.markdown("---")
        ga = st.slider("Gap from Wall A (m)", 0.0, 1.0, 0.1)
        gb = st.slider("Gap from Wall B (m)", 0.0, 1.0, 0.1)
        gaps = [ga, gb]
        
    else: # U-Shaped
        a = st.number_input("Wall Left Depth (m)", min_value=1.5, value=2.0)
        b = st.number_input("Wall Back Width (m)", min_value=3.0, value=4.0)
        c = st.number_input("Wall Right Depth (m)", min_value=1.5, value=2.0)
        dims = [a, b, c]
        st.markdown("---")
        ga = st.slider("Gap from Left Wall (m)", 0.0, 1.0, 0.1)
        gb = st.slider("Gap from Back Wall (m)", 0.0, 1.0, 0.1)
        gc = st.slider("Gap from Right Wall (m)", 0.0, 1.0, 0.1)
        gaps = [ga, gb, gc]

# Logic and Display
fig, total_len = draw_layout(shape, dims, gaps, panel_w, corner_panels)
panels = np.ceil(round(total_len, 3) / panel_w)

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Total Panels Needed", int(panels))
    st.write(f"**Calculated Path:** {total_len:.2f} meters")
    
    # Detail breakdown
    st.write("---")
    st.write("**Technical Details:**")
    calc_radius = (corner_panels * panel_w * 2) / np.pi
    st.write(f"• Panel Width: {panel_w*1000:.0f}mm")
    st.write(f"• Corner Radius: {calc_radius:.2f}m")
    st.write(f"• Corner Arc Length: {corner_panels * panel_w:.2f}m")

with col2:
    st.pyplot(fig)
