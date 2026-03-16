import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Calculator", layout="wide")

def draw_layout(shape, dims, panel_w, radius):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Starting point
    x, y = [0], [0]
    angle = 0
    
    if shape == "S - Straight":
        length = dims[0]
        x = [0, length]
        y = [0, 0]
        total_len = length
        
    elif shape == "L - Shaped":
        side_a, side_b = dims
        # Straight part A
        x = [0, side_a - radius]
        y = [0, 0]
        # Curve
        t = np.linspace(0, -np.pi/2, 20)
        cx, cy = x[-1], y[-1] - radius
        x = np.concatenate([x, cx + radius * np.sin(t + np.pi/2)])
        y = np.concatenate([y, cy + radius * np.cos(t + np.pi/2)])
        # Straight part B
        x = np.concatenate([x, [x[-1], x[-1]]])
        y = np.concatenate([y, [y[-1], y[-1] - (side_b - radius)]])
        total_len = (side_a - radius) + (1.57 * radius) + (side_b - radius)

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        # A
        x, y = [0, 0], [side_a - radius, 0]
        # Curve 1
        t = np.linspace(0, np.pi/2, 20)
        x = np.concatenate([x, radius - radius * np.cos(t)])
        y = np.concatenate([y, -radius * np.sin(t)])
        # Back
        x = np.concatenate([x, [radius, back - radius]])
        y = np.concatenate([y, [-radius, -radius]])
        # Curve 2
        t = np.linspace(np.pi/2, 0, 20)
        x = np.concatenate([x, (back - radius) + radius * np.cos(t)])
        y = np.concatenate([y, -radius + radius * np.sin(t)])
        # C
        x = np.concatenate([x, [back, back]])
        y = np.concatenate([y, [0, side_c - radius]])
        total_len = (side_a - radius) + (1.57 * radius) + (back - 2*radius) + (1.57 * radius) + (side_c - radius)

    ax.plot(x, y, color='#2e7d32', linewidth=5, solid_capstyle='round')
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, total_len

st.title("📏 ISOframe Wave Calculator")
st.write("Calculate how many 800mm panels you need for your booth layout.")

col1, col2 = st.columns([1, 2])

with col1:
    shape = st.selectbox("Wall Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    panel_w = 0.8 # 800mm
    radius = 1.02 # Radius for a 2-panel 90-degree curve
    
    if shape == "S - Straight":
        l = st.number_input("Wall Length (m)", value=8.0)
        dims = [l]
    elif shape == "L - Shaped":
        w = st.number_input("Side A (m)", value=4.0)
        d = st.number_input("Side B (m)", value=4.0)
        dims = [w, d]
    else:
        a = st.number_input("Side A Depth (m)", value=3.0)
        b = st.number_input("Back Wall Width (m)", value=6.0)
        c = st.number_input("Side C Depth (m)", value=3.0)
        dims = [a, b, c]

    fig, total_len = draw_layout(shape, dims, panel_w, radius)
    panels = np.ceil(total_len / panel_w)
    
    st.metric("Panels Needed", int(panels))
    st.write(f"**Total Path Length:** {total_len:.2f}m")

with col2:
    st.write("### Layout Preview (Top Down)")
    st.pyplot(fig)
