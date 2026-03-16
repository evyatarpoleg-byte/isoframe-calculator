import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Calculator", layout="wide")

def draw_layout(shape, dims, panel_w, radius, gap=0.1):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # ISOframe Math: Quarter circle arc length
    arc_len = (np.pi * radius) / 2
    
    # Coordinates for the Booth Wall (Grey) and System (Green)
    wall_x, wall_y = [], []
    sys_x, sys_y = [], []

    if shape == "S - Straight":
        l = dims[0]
        # Wall
        wall_x = [0, l]
        wall_y = [gap, gap]
        # System
        sys_x = [0, l]
        sys_y = [0, 0]
        total_len = l
        
    elif shape == "L - Shaped":
        w, d = dims
        # Wall (Sharp corner)
        wall_x = [0, w, w]
        wall_y = [0, 0, -d]
        
        # System (Offset by gap)
        # 1. Horizontal
        sys_x.extend([0, w - radius - gap])
        sys_y.extend([-gap, -gap])
        # 2. Corner (Center is at w-radius-gap, -radius-gap)
        t = np.linspace(np.pi/2, 0, 20)
        sys_x.extend((w - radius - gap) + radius * np.cos(t))
        sys_y.extend((-radius - gap) + radius * np.sin(t))
        # 3. Vertical
        sys_x.append(w - gap)
        sys_y.append(-d)
        
        total_len = (w - radius - gap) + arc_len + (d - radius - gap)

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        # Wall (Sharp corners)
        wall_x = [0, 0, back, back]
        wall_y = [side_a, 0, 0, side_c]
        
        # System (Offset inward by gap)
        # 1. Left Vertical
        sys_x.extend([gap, gap])
        sys_y.extend([side_a, radius + gap])
        # 2. Bottom Left Corner (Center at R+gap, R+gap)
        t = np.linspace(np.pi, 1.5 * np.pi, 20)
        sys_x.extend((radius + gap) + radius * np.cos(t))
        sys_y.extend((radius + gap) + radius * np.sin(t))
        # 3. Horizontal Back
        sys_x.append(back - radius - gap)
        sys_y.append(gap)
        # 4. Bottom Right Corner (Center at back-R-gap, R+gap)
        t = np.linspace(1.5 * np.pi, 2 * np.pi, 20)
        sys_x.extend((back - radius - gap) + radius * np.cos(t))
        sys_y.extend((radius + gap) + radius * np.sin(t))
        # 5. Right Vertical
        sys_x.append(back - gap)
        sys_y.append(side_c)
        
        total_len = (side_a - radius - gap) + arc_len + (back - 2*(radius + gap)) + arc_len + (side_c - radius - gap)

    # Plot Wall
    ax.plot(wall_x, wall_y, color='#BDBDBD', linewidth=3, label="Booth Back Wall", linestyle='--')
    # Plot System
    ax.plot(sys_x, sys_y, color='#2e7d32', linewidth=6, solid_capstyle='round', label="ISOframe Wave")
    
    # Legend and Styling
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
    
    return fig, total_len

st.title("📏 ISOframe Wave Calculator")
st.write("Determine the number of 800mm panels required, accounting for a 10cm wall clearance.")

col1, col2 = st.columns([1, 2])

with col1:
    shape = st.selectbox("Wall Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    panel_w = 0.8
    radius = 1.02 # Safe 2-panel curve radius
    gap = 0.1    # 10cm distance from wall
    
    if shape == "S - Straight":
        l = st.number_input("Booth Wall Length (m)", min_value=0.8, value=8.0, step=0.1)
        dims = [l]
    elif shape == "L - Shaped":
        w = st.number_input("Wall Side A (Width) (m)", min_value=1.5, value=4.0, step=0.1)
        d = st.number_input("Wall Side B (Depth) (m)", min_value=1.5, value=2.5, step=0.1)
        dims = [w, d]
    else:
        a = st.number_input("Wall Left Depth (m)", min_value=1.5, value=2.0, step=0.1)
        b = st.number_input("Wall Back Width (m)", min_value=3.0, value=4.0, step=0.1)
        c = st.number_input("Wall Right Depth (m)", min_value=1.5, value=2.0, step=0.1)
        dims = [a, b, c]

    fig, total_len = draw_layout(shape, dims, panel_w, radius, gap)
    panels = np.ceil(total_len / panel_w)
    
    st.divider()
    st.metric("ISOframe Panels Needed", int(panels))
    st.write(f"**Total Path Length:** {total_len:.2f}m")
    st.info(f"System is calculated with a {int(gap*100)}cm gap from the booth wall.")

with col2:
    st.write("### Top-Down Layout Preview")
    st.pyplot(fig)
