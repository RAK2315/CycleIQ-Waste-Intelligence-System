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

import os, requests as _req

def _get_api():
    render = os.getenv("API_URL", "https://cycleiq-api.onrender.com") + "/api"
    local  = "http://localhost:8000/api"
    try:
        _req.get(f"{local}/waste/stats", timeout=2)
        return local
    except Exception:
        return render

API = _get_api()

@st.cache_data(ttl=30)
def load_points():
    return requests.get(f"{API}/waste/collection-points", timeout=5).json()

@st.cache_data(ttl=60)
def load_ward_summary():
    return requests.get(f"{API}/waste/ward-summary", timeout=5).json()

st.markdown('<div class="page-header"><h1>Waste Map</h1><span>Real-Time · IoT Feed</span></div>', unsafe_allow_html=True)

try:
    points = load_points()
    ward_summary = load_ward_summary()
except:
    st.error("API not reachable.")
    st.stop()

df = pd.DataFrame(points)
ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()

# ── KPIs ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Total Points", len(df))
with c2:
    high = len(df[df["fill_level"] > 75])
    st.metric("High Priority (>75%)", high)
with c3: st.metric("Avg Fill Level", f"{df['fill_level'].mean():.1f}%")
with c4: st.metric("Wards Covered", df["ward_name"].nunique())
with c5:
    haz_count = int(ws_df[ws_df["avg_hazardous"] > 10].shape[0]) if not ws_df.empty else 0
    st.metric("Hazardous Alerts", haz_count)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Map layer selector ───────────────────────────────────────────────────────
layer = st.radio(
    "Map Layer",
    ["Fill Levels", "Hazardous Contamination", "Both"],
    horizontal=True,
    label_visibility="collapsed"
)

col_map, col_detail = st.columns([3, 2], gap="large")

