import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import pandas as pd

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
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

st.markdown('<div class="page-header"><h1>Driver View</h1><span>Today\'s Route</span></div>', unsafe_allow_html=True)

TRUCK_COLORS = ["#4ade80","#60a5fa","#f59e0b","#f87171","#a78bfa","#34d399"]

# ── Load or fetch routes ─────────────────────────────────────────────────────
if "driver_routes" not in st.session_state:
    st.session_state.driver_routes = None

col_ctrl, col_info = st.columns([3, 4], gap="large")
with col_ctrl:
    num_trucks = st.slider("Number of Trucks", 2, 6, 3, key="driver_num_trucks")
    if st.button("Load Today's Routes from Optimizer"):
        with st.spinner("Fetching optimized routes..."):
            try:
                r = requests.get(f"{API}/routes/optimize?num_trucks={num_trucks}", timeout=30)
                st.session_state.driver_routes = r.json()
                st.session_state.driver_completed = {}
            except Exception as e:
                st.error(f"Could not load routes: {e}")

with col_info:
    now = datetime.now().strftime("%A, %d %B · %I:%M %p")
    st.markdown(f"""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:10px;padding:0.75rem 1rem;font-size:0.82rem;color:#6b8f74;margin-top:0.5rem;">
        📅 {now}<br>
        <span style="color:#4ade80;">Routes are generated from live fill level data — same as Route Optimizer page.</span>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.driver_routes:
    st.markdown("""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:2rem;text-align:center;color:#6b8f74;margin-top:1rem;">
        Press <b style="color:#e8ede9;">Load Today's Routes</b> to pull the optimized route from the system.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

routes = st.session_state.driver_routes
if "driver_completed" not in st.session_state:
    st.session_state.driver_completed = {}

# ── Truck selector ────────────────────────────────────────────────────────────
truck_ids = [r["truck_id"] for r in routes]
selected_truck_id = st.selectbox("Select your truck", truck_ids)
route = next((r for r in routes if r["truck_id"] == selected_truck_id), routes[0])
truck_idx = truck_ids.index(selected_truck_id)
truck_color = TRUCK_COLORS[truck_idx % len(TRUCK_COLORS)]

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
completed_key = selected_truck_id
if completed_key not in st.session_state.driver_completed:
    st.session_state.driver_completed[completed_key] = set()
done_set = st.session_state.driver_completed[completed_key]

seq = route.get("collection_sequence", [])
total_stops = len(seq)
done_count = len(done_set)

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Stops", total_stops)
with c2: st.metric("Completed", done_count)
with c3: st.metric("Distance", f"{route.get('total_distance_km', 0):.1f} km")
with c4: st.metric("Est. Time", f"{route.get('estimated_time_minutes', 0):.0f} min")

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

col_map, col_stops = st.columns([3, 2], gap="large")

with col_map:
    st.markdown(f"**Route Map — {selected_truck_id}**")
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=11, tiles="CartoDB dark_matter")

    coords = []
    for s in seq:
        lat = s.get("lat") or s.get("latitude")
        lon = s.get("lon") or s.get("longitude")
        if lat and lon:
            coords.append([lat, lon])

    if len(coords) > 1:
        folium.PolyLine(coords, color=truck_color, weight=3, opacity=0.85, dash_array="6 3").add_to(m)

    for j, (stop, coord) in enumerate(zip(seq, coords)):
        is_done = j in done_set
        fill = stop.get("fill_level", stop.get("fill", 70))
        dot_color = "#6b8f74" if is_done else truck_color
        folium.Marker(
            location=coord,
            popup=folium.Popup(
                f"<b>Stop {j+1}: {stop.get('name','')}</b><br>Ward: {stop.get('ward','')}<br>Fill: {fill:.0f}%",
                max_width=200
            ),
            tooltip=f"{'✓ ' if is_done else ''}Stop {j+1} — {stop.get('name','')}",
            icon=folium.DivIcon(
                html=f"""<div style="background:{dot_color};color:#000;font-weight:700;font-size:11px;
                            width:24px;height:24px;border-radius:50%;display:flex;align-items:center;
                            justify-content:center;border:2px solid {'#fff' if not is_done else '#444'};
                            font-family:sans-serif;opacity:{'0.4' if is_done else '1'};">
                            {'✓' if is_done else j+1}</div>""",
                icon_size=(24, 24), icon_anchor=(12, 12)
            )
        ).add_to(m)

    st_folium(m, height=440, use_container_width=True)

with col_stops:
    st.markdown("**Stop List**")

    for j, stop in enumerate(seq):
        is_done = j in done_set
        fill = float(stop.get("fill_level", stop.get("fill", 70)))
        is_urgent = fill > 80
        fill_color = "#ef4444" if is_urgent else "#f59e0b" if fill > 60 else "#4ade80"
        stop_name = stop.get("name", f"Stop {j+1}")
        ward_name = stop.get("ward", "")
        fill_str = f"{fill:.0f}%"
        badge = "✓" if is_done else str(j+1)

        # Use native columns — no HTML f-string at all
        ca, cb, cc = st.columns([1, 6, 2])
        with ca:
            st.markdown(f"""<div style="margin-top:6px;background:{truck_color}20;border-radius:50%;
                width:26px;height:26px;display:flex;align-items:center;justify-content:center;
                font-size:0.8rem;color:{truck_color};font-weight:700;">{badge}</div>""",
                unsafe_allow_html=True)
        with cb:
            name_style = "color:#6b8f74;" if is_done else "color:#e8ede9;"
            st.markdown(f"""<div style="padding-top:4px;">
                <div style="font-size:0.82rem;font-weight:600;{name_style}">{stop_name}</div>
                <div style="font-size:0.7rem;color:#6b8f74;">{ward_name}{' · ⚠ Urgent' if is_urgent and not is_done else ''}</div>
            </div>""", unsafe_allow_html=True)
        with cc:
            st.markdown(f"""<div style="padding-top:6px;text-align:right;
                font-family:'DM Mono',monospace;font-size:0.88rem;
                color:{fill_color};font-weight:700;">{fill_str}</div>""",
                unsafe_allow_html=True)

        btn_label = "↩ Undo" if is_done else "✓ Done"
        if st.button(btn_label, key=f"dv_{selected_truck_id}_{j}"):
            if j in done_set:
                done_set.discard(j)
            else:
                done_set.add(j)
            st.session_state.driver_completed[completed_key] = done_set
            st.rerun()
        st.markdown("<hr style='border-color:#1e2e24;margin:0.1rem 0 0.4rem 0;'>", unsafe_allow_html=True)

    if done_count == total_stops and total_stops > 0:
        st.markdown("""
        <div style="margin-top:0.75rem;background:#0d2010;border:1px solid #4ade8040;border-radius:8px;
                    padding:0.75rem;text-align:center;font-size:0.82rem;color:#4ade80;font-weight:600;">
            🎉 All stops completed! Return to depot.
        </div>
        """, unsafe_allow_html=True)
    elif done_count > 0:
        st.markdown(f"""
        <div style="margin-top:0.75rem;background:#0d1a10;border:1px solid #4ade8020;border-radius:8px;
                    padding:0.6rem;text-align:center;font-size:0.78rem;color:#6b8f74;">
            {done_count}/{total_stops} stops done
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:0.75rem;background:#1a0800;border:1px solid #ef444430;border-radius:8px;
                padding:0.7rem 0.9rem;font-size:0.74rem;color:#fca5a5;">
        <b>Reminder:</b> Red bin (hazardous) waste must be transferred to the
        DPCC-designated vehicle at depot. Do NOT mix with general waste load.
    </div>
    """, unsafe_allow_html=True)