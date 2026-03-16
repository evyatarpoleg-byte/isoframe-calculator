import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Pro - Drawing Fix", layout="wide")

def get_arc(cx, cy, r, start_deg, end_deg):
    """Helper to generate smooth arc points between two angles."""
    if r <= 0: return [cx], [cy]
    angles = np.deg2rad(np.linspace(start_deg, end_deg, 20))
    return cx + r * np.cos(angles), cy + r * np.sin(angles)

def draw_layout(shape, dims, gaps, panel_w, corner_panels):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # ISOframe corner radius
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
            # Start Closure (Wall to System)
            ax1, ay1 = get_arc(g, g, g, 180, 270)
            sys_x.extend(ax1); sys_y.extend(ay1)
            # Straight
            sys_x.extend([g, l-g]); sys_y.extend([0, 0])
            # End Closure (System to Wall)
            ax2, ay2 = get_arc(l-g, g, g, 270, 360)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len = (np.pi * g) + (l - 2*g)
        else:
            sys_x, sys_y = [0, l], [0, 0]
            total_len = l

    elif shape == "L - Shaped":
        w, d = dims
        ga, gb = gaps
        wall_x, wall_y = [0, w, w], [0, 0, -d]
        
        # 1. Start Closure (at x=0)
        if ga > 0.05:
            ax1, ay1 = get_arc(ga, 0, ga, 180, 270)
            sys_x.extend(ax1); sys_y.extend(ay1)
            total_len += (np.pi * ga) / 2
        else:
            sys_x.append(0); sys_y.append(0)

        # 2. Straight A
        sys_x.append(w - radius - gb); sys_y.append(-ga)
        total_len += (w - radius - gb - (ga if ga > 0.05 else 0))

        # 3. Main Corner
        axc, ayc = get_arc(w - radius - gb, -ga - radius, radius, 90, 0)
        sys_x.extend(axc); sys_y.extend(ayc)
        total_len += main_arc_len

        # 4. Straight B
        sys_x.append(w - gb); sys_y.append(-d + gb if gb > 0.05 else -d)
        total_len += (d - radius - ga - (gb if gb > 0.05 else 0))

        # 5. End Closure (at y=-d)
        if gb > 0.05:
            ax2, ay2 = get_arc(w, -d + gb, gb, 180, 270)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len += (np.pi * gb) / 2

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        ga, gb, gc = gaps # ga=Left gap, gb=Back gap, gc=Right gap
        wall_x, wall_y = [0, 0, back, back], [side_a, 0, 0, side_c]
        
        # Adjust radius if back wall is too small
        r_eff = min(radius, (back - ga - gc) / 2.1)

        # 1. Start Closure (Top Left)
        if ga > 0.05:
            ax1, ay1 = get_arc(ga, side_a, ga, 180, 90)
            sys_x.extend(ax1[::-1]); sys_y.extend(ay1[::-1])
            total_len += (np.pi * ga) / 2
        else:
            sys_x.append(0); sys_y.append(side_a)

        # 2. Left Side Straight
        sys_x.append(ga); sys_y.append(r_eff + gb)
        total_len += (side_a - r_eff - gb - (ga if ga > 0.05 else 0))

        # 3. Corner 1 (Bottom Left)
        axc1, ayc1 = get_arc(ga + r_eff, r_eff + gb, r_eff, 180, 270)
        sys_x.extend(axc1); sys_y.extend(ayc1)
        total_len += (np.pi * r_eff) / 2

        # 4. Back Wall Straight
        sys_x.append(back - gc - r_eff); sys_y.append(gb)
        total_len += (back - ga - gc - 2*r_eff)

        # 5. Corner 2 (Bottom Right)
        axc2, ayc2 = get_arc(back - gc - r_eff, r_eff + gb, r_eff, 270, 360)
        sys_x.extend(axc2); sys_y.extend(ayc2)
        total_len += (np.pi * r_eff) / 2

        # 6. Right Side Straight
        sys_x.append(back - gc); sys_y.append(side_c - gc if gc > 0.05 else side_c)
        total_len += (side_c - r_eff - gb - (gc if gc > 0.05 else 0))

        # 7. End Closure (Top Right)
        if gc > 0.05:
            ax2, ay2 = get_arc(back - gc, side_c, gc, 0, 90)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len += (np.pi * gc) / 2

    # Plot
    ax.plot(wall_x, wall_y, color='#BDBDBD', lw=2, ls='--', label="Booth Wall")
    ax.plot(sys_x, sys_y, color='#2e7d32', lw=5, solid_capstyle='round', label="ISOframe (Closed)")
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
    
    return fig, total_len

# --- Streamlit UI ---
st.title("📏 ISOframe Wave Pro - Final Version")

with st.sidebar:
    st.header("1. System Config")
    p_w = 0.8
    c_p = st.number_input("Panels per Corner", 1.5, 5.0, 2.0, 0.1)
    
    st.header("2. Layout")
    shape = st.selectbox("Booth Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    
    d, g = [], []
    if shape == "S - Straight":
        d = [st.number_input("Length", 1.0, 20.0, 8.0)]
        g = [st.slider("Wall Gap", 0.0, 1.0, 0.2)]
    elif shape == "L - Shaped":
        d = [st.number_input("Width (Side A)", 1.5, 20.0, 4.0), st.number_input("Depth (Side B)", 1.5, 20.0, 2.5)]
        g = [st.slider("Gap Side A", 0.0, 1.0, 0.2), st.slider("Gap Side B", 0.0, 1.0, 0.2)]
    else:
        d = [st.number_input("Left Arm", 1.5, 10.0, 2.0), st.number_input("Back Width", 3.0, 20.0, 5.0), st.number_input("Right Arm", 1.5, 10.0, 2.0)]
        g = [st.slider("Gap Left", 0.0, 1.0, 0.2), st.slider("Gap Back", 0.0, 1.0, 0.2), st.slider("Gap Right", 0.0, 1.0, 0.2)]

fig, t_len = draw_layout(shape, d, g, p_w, c_p)
panels = np.ceil(round(t_len, 4) / p_w)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total Panels", int(panels))
    st.write(f"**Total Path:** {t_len:.2f}m")
    st.caption("Corners automatically curve back to the booth wall to prevent access to the backside.")
with col2:
    st.pyplot(fig)
