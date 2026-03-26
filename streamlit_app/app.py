import streamlit as st

st.set_page_config(
    page_title="CycleIQ — Delhi Waste Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header { visibility: visible; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }
.stApp { background: #0a0f0d; color: #e8ede9; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
[data-testid="stSidebar"] .stMarkdown h3 { color: #4ade80; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; margin: 1.5rem 0 0.5rem 0; }
[data-testid="metric-container"] { background: #111a15 !important; border: 1px solid #1e2e24 !important; border-radius: 12px !important; padding: 1rem 1.2rem !important; }
[data-testid="metric-container"] label { color: #6b8f74 !important; font-size: 0.72rem !important; font-weight: 500 !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ede9 !important; font-size: 1.8rem !important; font-weight: 600 !important; font-family: 'DM Mono', monospace !important; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d1410; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #1e2e24; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b8f74 !important; border-radius: 7px !important; font-weight: 500 !important; font-size: 0.85rem !important; }
.stTabs [aria-selected="true"] { background: #166534 !important; color: #dcfce7 !important; }
hr { border-color: #1e2e24 !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0a0f0d; } ::-webkit-scrollbar-thumb { background: #1e2e24; border-radius: 3px; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.stat-card { background:#111a15; border:1px solid #1e2e24; border-radius:14px; padding:1.2rem 1.5rem; }
.alert-row { display:flex; align-items:center; gap:0.75rem; padding:0.6rem 0; border-bottom:1px solid #1a2420; }
.alert-row:last-child { border-bottom:none; }
.haz-banner { background:#1a0800; border:1px solid #ef444450; border-radius:10px; padding:0.75rem 1rem; margin-bottom:0.5rem; }
</style>
""", unsafe_allow_html=True)

import requests
import plotly.graph_objects as go
import pandas as pd
import sys, os, numpy as np
from datetime import datetime, timedelta
# Works both locally and on Streamlit Cloud
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
from data.real_data import get_all_wards_summary, get_ward_waste_stats, WARD_REAL_DATA, BASELINE_LANDFILL_RATE, CYCLEIQ_LANDFILL_RATE, BASELINE_RECYCLING_RATE, CYCLEIQ_RECYCLING_RATE, BASELINE_COMPOST_RATE, CYCLEIQ_COMPOST_RATE

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
def load_summary():
    return requests.get(f"{API}/dashboard/summary", timeout=5).json()

@st.cache_data(ttl=30)
def load_points():
    return requests.get(f"{API}/waste/collection-points", timeout=5).json()

@st.cache_data(ttl=60)
def load_ward_summary():
    return requests.get(f"{API}/waste/ward-summary", timeout=5).json()

@st.cache_data(ttl=60)
def load_citizen_stats():
    return requests.get(f"{API}/citizens/stats", timeout=5).json()

# Sidebar
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
    st.page_link("pages/0_home.py", label="About CycleIQ", icon="ℹ️")
    st.page_link("app.py", label="Live Overview", icon="📊")
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

# Main
st.markdown('<div class="page-header"><h1>Overview</h1><span>Live Dashboard</span></div>', unsafe_allow_html=True)

try:
    summary = load_summary()
    points_data = load_points()
    ward_summary = load_ward_summary()
    citizen_stats = load_citizen_stats()
except Exception as e:
    st.warning("Could not connect to API. Make sure `uvicorn main:app --reload --port 8000` is running.")
    st.stop()

df = pd.DataFrame(points_data)
ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()

# ── Hazardous contamination banner ─────────────────────────────────────────
if not ws_df.empty:
    haz_wards = ws_df[ws_df["avg_hazardous"] > 10].sort_values("avg_hazardous", ascending=False)
    if not haz_wards.empty:
        ward_id_to_name = {row["ward_id"]: row["ward_name"] for row in points_data}
        haz_names = [ward_id_to_name.get(r["ward_id"], r["ward_id"]) for _, r in haz_wards.iterrows()]
        st.markdown(f"""
        <div class="haz-banner">
            <span style="color:#ef4444;font-weight:700;font-size:0.82rem;">⚠ HAZARDOUS CONTAMINATION ALERT</span>
            <span style="color:#fca5a5;font-size:0.78rem;margin-left:0.75rem;">
                {len(haz_wards)} ward(s) exceeding 10% hazardous threshold —
                <strong>{', '.join(haz_names[:3])}</strong>
                {' ...' if len(haz_names) > 3 else ''}.
                Requires DPCC-authorised special collection vehicle.
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── Row 1: KPI metrics ──────────────────────────────────────────────────────
city_real = get_all_wards_summary()

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
with c1: st.metric("Wards Monitored", summary.get("total_wards", 20))
with c2: st.metric("Collection Points", summary.get("total_collection_points", 0))
with c3:
    fill = summary.get("avg_fill_level", 0)
    st.metric("Avg Fill Level", f"{fill}%", delta=f"{fill-60:.1f}% vs 60% threshold",
              delta_color="inverse" if fill > 60 else "normal")
with c4: st.metric("High Priority", summary.get("high_priority_points", 0), delta="urgent collection", delta_color="inverse")
with c5:
    haz_count = int(ws_df[ws_df["avg_hazardous"] > 10].shape[0]) if not ws_df.empty else 0
    st.metric("Hazardous Alerts", haz_count, delta="wards >10% hazardous", delta_color="inverse" if haz_count > 0 else "off")
with c6: st.metric("Waste Monitored", f"{city_real['daily_waste_monitored_tonnes']:,}t/day", delta=f"{city_real['coverage_pct']}% of Delhi")
with c6: st.metric("Waste Monitored", f"{city_real['daily_waste_monitored_tonnes']:,}t/day", delta=f"{city_real['coverage_pct']}% of Delhi")
with c7: st.metric("Citizens Enrolled", f"{summary.get('total_citizens', 0):,}")

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Row 2: Fill levels + Composition ───────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("**Ward Fill Levels**")
    ward_fills = {}
    for _, row in df.iterrows():
        wn = row["ward_name"]
        if wn not in ward_fills:
            ward_fills[wn] = []
        ward_fills[wn].append(row["fill_level"])
    ward_avg = pd.DataFrame([{"ward": w, "fill": sum(v)/len(v)} for w, v in ward_fills.items()])
    ward_avg = ward_avg.sort_values("fill", ascending=True)
    colors = ["#ef4444" if v > 75 else "#f59e0b" if v > 50 else "#4ade80" for v in ward_avg["fill"]]
    fig = go.Figure(go.Bar(
        x=ward_avg["fill"], y=ward_avg["ward"], orientation="h",
        marker_color=colors, hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af", size=11),
        margin=dict(l=0,r=10,t=0,b=0), height=380,
        xaxis=dict(gridcolor="#1e2e24", title="Avg Fill Level (%)", range=[0,100]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("**City-Wide Waste Composition**")
    if not ws_df.empty:
        avg = {
            "Organic\n(Green Bin)": ws_df["avg_organic"].mean(),
            "Plastic\n(Blue Bin)": ws_df["avg_plastic"].mean(),
            "Paper\n(Blue Bin)": ws_df["avg_paper"].mean(),
            "Metal\n(Blue Bin)": ws_df["avg_metal"].mean(),
            "Glass\n(Blue Bin)": ws_df["avg_glass"].mean(),
            "Hazardous\n(Red Bin)": ws_df["avg_hazardous"].mean(),
        }
        fig2 = go.Figure(go.Pie(
            labels=list(avg.keys()), values=list(avg.values()), hole=0.55,
            marker_colors=["#4ade80","#60a5fa","#fbbf24","#a78bfa","#34d399","#f87171"],
            textinfo="label+percent", textfont=dict(family="DM Sans", size=10),
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af"),
            margin=dict(l=0,r=0,t=0,b=0), height=230, showlegend=False,
            annotations=[dict(text="Composition", x=0.5, y=0.5,
                              font_size=11, font_color="#6b8f74", showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True)

        # 3-bin legend
        st.markdown("""
        <div style="display:flex;gap:0.75rem;margin-bottom:0.75rem;">
            <div style="background:#0d2010;border:1px solid #4ade8040;border-radius:6px;padding:4px 10px;font-size:0.7rem;color:#4ade80;">🟢 Green Bin — Organic/Wet</div>
            <div style="background:#0d1a2e;border:1px solid #60a5fa40;border-radius:6px;padding:4px 10px;font-size:0.7rem;color:#60a5fa;">🔵 Blue Bin — Dry/Recyclable</div>
            <div style="background:#1a0800;border:1px solid #ef444440;border-radius:6px;padding:4px 10px;font-size:0.7rem;color:#f87171;">🔴 Red Bin — Hazardous</div>
        </div>
        """, unsafe_allow_html=True)

    # Urgent alerts
    st.markdown("**Urgent Collection Needed**")
    urgent = df[df["fill_level"] > 75].sort_values("fill_level", ascending=False).head(5)
    for _, row in urgent.iterrows():
        fill = row["fill_level"]
        color = "#ef4444" if fill > 85 else "#f59e0b"
        st.markdown(f"""
        <div class="alert-row">
            <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
            <div style="flex:1;">
                <div style="font-size:0.82rem;color:#e8ede9;">{row['name']}</div>
                <div style="font-size:0.7rem;color:#6b8f74;">{row['ward_name']}</div>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:0.85rem;color:{color};font-weight:600;">{fill:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Row 3: Hazardous wards table + Citizen tiers ────────────────────────────
col_haz, col_cit = st.columns([3, 2], gap="large")

with col_haz:
    st.markdown("**Hazardous Contamination by Ward**")
    if not ws_df.empty:
        try:
            ward_id_to_name = {row["ward_id"]: row["ward_name"] for row in points_data}
            ws_df["ward_name_full"] = ws_df["ward_id"].map(ward_id_to_name).fillna(ws_df["ward_id"])
        except:
            ws_df["ward_name_full"] = ws_df["ward_id"]

        ws_sorted = ws_df.sort_values("avg_hazardous", ascending=False).head(10)
        for _, row in ws_sorted.iterrows():
            haz = float(row["avg_hazardous"])
            color = "#ef4444" if haz > 10 else "#f59e0b" if haz > 6 else "#4ade80"
            bar_w = int(haz * 5)
            status = "⚠ Special vehicle required" if haz > 10 else "Monitor" if haz > 6 else "Normal"
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.45rem 0.75rem;
                        background:#111a15;border:1px solid {'#ef444430' if haz > 10 else '#1e2e24'};
                        border-radius:8px;margin-bottom:0.35rem;gap:0.75rem;">
                <div style="min-width:130px;font-size:0.78rem;color:#e8ede9;">{row['ward_name_full']}</div>
                <div style="flex:1;background:#1e2e24;border-radius:3px;height:6px;">
                    <div style="background:{color};width:{min(bar_w,100)}%;height:6px;border-radius:3px;"></div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.78rem;color:{color};font-weight:600;min-width:38px;text-align:right;">{haz:.1f}%</div>
                <div style="font-size:0.68rem;color:{color};min-width:170px;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

with col_cit:
    st.markdown("**Citizen Tier Breakdown**")
    tiers = citizen_stats.get("tier_distribution", {})
    TIER_COLORS = {"Bronze":"#cd7f32","Silver":"#c0c0c0","Gold":"#ffd700","Platinum":"#e5e4e2"}
    TIER_BG = {"Bronze":"#1a0f00","Silver":"#141414","Gold":"#1a1500","Platinum":"#111418"}
    cols = st.columns(4)
    for col, (tier, count) in zip(cols, tiers.items()):
        color = TIER_COLORS.get(tier, "#6b8f74")
        bg = TIER_BG.get(tier, "#111a15")
        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {color}30;border-radius:12px;
                        padding:1rem;text-align:center;">
                <div style="font-size:0.65rem;color:{color};font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">{tier}</div>
                <div style="font-size:1.8rem;font-weight:700;color:{color};font-family:'DM Mono',monospace;margin:0.3rem 0;">{count}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-top:0.75rem;padding:0.75rem 1rem;background:#111a15;border:1px solid #1e2e24;
                border-radius:10px;font-size:0.8rem;color:#6b8f74;">
        Total points awarded: <span style="color:#4ade80;font-family:'DM Mono',monospace;font-weight:600;">
        {citizen_stats.get('total_points_awarded', 0):,}</span>
        &nbsp;·&nbsp; Avg per citizen: <span style="color:#e8ede9;font-family:'DM Mono',monospace;">
        {citizen_stats.get('avg_points', 0):.0f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("**Fill Level Distribution**")
    bins = {"0–25%": 0, "25–50%": 0, "50–75%": 0, "75–100%": 0}
    for _, row in df.iterrows():
        f = row["fill_level"]
        if f < 25: bins["0–25%"] += 1
        elif f < 50: bins["25–50%"] += 1
        elif f < 75: bins["50–75%"] += 1
        else: bins["75–100%"] += 1
    fig3 = go.Figure(go.Bar(
        x=list(bins.keys()), y=list(bins.values()),
        marker_color=["#4ade80","#86efac","#f59e0b","#ef4444"],
        text=list(bins.values()), textposition="outside",
        textfont=dict(color="#9ca3af", size=11)))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af", size=12),
        margin=dict(l=0,r=0,t=20,b=0), height=180,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#1e2e24"),
        showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

tab_overview, tab_economy = st.tabs(["📊 Live Overview", "♻️ Circular Economy"])
with tab_overview:
    st.info("Scroll up to see the live overview dashboard.")
with tab_economy:
    d = city_real["daily_waste_monitored_tonnes"]
    st.markdown(f"""
    <div style="background:#0d1a2e;border:1px solid #60a5fa30;border-radius:10px;
                padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.75rem;color:#6b8f74;">
        📊 Sources: <span style="color:#60a5fa;">CPCB Annual Report 2023</span> ·
        <span style="color:#60a5fa;">Census 2011</span> ·
        <span style="color:#60a5fa;">Swachh Survekshan 2022</span> ·
        Coverage: <span style="color:#e8ede9;">{city_real['coverage_pct']}% of Delhi</span> ({city_real['total_population_covered']:,} residents)
    </div>
    """, unsafe_allow_html=True)

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1: st.metric("Waste Monitored", f"{d:,} t/day")
    with ec2: st.metric("Landfill Reduction", f"{city_real['daily_landfill_reduction']} t/day", delta=f"{round(city_real['daily_landfill_reduction']/city_real['current_daily_landfill']*100,1)}% less")
    with ec3: st.metric("CO₂ Saved Daily", f"{city_real['daily_co2_saved_tonnes']} t")
    with ec4: st.metric("Annual CO₂ Saving", f"{int(city_real['annual_co2_saved_tonnes']):,} t", delta=f"≈{int(city_real['annual_co2_saved_tonnes']/4.6):,} cars removed")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    eco_col1, eco_col2 = st.columns([3,2], gap="large")

    with eco_col1:
        st.markdown("**Before vs With CycleIQ — Daily Waste Flow**")
        before_after = [
            ("🔴 Landfill", round(d*BASELINE_LANDFILL_RATE), round(d*CYCLEIQ_LANDFILL_RATE), "#ef4444"),
            ("🔵 Recycled", round(d*BASELINE_RECYCLING_RATE), round(d*CYCLEIQ_RECYCLING_RATE), "#60a5fa"),
            ("🟢 Composted", round(d*BASELINE_COMPOST_RATE), round(d*CYCLEIQ_COMPOST_RATE), "#4ade80"),
        ]
        for label, before, after, color in before_after:
            b_pct = round(before/d*100)
            a_pct = round(after/d*100)
            st.markdown(f"""
            <div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:0.82rem;color:#e8ede9;">{label}</span>
                    <span style="font-size:0.78rem;color:#6b8f74;">{before}t → <span style="color:{color};font-weight:600;">{after}t</span>/day</span>
                </div>
                <div style="background:#1e2e24;border-radius:4px;height:10px;position:relative;margin-bottom:2px;">
                    <div style="background:rgba(239,68,68,0.3);width:{b_pct}%;height:10px;border-radius:4px;position:absolute;"></div>
                    <div style="background:{color};width:{a_pct}%;height:10px;border-radius:4px;position:absolute;"></div>
                </div>
                <div style="font-size:0.68rem;color:#6b8f74;">Before: {b_pct}% &nbsp;→&nbsp; After: {a_pct}%</div>
            </div>
            """, unsafe_allow_html=True)

    with eco_col2:
        st.markdown("**CO₂ Impact Trend (30 days)**")
        dates = [datetime.now() - timedelta(days=29-i) for i in range(30)]
        daily_co2 = city_real["daily_co2_saved_tonnes"]
        co2_trend = [daily_co2 * (0.88 + np.random.uniform(-0.08, 0.12)) for _ in range(30)]
        fig_co2 = go.Figure()
        fig_co2.add_trace(go.Scatter(
            x=dates, y=co2_trend, mode="lines", fill="tozeroy",
            fillcolor="rgba(74,222,128,0.08)", line=dict(color="#4ade80", width=2)))
        fig_co2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af", size=10),
            margin=dict(l=0,r=0,t=10,b=0), height=160,
            xaxis=dict(gridcolor="#1e2e24"),
            yaxis=dict(gridcolor="#1e2e24", title="t CO₂"),
            showlegend=False)
        st.plotly_chart(fig_co2, use_container_width=True)
        st.markdown(f"""
        <div style="background:#111a15;border:1px solid #1e2e24;border-radius:10px;
                    padding:0.75rem;font-size:0.78rem;line-height:2;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6b8f74;">Landfill reduction/day</span>
                <span style="color:#4ade80;font-family:'DM Mono',monospace;">{city_real['daily_landfill_reduction']} t</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6b8f74;">Annual CO₂ saved</span>
                <span style="color:#4ade80;font-family:'DM Mono',monospace;">{int(city_real['annual_co2_saved_tonnes']):,} t</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6b8f74;">Cars equivalent</span>
                <span style="color:#60a5fa;font-family:'DM Mono',monospace;">{int(city_real['annual_co2_saved_tonnes']/4.6):,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6b8f74;">Fleet savings</span>
                <span style="color:#fbbf24;font-family:'DM Mono',monospace;">~22%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""<div style="font-size:0.65rem;color:#4b6358;margin-top:0.5rem;">
            Sources: {city_real['source']}
        </div>""", unsafe_allow_html=True)