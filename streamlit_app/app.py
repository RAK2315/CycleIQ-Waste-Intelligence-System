import streamlit as st

st.set_page_config(
    page_title="CycleIQ — Delhi Waste Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
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
.stat-card .label { font-size:0.7rem; color:#6b8f74; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.4rem; }
.stat-card .value { font-size:1.8rem; font-weight:700; font-family:'DM Mono',monospace; color:#e8ede9; }
.stat-card .sub { font-size:0.75rem; color:#4ade80; margin-top:0.2rem; }
.alert-row { display:flex; align-items:center; gap:0.75rem; padding:0.6rem 0; border-bottom:1px solid #1a2420; }
.alert-row:last-child { border-bottom:none; }
</style>
""", unsafe_allow_html=True)

import requests
import plotly.graph_objects as go
import pandas as pd

API = "http://localhost:8000/api"

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
    <div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #1e2e24;margin-bottom:0.5rem;">
        <div style="font-size:1.4rem;font-weight:700;color:#e8ede9;letter-spacing:-0.02em;">CycleIQ</div>
        <div style="font-size:0.72rem;color:#4ade80;font-family:'DM Mono',monospace;margin-top:2px;">Delhi Waste Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Navigation")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_waste_map.py", label="Waste Map", icon="🗺️")
    st.page_link("pages/2_forecasting.py", label="Forecasting", icon="📈")
    st.page_link("pages/3_routes.py", label="Route Optimizer", icon="🚛")
    st.page_link("pages/4_llm_chat.py", label="AI Assistant", icon="🤖")
    st.page_link("pages/5_citizens.py", label="Citizens", icon="👥")
    st.page_link("pages/6_cv_classify.py", label="Waste Classifier", icon="📷")
    st.page_link("pages/7_circular_economy.py", label="Circular Economy", icon="♻️")
    st.markdown("### System")
    st.markdown("""
    <div style="font-size:0.75rem;color:#6b8f74;line-height:2;">
        <div>● API &nbsp;<span style="color:#4ade80">Online</span></div>
        <div>● Database &nbsp;<span style="color:#4ade80">Neon PostgreSQL</span></div>
        <div>● LLM &nbsp;<span style="color:#4ade80">Groq / Llama 3.1</span></div>
        <div>● CV &nbsp;<span style="color:#fbbf24">YOLOv8n</span></div>
        <div>● Forecast &nbsp;<span style="color:#4ade80">Prophet</span></div>
        <div>● Routes &nbsp;<span style="color:#4ade80">OR-Tools</span></div>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<div class="page-header"><h1>Overview</h1><span>Live Dashboard</span></div>', unsafe_allow_html=True)

try:
    summary = load_summary()
    points_data = load_points()
    ward_summary = load_ward_summary()
    citizen_stats = load_citizen_stats()
except Exception as e:
    st.warning(f"Could not connect to API. Make sure `uvicorn main:app --reload --port 8000` is running.")
    st.stop()

df = pd.DataFrame(points_data)

# ── Row 1: KPI metrics ──────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: st.metric("Wards Monitored", summary.get("total_wards", 20))
with c2: st.metric("Collection Points", summary.get("total_collection_points", 0))
with c3:
    fill = summary.get("avg_fill_level", 0)
    st.metric("Avg Fill Level", f"{fill}%", delta=f"{fill-60:.1f}% vs 60% threshold",
              delta_color="inverse" if fill > 60 else "normal")
with c4: st.metric("High Priority", summary.get("high_priority_points", 0), delta="need urgent collection", delta_color="inverse")
with c5: st.metric("Citizens Enrolled", f"{summary.get('total_citizens', 0):,}")
with c6: st.metric("Classifications Done", f"{summary.get('total_classifications', 0):,}")

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
    ws_df = pd.DataFrame(ward_summary)
    if not ws_df.empty:
        avg = {
            "Organic": ws_df["avg_organic"].mean(),
            "Plastic": ws_df["avg_plastic"].mean(),
            "Paper": ws_df["avg_paper"].mean(),
            "Metal": ws_df["avg_metal"].mean(),
            "Glass": ws_df["avg_glass"].mean(),
            "Hazardous": ws_df["avg_hazardous"].mean(),
        }
        fig2 = go.Figure(go.Pie(
            labels=list(avg.keys()), values=list(avg.values()), hole=0.55,
            marker_colors=["#4ade80","#60a5fa","#fbbf24","#a78bfa","#34d399","#f87171"],
            textinfo="label+percent", textfont=dict(family="DM Sans", size=11),
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af"),
            margin=dict(l=0,r=0,t=0,b=0), height=220, showlegend=False,
            annotations=[dict(text="Composition", x=0.5, y=0.5,
                              font_size=12, font_color="#6b8f74", showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True)

    # Urgent alerts
    st.markdown("**Urgent Collection Needed**")
    urgent = df[df["fill_level"] > 75].sort_values("fill_level", ascending=False).head(6)
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

# ── Row 3: Citizen tiers + fill distribution ────────────────────────────────
col_a, col_b = st.columns([2, 3], gap="large")

with col_a:
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

with col_b:
    st.markdown("**Fill Level Distribution Across All Points**")
    bins = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0}
    for _, row in df.iterrows():
        f = row["fill_level"]
        if f < 25: bins["0-25%"] += 1
        elif f < 50: bins["25-50%"] += 1
        elif f < 75: bins["50-75%"] += 1
        else: bins["75-100%"] += 1
    fig3 = go.Figure(go.Bar(
        x=list(bins.keys()), y=list(bins.values()),
        marker_color=["#4ade80","#86efac","#f59e0b","#ef4444"],
        hovertemplate="%{x}: %{y} points<extra></extra>",
        text=list(bins.values()), textposition="outside",
        textfont=dict(color="#9ca3af", size=11)))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af", size=12),
        margin=dict(l=0,r=0,t=20,b=0), height=200,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#1e2e24", title="Number of Points"),
        showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)