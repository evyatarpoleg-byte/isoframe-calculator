import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Calculator", layout="wide")

def draw_layout(shape, dims, panel_w, radius):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Standard 90-degree arc length (Quarter circle)
    # L = (pi * R) / 2
    arc_len = (np.pi * radius) / 2
    
    x_coords = []
    y_coords = []

    if shape == "S - Straight":
        length = dims[0]
        x_coords = [0, length]
        y_coords = [0, 0]
        total_len = length
        
    elif shape == "L - Shaped":
        side_a, side_b = dims
        # 1. Horizontal line from left to corner start
        x_coords.extend([0, side_a - radius])
        y_coords.extend([0, 0])
        # 2. Smooth 90 deg corner (center is at side_a-radius, -radius)
        t = np.linspace(np.pi/2, 0, 20)
        x_coords.extend((side_a - radius) + radius * np.cos(t))
        y_coords.extend((-radius) + radius * np.sin(t))
        # 3. Vertical line down to end
        x_coords.append(side_a)
        y_coords.append(-(side_b - radius + radius)) # Total depth is side_b
        
        total_len = (side_a - radius) + arc_len + (side_b - radius)

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        # 1. Left side (Vertical) - start at top left
        x_coords.append(0)
        y_coords.append(side_a)
        x_coords.append(0)
        y_coords.append(radius)
        # 2. Bottom-left corner (center at R, R)
        t = np.linspace(np.pi, 1.5 * np.pi, 20)
        x_coords.extend(radius + radius * np.cos(t))
        y_coords.extend(radius + radius * np.sin(t))
        # 3. Back wall (Horizontal)
        x_coords.append(back - radius)
        y_coords.append(0)
        # 4. Bottom-right corner (center at back-R, R)
        t = np.linspace(1.5 * np.pi, 2 * np.pi, 20)
        x_coords.extend((back - radius) + radius * np.cos(t))
        y_coords.extend(radius + radius * np.sin(t))
        # 5. Right side (Vertical)
        x_coords.append(back)
        y_coords.append(side_c)
        
        total_len = (side_a - radius) + arc_len + (back - 2*radius) + arc_len + (side_c - radius)

    # Plotting the wall
    ax.plot(x_coords, y_coords, color='#2e7d32', linewidth=6, solid_capstyle='round')
    
    # Adding some style
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add a floor grid for scale (optional)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    return fig, total_len

st.title("📏 ISOframe Wave Calculator")
st.write("Calculate how many 800mm panels you need for your booth layout.")

col1, col2 = st.columns([1, 2])

with col1:
    shape = st.selectbox("Wall Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    panel_w = 0.8 # 800mm
    # To use 2 panels for a 90 degree curve, the radius must be approx 1.02m
    radius = 1.02 
    
    if shape == "S - Straight":
        l = st.number_input("Wall Length (m)", min_value=0.8, value=8.0, step=0.1)
        dims = [l]
    elif shape == "L - Shaped":
        w = st.number_input("Side A (Width) (m)", min_value=1.5, value=4.0, step=0.1)
        d = st.number_input("Side B (Depth) (m)", min_value=1.5, value=2.5, step=0.1)
        dims = [w, d]
    else:
        a = st.number_input("Left Side Depth (m)", min_value=1.5, value=2.0, step=0.1)
        b = st.number_input("Back Wall Width (m)", min_value=3.0, value=4.0, step=0.1)
        c = st.number_input("Right Side Depth (m)", min_value=1.5, value=2.0, step=0.1)
        dims = [a, b, c]

    fig, total_len = draw_layout(shape, dims, panel_w, radius)
    panels = np.ceil(total_len / panel_w)
    
    st.divider()
    st.metric("Panels Needed", int(panels))
    st.write(f"**Total Wall Path:** {total_len:.2f}m")
    st.caption(f"Calculation uses a {radius}m radius for corners (2 panels per corner).")

with col2:
    st.write("### Layout Preview (Top Down)")
    st.pyplot(fig)