with col_map:
    st.markdown(f"**Collection Point Map — {layer}**")
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles="CartoDB dark_matter")

    # Build ward hazardous lookup
    haz_lookup = {}
    if not ws_df.empty:
        for _, r in ws_df.iterrows():
            haz_lookup[r["ward_id"]] = float(r["avg_hazardous"])

    for _, row in df.iterrows():
        fill = row["fill_level"]
        haz_pct = haz_lookup.get(row["ward_id"], 0)

        if layer == "Fill Levels":
            color = "#ef4444" if fill > 75 else "#f59e0b" if fill > 50 else "#4ade80"
            radius = 6 + (fill/100)*8
        elif layer == "Hazardous Contamination":
            color = "#ef4444" if haz_pct > 10 else "#f59e0b" if haz_pct > 6 else "#4ade80"
            radius = 6 + (haz_pct/20)*8
        else:  # Both — fill drives size, hazardous drives color if alert
            color = "#ef4444" if haz_pct > 10 else "#f59e0b" if fill > 75 else "#4ade80"
            radius = 6 + (fill/100)*8

        popup_html = f"""
        <div style="font-family:sans-serif;font-size:12px;min-width:160px;">
            <b style="color:#111;">{row['name']}</b><br>
            Ward: {row['ward_name']}<br>
            Fill Level: <b>{fill:.0f}%</b><br>
            Hazardous: <b style="color:{'red' if haz_pct > 10 else 'orange' if haz_pct > 6 else 'green'};">{haz_pct:.1f}%</b><br>
            {'<b style="color:red;">⚠ Special vehicle required</b>' if haz_pct > 10 else ''}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius, color=color, fill=True,
            fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{row['name']} — Fill:{fill:.0f}% Haz:{haz_pct:.1f}%"
        ).add_to(m)

    # Legend
    if layer == "Fill Levels":
        legend = """<div style='position:fixed;bottom:20px;left:20px;background:rgba(10,15,13,0.92);
            border:1px solid #1e2e24;padding:10px 14px;border-radius:8px;font-family:sans-serif;
            font-size:11px;color:#e8ede9;z-index:1000;'>
            <div style='font-weight:600;margin-bottom:6px;color:#4ade80;'>Fill Level</div>
            <div><span style='color:#4ade80'>●</span> &lt;50% Normal</div>
            <div><span style='color:#f59e0b'>●</span> 50–75% Moderate</div>
            <div><span style='color:#ef4444'>●</span> &gt;75% Urgent</div></div>"""
    elif layer == "Hazardous Contamination":
        legend = """<div style='position:fixed;bottom:20px;left:20px;background:rgba(10,15,13,0.92);
            border:1px solid #1e2e24;padding:10px 14px;border-radius:8px;font-family:sans-serif;
            font-size:11px;color:#e8ede9;z-index:1000;'>
            <div style='font-weight:600;margin-bottom:6px;color:#f87171;'>Hazardous %</div>
            <div><span style='color:#4ade80'>●</span> &lt;6% Safe</div>
            <div><span style='color:#f59e0b'>●</span> 6–10% Monitor</div>
            <div><span style='color:#ef4444'>●</span> &gt;10% Special vehicle</div></div>"""
    else:
        legend = """<div style='position:fixed;bottom:20px;left:20px;background:rgba(10,15,13,0.92);
            border:1px solid #1e2e24;padding:10px 14px;border-radius:8px;font-family:sans-serif;
            font-size:11px;color:#e8ede9;z-index:1000;'>
            <div style='font-weight:600;margin-bottom:6px;color:#e8ede9;'>Combined</div>
            <div><span style='color:#ef4444'>●</span> Hazardous alert</div>
            <div><span style='color:#f59e0b'>●</span> High fill</div>
            <div><span style='color:#4ade80'>●</span> Normal</div></div>"""
    m.get_root().html.add_child(folium.Element(legend))
    st_folium(m, height=450, use_container_width=True)

with col_detail:
    # 3-bin composition chart
    st.markdown("**Ward Waste Composition — 3 Bin Types**")
    ward_names = sorted(df["ward_name"].unique().tolist())
    ward_sel = st.selectbox("Select Ward", ward_names, label_visibility="collapsed")

    if not ws_df.empty:
        ward_rows = df[df["ward_name"] == ward_sel]
        if not ward_rows.empty:
            ward_id = ward_rows["ward_id"].values[0]
            comp_row = ws_df[ws_df["ward_id"] == ward_id]
            r = comp_row.iloc[0] if not comp_row.empty else ws_df.iloc[0]

            organic = float(r["avg_organic"])
            recyclable = float(r["avg_plastic"]) + float(r["avg_paper"]) + float(r["avg_metal"]) + float(r["avg_glass"])
            hazardous = float(r["avg_hazardous"])

            # 3-bin summary first
            col_g, col_b, col_r = st.columns(3)
            with col_g:
                st.markdown(f"""<div style="background:#0d2010;border:1px solid #4ade8040;border-radius:10px;
                    padding:0.75rem;text-align:center;">
                    <div style="font-size:0.65rem;color:#4ade80;font-weight:600;">🟢 GREEN BIN</div>
                    <div style="font-size:1.4rem;font-weight:700;color:#4ade80;font-family:'DM Mono',monospace;">{organic:.0f}%</div>
                    <div style="font-size:0.65rem;color:#6b8f74;">Organic/Wet</div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""<div style="background:#0d1a2e;border:1px solid #60a5fa40;border-radius:10px;
                    padding:0.75rem;text-align:center;">
                    <div style="font-size:0.65rem;color:#60a5fa;font-weight:600;">🔵 BLUE BIN</div>
                    <div style="font-size:1.4rem;font-weight:700;color:#60a5fa;font-family:'DM Mono',monospace;">{recyclable:.0f}%</div>
                    <div style="font-size:0.65rem;color:#6b8f74;">Dry/Recyclable</div>
                </div>""", unsafe_allow_html=True)
            with col_r:
                haz_color = "#ef4444" if hazardous > 10 else "#f59e0b" if hazardous > 6 else "#f87171"
                haz_bg = "#1a0800" if hazardous > 10 else "#111a15"
                haz_border = "#ef444450" if hazardous > 10 else "#f8717140"
                st.markdown(f"""<div style="background:{haz_bg};border:1px solid {haz_border};border-radius:10px;
                    padding:0.75rem;text-align:center;">
                    <div style="font-size:0.65rem;color:{haz_color};font-weight:600;">🔴 RED BIN</div>
                    <div style="font-size:1.4rem;font-weight:700;color:{haz_color};font-family:'DM Mono',monospace;">{hazardous:.0f}%</div>
                    <div style="font-size:0.65rem;color:#6b8f74;">Hazardous</div>
                </div>""", unsafe_allow_html=True)

            if hazardous > 10:
                st.markdown(f"""<div style="margin-top:0.5rem;background:#1a0800;border:1px solid #ef444440;
                    border-radius:8px;padding:0.5rem 0.8rem;font-size:0.75rem;color:#fca5a5;">
                    ⚠ {ward_sel} requires DPCC-authorised special collection vehicle for hazardous waste disposal.
                </div>""", unsafe_allow_html=True)

            # Detailed breakdown bar chart
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            cats = ["Organic","Plastic","Paper","Metal","Glass","Hazardous"]
            vals = [float(r["avg_organic"]),float(r["avg_plastic"]),float(r["avg_paper"]),
                    float(r["avg_metal"]),float(r["avg_glass"]),float(r["avg_hazardous"])]
            colors_bar = ["#4ade80","#60a5fa","#fbbf24","#a78bfa","#34d399","#f87171"]
            fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors_bar,
                hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#9ca3af", size=11),
                margin=dict(l=0,r=0,t=10,b=0), height=180,
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                yaxis=dict(gridcolor="#1e2e24", title="% Composition"),
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("**High Priority Points**")
    high_df = df[df["fill_level"] > 75].sort_values("fill_level", ascending=False)[["name","ward_name","fill_level"]].copy()
    high_df.columns = ["Point","Ward","Fill %"]
    high_df["Fill %"] = high_df["Fill %"].round(1)
    st.dataframe(high_df, use_container_width=True, hide_index=True, height=170)