import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import math

st.set_page_config(page_title="Indora Battery Pack Designer", layout="wide", page_icon="🔋")
st.title("🔋 Indora Battery Pack Calculator + 3D Designer")
st.caption("Made for Indora Global Exports - Workshop Use")

# SIDEBAR INPUTS
with st.sidebar:
    st.header("1. Cell Inputs")
    cell_type = st.selectbox("Cell Type", ["18650", "21700", "32700 LFP"])
    cell_v = st.number_input("Cell Nominal Voltage V", 3.2, 3.7, 3.7, 0.1)
    cell_ah = st.number_input("Cell Capacity Ah", 1.0, 10.0, 2.0, 0.1)
    cell_ir = st.number_input("Cell Max Discharge A", 5, 40, 10)
    cell_price = st.number_input("Cell Price Rs", 100, 500, 180)

    st.header("2. Pack Target")
    target_v = st.number_input("Target Pack Voltage V", 12, 72, 48)
    target_ah = st.number_input("Target Pack Capacity Ah", 5, 100, 20)
    target_a = st.number_input("Target Max Current A", 10, 200, 30)

# CALCULATIONS
s = math.ceil(target_v / cell_v)
p = math.ceil(target_ah / cell_ah)
total_cells = s * p
pack_v = s * cell_v
pack_ah = p * cell_ah
pack_wh = pack_v * pack_ah
pack_a = p * cell_ir
bms = math.ceil(target_a * 1.25 / 5) * 5
nickel_w = 8 if target_a <= 10 else 10 if target_a <= 20 else 15 if target_a <= 40 else 20
nickel_t = 0.15 if target_a <= 20 else 0.2 if target_a <= 40 else 0.3
cost = total_cells * cell_price

# LAYOUT
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📊 Calculator Results")
    data = {
        "Parameter": ["Config", "Total Cells", "Pack Voltage", "Pack Capacity", "Pack Energy", "Max Discharge", "BMS Suggestion", "Nickel Strip", "Est. Cell Cost"],
        "Value": [f"{s}S {p}P", total_cells, f"{pack_v:.1f} V", f"{pack_ah:.1f} Ah", f"{pack_wh:.0f} Wh", f"{pack_a:.0f} A", f"{bms} A", f"{nickel_w}mm x {nickel_t}mm", f"Rs {cost:,}"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    if pack_a < target_a:
        st.error(f"⚠️ Warning: Increase P. Current pack can only do {pack_a}A. Need at least {math.ceil(target_a/cell_ir)}P")
    else:
        st.success("✅ Pack specs are OK")

    st.download_button("📥 Download BOM as CSV", df.to_csv(index=False), "Indora_BOM.csv")

with col2:
    st.header("🧊 3D Cell Layout")
    
    cell_d = 18.6 if cell_type == "18650" else 21.2 if cell_type == "21700" else 32
    cell_h = 65 if cell_type == "18650" else 70 if cell_type == "21700" else 70
    
    x, y, z, color, text = [], [], [], [], []
    cell_count = 0
    for row in range(p):
        for col in range(s):
            x.append(col * cell_d)
            y.append(row * cell_d)
            z.append(0)
            color.append('red' if col % 2 == 0 else 'blue')
            text.append(f"S{col+1} P{row+1}")
            cell_count += 1
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=cell_d, color=color, opacity=0.85, line=dict(width=1, color='black')),
        text=text,
        hoverinfo='text'
    )])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Series S', 
            yaxis_title='Parallel P', 
            zaxis_title='',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ), 
        height=500, margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔴 Red = Start of Series Group, 🔵 Blue = End. Connect Red to Blue for Series")

st.header("📄 Wiring Guide for Workers")
st.info(f"""
**How to wire {s}S {p}P Pack:**
1.  Make `{p}` groups. Each group has `{s}` cells in Parallel. Weld all + together, all - together.
2.  Connect in Series: Group1 +  →  Group2 - .  Group2 +  →  Group3 - ... till `{s}` groups.
3.  BMS Wiring: B- to Pack -, B1 to after cell1, B2 to after cell2 ... B{s} to Pack +
4.  P- to Controller, C- to Charger
5.  Use Nickel: `{nickel_w}mm x {nickel_t}mm` for main current paths
""")
st.success("Tip: Take a screenshot of the 3D view and print it for your spot welding table")

