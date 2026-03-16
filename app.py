import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="ISOframe Pro - U-Shape Fix", layout="wide")

def get_arc(cx, cy, r, start_deg, end_deg):
    """Generates smooth arc points. Handles radius of 0 safely."""
    if r <= 0: return [cx], [cy]
    angles = np.deg2rad(np.linspace(start_deg, end_deg, 20))
    return cx + r * np.cos(angles), cy + r * np.sin(angles)

def draw_layout(shape, dims, gaps, panel_w, corner_panels):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Standard 90-degree corner radius
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
            # Closure start -> straight -> closure end
            ax1, ay1 = get_arc(g, g, g, 180, 270)
            sys_x.extend(ax1); sys_y.extend(ay1)
            sys_x.extend([g, l - g]); sys_y.extend([0, 0])
            ax2, ay2 = get_arc(l - g, g, g, 270, 360)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len = (np.pi * g / 2) * 2 + (l - 2*g)
        else:
            sys_x, sys_y = [0, l], [0, 0]
            total_len = l

    elif shape == "L - Shaped":
        w, d = dims
        ga, gb = gaps
        wall_x, wall_y = [0, w, w], [0, 0, -d]
        # Closure Start
        if ga > 0.05:
            ax1, ay1 = get_arc(ga, 0, ga, 180, 270)
            sys_x.extend(ax1); sys_y.extend(ay1)
            total_len += (np.pi * ga / 2)
        else:
            sys_x.append(0); sys_y.append(0)
        # Main Corner
        sys_x.append(w - radius - gb); sys_y.append(-ga)
        axc, ayc = get_arc(w - radius - gb, -ga - radius, radius, 90, 0)
        sys_x.extend(axc); sys_y.extend(ayc)
        # Closure End
        sys_x.append(w - gb); sys_y.append(-d + gb if gb > 0.05 else -d)
        if gb > 0.05:
            ax2, ay2 = get_arc(w - gb, -d + gb, gb, 0, -90)
            sys_x.extend(ax2[::-1]); sys_y.extend(ay2[::-1])
            total_len += (np.pi * gb / 2)
        total_len += (w - radius - gb - (ga if ga > 0.05 else 0)) + main_arc_len + (d - radius - ga - (gb if gb > 0.05 else 0))

    elif shape == "U - Shaped":
        side_a, back, side_c = dims
        ga, gb, gc = gaps # Left, Back, Right gaps
        wall_x, wall_y = [0, 0, back, back], [side_a, 0, 0, side_c]
        
        # Ensure radius isn't too large for the booth
        r_eff = min(radius, (back - ga - gc) / 2.1, (side_a - gb), (side_c - gb))

        # 1. Closure Top Left (Wall to System)
        if ga > 0.05:
            ax1, ay1 = get_arc(ga, side_a, ga, 180, 270)
            sys_x.extend(ax1[::-1]); sys_y.extend(ay1[::-1])
            total_len += (np.pi * ga / 2)
        else:
            sys_x.append(0); sys_y.append(side_a)

        # 2. Left Wall Straight
        sys_x.append(ga); sys_y.append(r_eff + gb)
        total_len += (side_a - r_eff - gb - (ga if ga > 0.05 else 0))

        # 3. Bottom Left Corner
        axc1, ayc1 = get_arc(ga + r_eff, r_eff + gb, r_eff, 180, 270)
        sys_x.extend(axc1); sys_y.extend(ayc1)
        total_len += (np.pi * r_eff / 2)

        # 4. Back Wall Straight
        sys_x.append(back - gc - r_eff); sys_y.append(gb)
        total_len += (back - ga - gc - 2*r_eff)

        # 5. Bottom Right Corner
        axc2, ayc2 = get_arc(back - gc - r_eff, r_eff + gb, r_eff, 270, 360)
        sys_x.extend(axc2); sys_y.extend(ayc2)
        total_len += (np.pi * r_eff / 2)

        # 6. Right Wall Straight
        sys_x.append(back - gc); sys_y.append(side_c - gc if gc > 0.05 else side_c)
        total_len += (side_c - r_eff - gb - (gc if gc > 0.05 else 0))

        # 7. Closure Top Right (System to Wall)
        if gc > 0.05:
            ax2, ay2 = get_arc(back - gc, side_c, gc, 270, 360)
            sys_x.extend(ax2); sys_y.extend(ay2)
            total_len += (np.pi * gc / 2)

    # Styling
    ax.plot(wall_x, wall_y, color='#BDBDBD', lw=2, ls='--', label="Booth Wall")
    ax.plot(sys_x, sys_y, color='#2e7d32', lw=5, solid_capstyle='round', label="ISOframe System")
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
    
    return fig, total_len

# --- UI ---
st.title("📏 ISOframe Wave Pro")

with st.sidebar:
    st.header("1. System Config")
    panel_w = 0.8
    corner_p = st.number_input("Panels per Corner", 1.5, 5.0, 2.0, 0.1)
    
    st.header("2. Layout")
    shape = st.selectbox("Booth Shape", ["S - Straight", "L - Shaped", "U - Shaped"])
    
    d, g = [], []
    if shape == "S - Straight":
        d = [st.number_input("Length", 1.0, 20.0, 8.0)]
        g = [st.slider("Wall Gap", 0.0, 1.0, 0.2)]
    elif shape == "L - Shaped":
        d = [st.number_input("Width (A)", 1.5, 20.0, 4.0), st.number_input("Depth (B)", 1.5, 20.0, 2.5)]
        g = [st.slider("Gap Side A", 0.0, 1.0, 0.2), st.slider("Gap Side B", 0.0, 1.0, 0.2)]
    else:
        d = [st.number_input("Left Arm (A)", 1.5, 10.0, 2.0), st.number_input("Back Wall (B)", 3.0, 20.0, 5.0), st.number_input("Right Arm (C)", 1.5, 10.0, 2.0)]
        g = [st.slider("Gap Left (A)", 0.0, 1.0, 0.2), st.slider("Gap Back (B)", 0.0, 1.0, 0.2), st.slider("Gap Right (C)", 0.0, 1.0, 0.2)]

fig, t_len = draw_layout(shape, d, g, panel_w, corner_p)
panels = np.ceil(round(t_len, 4) / panel_w)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total Panels", int(panels))
    st.write(f"**Total Path:** {t_len:.2f}m")
    st.caption("The system now calculates a continuous path, including 90° curves back to the booth walls.")
with col2:
    st.pyplot(fig)
