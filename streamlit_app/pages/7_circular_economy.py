import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

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
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ede9 !important; font-size: 1.8rem !important; font-weight: 600 !important; font-family: 'DM Mono', monospace !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.flow-card { background:#111a15; border:1px solid #1e2e24; border-radius:14px; padding:1.2rem 1.5rem; text-align:center; }
.flow-card .flow-icon { font-size:1.8rem; margin-bottom:0.5rem; }
.flow-card .flow-label { font-size:0.7rem; color:#6b8f74; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; }
.flow-card .flow-value { font-size:1.4rem; font-weight:700; font-family:'DM Mono',monospace; color:#4ade80; margin:0.2rem 0; }
.flow-card .flow-sub { font-size:0.75rem; color:#6b8f74; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

@st.cache_data(ttl=60)
def load_ward_summary():
    return requests.get(f"{API}/waste/ward-summary", timeout=5).json()

@st.cache_data(ttl=30)
def load_citizen_stats():
    return requests.get(f"{API}/citizens/stats", timeout=5).json()

@st.cache_data(ttl=60)
def load_route_stats():
    return requests.get(f"{API}/routes/stats", timeout=5).json()

st.markdown('<div class="page-header"><h1>Circular Economy</h1><span>Material Flow Tracker</span></div>', unsafe_allow_html=True)

try:
    ward_summary = load_ward_summary()
    citizen_stats = load_citizen_stats()
    route_stats = load_route_stats()
except:
    st.error("API not reachable.")
    st.stop()

ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()

# Calculate city-level material flow metrics
if not ws_df.empty:
    avg_organic = ws_df["avg_organic"].mean()
    avg_plastic = ws_df["avg_plastic"].mean()
    avg_paper = ws_df["avg_paper"].mean()
    avg_metal = ws_df["avg_metal"].mean()
    avg_glass = ws_df["avg_glass"].mean()
    avg_hazardous = ws_df["avg_hazardous"].mean()
else:
    avg_organic, avg_plastic, avg_paper = 42.0, 28.0, 14.0
    avg_metal, avg_glass, avg_hazardous = 7.0, 5.0, 4.0

total_daily_waste_tonnes = 11000  # Delhi baseline
recyclable_pct = avg_plastic + avg_paper + avg_metal + avg_glass
compostable_pct = avg_organic
hazardous_pct = avg_hazardous
landfill_pct = 100 - recyclable_pct - compostable_pct

recyclable_tonnes = total_daily_waste_tonnes * recyclable_pct / 100
compostable_tonnes = total_daily_waste_tonnes * compostable_pct / 100
hazardous_tonnes = total_daily_waste_tonnes * hazardous_pct / 100
landfill_tonnes = max(0, total_daily_waste_tonnes * landfill_pct / 100)

# CO2 savings: recycling saves ~1.5 tonne CO2 per tonne waste vs landfill
co2_saved_daily = recyclable_tonnes * 1.5 + compostable_tonnes * 0.3
route_emissions_saved = route_stats.get("estimated_savings_pct", 22) / 100 * 500  # baseline 500kg/day fleet

# ── KPIs ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Daily Waste Processed", f"{total_daily_waste_tonnes:,} t")
with c2: st.metric("Recyclable Diverted", f"{recyclable_pct:.1f}%", delta=f"{recyclable_tonnes:.0f} tonnes/day")
with c3: st.metric("Compostable Diverted", f"{compostable_pct:.1f}%", delta=f"{compostable_tonnes:.0f} tonnes/day")
with c4: st.metric("CO₂ Saved (Daily)", f"{co2_saved_daily:.0f} t", delta="vs full landfill baseline")
with c5:
    landfill_div = 100 - landfill_pct
    st.metric("Landfill Diversion", f"{max(0,landfill_div):.1f}%", delta="from baseline 100%")

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Material Flow Sankey ─────────────────────────────────────────────────
st.markdown("**Material Flow — Delhi Daily Waste (Sankey)**")
fig_sankey = go.Figure(go.Sankey(
    node=dict(
        pad=15, thickness=20,
        line=dict(color="#1e2e24", width=0.5),
        label=["Total Waste", "Biodegradable", "Recyclables", "Hazardous",
               "Composting", "Landfill (Organic)", "Plastic Recycling",
               "Paper Recycling", "Metal Recycling", "Glass Recycling",
               "Hazardous Treatment"],
        color=["#2d4a36","#4ade80","#60a5fa","#f87171",
               "#22c55e","#6b8f74","#3b82f6",
               "#fbbf24","#a78bfa","#34d399","#ef4444"],
        x=[0.0, 0.3, 0.3, 0.3, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65],
        y=[0.5, 0.2, 0.5, 0.85, 0.1, 0.25, 0.42, 0.55, 0.67, 0.78, 0.9],
    ),
    link=dict(
        source=[0, 0, 0, 1, 1, 2, 2, 2, 2, 3],
        target=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        value=[
            compostable_tonnes, recyclable_tonnes, hazardous_tonnes,
            compostable_tonnes * 0.7, compostable_tonnes * 0.3,
            recyclable_tonnes * avg_plastic/recyclable_pct if recyclable_pct else 0,
            recyclable_tonnes * avg_paper/recyclable_pct if recyclable_pct else 0,
            recyclable_tonnes * avg_metal/recyclable_pct if recyclable_pct else 0,
            recyclable_tonnes * avg_glass/recyclable_pct if recyclable_pct else 0,
            hazardous_tonnes,
        ],
        color=["rgba(74,222,128,0.3)","rgba(96,165,250,0.3)","rgba(248,113,113,0.3)",
               "rgba(34,197,94,0.3)","rgba(107,143,116,0.3)","rgba(59,130,246,0.3)",
               "rgba(251,191,36,0.3)","rgba(167,139,250,0.3)","rgba(52,211,153,0.3)",
               "rgba(239,68,68,0.3)"],
    )
))
fig_sankey.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9ca3af", size=11),
    margin=dict(l=0,r=0,t=10,b=0), height=380)
st.plotly_chart(fig_sankey, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Bottom row ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("**Ward-Level Segregation Efficiency**")
    if not ws_df.empty:
        # Segregation score = recyclable % + compostable % (higher = better separation)
        ws_df["seg_score"] = ws_df["avg_organic"] + ws_df["avg_plastic"] + ws_df["avg_paper"] + ws_df["avg_metal"] + ws_df["avg_glass"]
        # Need ward names — merge with wards
        import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..")); from data.synthetic_data import DELHI_WARDS
        ward_id_to_name = {w["id"]: w["name"] for w in DELHI_WARDS}
        ws_df["ward_name"] = ws_df["ward_id"].map(ward_id_to_name).fillna(ws_df["ward_id"])
        ws_sorted = ws_df.sort_values("seg_score", ascending=True)

        colors = ["#ef4444" if v < 70 else "#fbbf24" if v < 85 else "#4ade80" for v in ws_sorted["seg_score"]]
        fig2 = go.Figure(go.Bar(
            x=ws_sorted["seg_score"], y=ws_sorted["ward_name"],
            orientation="h", marker_color=colors,
            hovertemplate="%{y}: %{x:.1f}% non-landfill<extra></extra>"
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af", size=11),
            margin=dict(l=0,r=10,t=0,b=0), height=380,
            xaxis=dict(gridcolor="#1e2e24", title="Diversion Rate (%)", range=[0,100]),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.markdown("**CO₂ Impact Summary**")
    # 30-day trend (simulated based on real data)
    import numpy as np
    dates = [datetime.now() - timedelta(days=29-i) for i in range(30)]
    co2_trend = [co2_saved_daily * (0.85 + np.random.uniform(-0.1, 0.15)) for _ in range(30)]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=dates, y=co2_trend, mode="lines", fill="tozeroy",
        fillcolor="rgba(74,222,128,0.08)", line=dict(color="#4ade80", width=2),
        hovertemplate="%{x|%b %d}: %{y:.0f}t CO₂ saved<extra></extra>"
    ))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af", size=11),
        margin=dict(l=0,r=0,t=10,b=0), height=180,
        xaxis=dict(gridcolor="#1e2e24"),
        yaxis=dict(gridcolor="#1e2e24", title="Tonnes CO₂"),
        showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Quick stats
    st.markdown(f"""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1rem 1.2rem;font-size:0.82rem;line-height:2.2;">
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#6b8f74;">30-day CO₂ saved</span>
            <span style="color:#4ade80;font-family:'DM Mono',monospace;font-weight:600;">{sum(co2_trend):.0f} tonnes</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#6b8f74;">Fleet emission reduction</span>
            <span style="color:#4ade80;font-family:'DM Mono',monospace;font-weight:600;">~22%</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#6b8f74;">Recyclable recovery rate</span>
            <span style="color:#60a5fa;font-family:'DM Mono',monospace;font-weight:600;">{recyclable_pct:.1f}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#6b8f74;">Composting potential</span>
            <span style="color:#4ade80;font-family:'DM Mono',monospace;font-weight:600;">{compostable_pct:.1f}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#6b8f74;">Hazardous safe disposal</span>
            <span style="color:#f87171;font-family:'DM Mono',monospace;font-weight:600;">{hazardous_pct:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)