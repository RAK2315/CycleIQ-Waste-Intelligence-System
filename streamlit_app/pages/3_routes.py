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
#MainMenu, footer { visibility: hidden; }
header { visibility: visible; }
.stApp { background: #0a0f0d; color: #e8ede9; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
[data-testid="metric-container"] { background: #111a15 !important; border: 1px solid #1e2e24 !important; border-radius: 12px !important; padding: 1rem !important; }
[data-testid="metric-container"] label { color: #6b8f74 !important; font-size: 0.72rem !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ede9 !important; font-size: 1.6rem !important; font-weight: 600 !important; font-family: 'DM Mono', monospace !important; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; padding: 0.5rem 1.5rem !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.truck-card { background:#111a15; border:1px solid #1e2e24; border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.75rem; }
.truck-card .truck-id { font-family:'DM Mono',monospace; font-size:0.85rem; color:#4ade80; font-weight:600; margin-bottom:0.5rem; }
.truck-card .truck-stat { font-size:0.78rem; color:#6b8f74; margin:2px 0; }
.truck-card .truck-stat span { color:#e8ede9; font-weight:500; }
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
TRUCK_COLORS = ["#4ade80","#60a5fa","#f59e0b","#f87171","#a78bfa","#34d399"]


# ── Shared sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1.2rem 0;border-bottom:1px solid #1e2e24;margin-bottom:1rem;">
        <div style="font-size:1.5rem;font-weight:700;color:#e8ede9;letter-spacing:-0.02em;">♻️ CycleIQ</div>
        <div style="font-size:0.7rem;color:#4ade80;font-family:'DM Mono',monospace;margin-top:3px;">Delhi Waste Intelligence</div>
        <div style="margin-top:0.75rem;display:flex;gap:0.4rem;flex-wrap:wrap;">
            <span style="background:#0d2010;border:1px solid #4ade8030;color:#4ade80;font-size:0.62rem;padding:1px 7px;border-radius:10px;">IoT Live</span>
            <span style="background:#0d1a2e;border:1px solid #60a5fa30;color:#60a5fa;font-size:0.62rem;padding:1px 7px;border-radius:10px;">YOLOv8</span>
            <span style="background:#1a0f00;border:1px solid #fbbf2430;color:#fbbf24;font-size:0.62rem;padding:1px 7px;border-radius:10px;">OR-Tools</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.65rem;color:#4ade80;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.4rem;padding-left:2px;">Main</div>', unsafe_allow_html=True)
    st.page_link("app.py", label="Live Overview", icon="📊")
    st.page_link("pages/0_home.py", label="About CycleIQ", icon="ℹ️")
    st.page_link("pages/1_waste_map.py", label="Waste Map", icon="🗺️")
    st.markdown('<div style="font-size:0.65rem;color:#6b8f74;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:0.75rem 0 0.4rem 0;padding-left:2px;">Intelligence</div>', unsafe_allow_html=True)
    st.page_link("pages/2_forecasting.py", label="Forecasting", icon="📈")
    st.page_link("pages/3_routes.py", label="Route Optimizer", icon="🛣️")
    st.page_link("pages/4_llm_chat.py", label="AI Assistant", icon="🤖")
    st.page_link("pages/6_cv_classify.py", label="Waste Classifier", icon="📷")
    st.page_link("pages/9_bin_monitor.py", label="Bin Monitor", icon="🎥")
    st.markdown('<div style="font-size:0.65rem;color:#6b8f74;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:0.75rem 0 0.4rem 0;padding-left:2px;">People</div>', unsafe_allow_html=True)
    st.page_link("pages/5_citizens.py", label="Citizens & Rewards", icon="👥")
    st.markdown('<div style="font-size:0.65rem;color:#6b8f74;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:0.75rem 0 0.4rem 0;padding-left:2px;">Operations</div>', unsafe_allow_html=True)
    st.page_link("pages/8_driver_view.py", label="Driver View", icon="🚛")
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0d1410;border:1px solid #1e2e24;border-radius:10px;padding:0.75rem;font-size:0.72rem;">
        <div style="color:#4ade80;font-weight:600;margin-bottom:0.5rem;">System Status</div>
        <div style="color:#6b8f74;line-height:2;">
            <div>🟢 API &nbsp;<span style="color:#4ade80">Online</span></div>
            <div>🟢 Database &nbsp;<span style="color:#4ade80">Neon PG</span></div>
            <div>🟢 LLM &nbsp;<span style="color:#4ade80">Groq/Llama</span></div>
            <div>🟡 CV &nbsp;<span style="color:#fbbf24">YOLOv8n</span></div>
            <div>🟢 Forecast &nbsp;<span style="color:#4ade80">Prophet</span></div>
            <div>🟢 Routes &nbsp;<span style="color:#4ade80">OR-Tools</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="page-header"><h1>Route Optimizer</h1><span>OR-Tools</span></div>', unsafe_allow_html=True)

# Check dispatch alert
try:
    alert = requests.get(f"{API}/dashboard/dispatch-alert", timeout=3).json()
    if alert.get("should_dispatch"):
        reason = alert.get("reason", "")
        haz_wards = alert.get("hazardous_wards", [])
        st.markdown(f"""
        <div style="background:#1a0800;border:1px solid #ef444440;border-radius:10px;
                    padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:#fca5a5;">
            ⚠ <b>Dispatch Recommended:</b> {reason}.
            {'Hazardous wards: <b>' + ', '.join(haz_wards[:3]) + '</b>' if haz_wards else ''}
            — Route generation will prioritise these bins automatically.
        </div>
        """, unsafe_allow_html=True)
except:
    pass

col_ctrl, _ = st.columns([2, 5])
with col_ctrl:
    num_trucks = st.slider("Number of Trucks", 2, 6, 3)
    run_btn = st.button("Generate Optimized Routes")

if "routes" not in st.session_state:
    st.session_state.routes = None

if run_btn:
    with st.spinner("Optimizing routes..."):
        try:
            r = requests.get(f"{API}/routes/optimize?num_trucks={num_trucks}", timeout=30)
            st.session_state.routes = r.json()
        except Exception as e:
            st.error(f"Optimization failed: {e}")

if st.session_state.routes:
    routes = st.session_state.routes

    total_dist = sum(r["total_distance_km"] for r in routes)
    total_emissions = sum(r["estimated_emissions_kg"] for r in routes)
    total_stops = sum(r["num_stops"] for r in routes)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Distance", f"{total_dist:.1f} km")
    with c2: st.metric("Est. Emissions", f"{total_emissions:.1f} kg CO₂")
    with c3: st.metric("Total Stops", total_stops)
    with c4: st.metric("Emission Saving", "~22%", delta="vs manual routing")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    col_map, col_list = st.columns([3, 2], gap="large")

    with col_map:
        m = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles="CartoDB dark_matter")
        for i, route in enumerate(routes):
            color = TRUCK_COLORS[i % len(TRUCK_COLORS)]
            seq = route.get("collection_sequence", [])
            # Safely get lat/lon with fallbacks
            coords = []
            for s in seq:
                lat = s.get("lat") or s.get("latitude")
                lon = s.get("lon") or s.get("longitude")
                if lat and lon:
                    coords.append([lat, lon])
            if len(coords) > 1:
                folium.PolyLine(coords, color=color, weight=2.5, opacity=0.8,
                                tooltip=route["truck_id"]).add_to(m)
            for j, (stop, coord) in enumerate(zip(seq, coords)):
                folium.CircleMarker(
                    location=coord, radius=5,
                    color=color, fill=True, fill_color=color, fill_opacity=0.9,
                    popup=f"Stop {j+1}: {stop.get('name','')}<br>Ward: {stop.get('ward','')}",
                    tooltip=f"{route['truck_id']} — Stop {j+1}"
                ).add_to(m)
        st_folium(m, height=440, use_container_width=True)

    with col_list:
        st.markdown("**Route Details**")
        for i, route in enumerate(routes):
            color = TRUCK_COLORS[i % len(TRUCK_COLORS)]
            haz_stops = route.get("hazardous_stops", 0)
            shift_start = "06:00 AM"
            from datetime import datetime, timedelta
            t = datetime.strptime(shift_start, "%I:%M %p") + timedelta(minutes=route['estimated_time_minutes'])
            end_time = t.strftime("%I:%M %p")
            st.markdown(f"""
            <div class="truck-card" style="border-left:3px solid {color};">
                <div class="truck-id">{route['truck_id']}</div>
                <div class="truck-stat">Stops: <span>{route['num_stops']}</span>{' &nbsp;🔴 <span style="color:#f87171;">' + str(haz_stops) + ' hazardous</span>' if haz_stops > 0 else ''}</div>
                <div class="truck-stat">Distance: <span>{route['total_distance_km']:.1f} km</span></div>
                <div class="truck-stat">Est. Time: <span>{route['estimated_time_minutes']:.0f} min</span></div>
                <div class="truck-stat">Shift: <span>06:00 AM → {end_time}</span></div>
                <div class="truck-stat">Emissions: <span>{route['estimated_emissions_kg']:.2f} kg CO₂</span></div>
            </div>
            """, unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=[r["truck_id"] for r in routes],
            y=[r["estimated_emissions_kg"] for r in routes],
            marker_color=TRUCK_COLORS[:len(routes)],
            hovertemplate="%{x}: %{y:.2f} kg CO₂<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af", size=11),
            margin=dict(l=0, r=0, t=20, b=0), height=160,
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="#1e2e24", title="kg CO₂"),
            title=dict(text="Emissions per Truck", font=dict(size=12, color="#6b8f74"))
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#2d4a36;border:1px dashed #1e2e24;border-radius:14px;margin-top:1rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🚛</div>
        <div style="font-size:0.9rem;">Set the number of trucks and click Generate Optimized Routes</div>
    </div>
    """, unsafe_allow_html=True)