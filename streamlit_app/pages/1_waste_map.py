import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0a0f0d; color: #e8ede9; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
[data-testid="metric-container"] { background: #111a15 !important; border: 1px solid #1e2e24 !important; border-radius: 12px !important; padding: 1rem !important; }
[data-testid="metric-container"] label { color: #6b8f74 !important; font-size: 0.72rem !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ede9 !important; font-size: 1.6rem !important; font-weight: 600 !important; font-family: 'DM Mono', monospace !important; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

@st.cache_data(ttl=60)
def load_points():
    return requests.get(f"{API}/waste/collection-points", timeout=5).json()

@st.cache_data(ttl=60)
def load_ward_summary():
    return requests.get(f"{API}/waste/ward-summary", timeout=5).json()

st.markdown('<div class="page-header"><h1>Waste Map</h1><span>Real-Time</span></div>', unsafe_allow_html=True)

try:
    points = load_points()
    ward_summary = load_ward_summary()
except:
    st.error("API not reachable.")
    st.stop()

df = pd.DataFrame(points)
ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Points", len(df))
with c2:
    high = len(df[df["fill_level"] > 75])
    st.metric("High Priority (>75%)", high)
with c3: st.metric("Avg Fill Level", f"{df['fill_level'].mean():.1f}%")
with c4: st.metric("Wards Covered", df["ward_name"].nunique())

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
col_map, col_detail = st.columns([3, 2], gap="large")

with col_map:
    st.markdown("**Collection Point Map**")
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles="CartoDB dark_matter")
    for _, row in df.iterrows():
        fill = row["fill_level"]
        color = "#ef4444" if fill > 75 else "#f59e0b" if fill > 50 else "#4ade80"
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6 + (fill/100)*8, color=color, fill=True,
            fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(f"<b>{row['name']}</b><br>Ward: {row['ward_name']}<br>Fill: {fill:.1f}%", max_width=200),
            tooltip=f"{row['name']} — {fill:.0f}%"
        ).add_to(m)
    legend_html = """<div style='position:fixed;bottom:20px;left:20px;background:rgba(10,15,13,0.9);
        border:1px solid #1e2e24;padding:10px 14px;border-radius:8px;font-family:sans-serif;
        font-size:11px;color:#e8ede9;z-index:1000;'>
        <div style='font-weight:600;margin-bottom:6px;color:#4ade80;'>Fill Level</div>
        <div><span style='color:#4ade80'>●</span> &lt;50% Normal</div>
        <div><span style='color:#f59e0b'>●</span> 50–75% Moderate</div>
        <div><span style='color:#ef4444'>●</span> &gt;75% Urgent</div></div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, height=450, use_container_width=True)

with col_detail:
    st.markdown("**Ward Waste Composition**")
    ward_names = sorted(df["ward_name"].unique().tolist())
    ward_sel = st.selectbox("Select Ward", ward_names, label_visibility="collapsed")

    if not ws_df.empty:
        # Get ward_id for selected ward name
        ward_rows = df[df["ward_name"] == ward_sel]
        if not ward_rows.empty:
            ward_id = ward_rows["ward_id"].values[0]
            # ward_summary uses ward_id to group
            comp_row = ws_df[ws_df["ward_id"] == ward_id]
            if not comp_row.empty:
                r = comp_row.iloc[0]
            else:
                # fallback: use first row for display
                r = ws_df.iloc[0]
            cats = ["Organic","Plastic","Paper","Metal","Glass","Hazardous"]
            vals = [float(r["avg_organic"]),float(r["avg_plastic"]),float(r["avg_paper"]),
                    float(r["avg_metal"]),float(r["avg_glass"]),float(r["avg_hazardous"])]
            colors = ["#4ade80","#60a5fa","#fbbf24","#a78bfa","#34d399","#f87171"]
            fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors,
                hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#9ca3af", size=11),
                margin=dict(l=0,r=0,t=10,b=0), height=220,
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                yaxis=dict(gridcolor="#1e2e24", title="% Composition"),
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("**High Priority Points**")
    high_df = df[df["fill_level"] > 75].sort_values("fill_level", ascending=False)[["name","ward_name","fill_level"]].copy()
    high_df.columns = ["Point","Ward","Fill %"]
    high_df["Fill %"] = high_df["Fill %"].round(1)
    st.dataframe(high_df, use_container_width=True, hide_index=True, height=200)