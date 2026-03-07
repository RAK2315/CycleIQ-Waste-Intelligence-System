import streamlit as st
import requests
import pandas as pd
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
.stTextInput > div > div > input, .stSelectbox > div > div > div { background: #111a15 !important; border: 1px solid #1e2e24 !important; color: #e8ede9 !important; border-radius: 8px !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

@st.cache_data(ttl=30)
def load_stats():
    return requests.get(f"{API}/citizens/stats", timeout=5).json()

@st.cache_data(ttl=30)
def load_leaderboard(ward_id=None):
    url = f"{API}/citizens/leaderboard?limit=20"
    if ward_id:
        url += f"&ward_id={ward_id}"
    return requests.get(url, timeout=5).json()

@st.cache_data(ttl=300)
def load_wards():
    return requests.get(f"{API}/forecast/wards", timeout=5).json()

st.markdown('<div class="page-header"><h1>Citizens</h1><span>Incentive Tracker</span></div>', unsafe_allow_html=True)

try:
    stats = load_stats()
    leaderboard = load_leaderboard()
    wards = load_wards()
except:
    st.error("API not reachable.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Citizens", f"{stats.get('total_citizens', 0):,}")
with c2: st.metric("Points Awarded", f"{stats.get('total_points_awarded', 0):,}")
with c3: st.metric("Avg Points", f"{stats.get('avg_points', 0):.0f}")
with c4: st.metric("Top Citizen", stats.get("top_citizen", "—"))

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
col_lb, col_right = st.columns([3, 2], gap="large")

with col_lb:
    st.markdown("**Leaderboard**")
    if leaderboard:
        TIER_COLORS = {"Platinum":"#e5e4e2","Gold":"#ffd700","Silver":"#c0c0c0","Bronze":"#cd7f32"}
        for row in leaderboard:
            rank = row["rank"]
            tier_color = TIER_COLORS.get(row["tier"], "#6b8f74")
            rank_display = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"
            rank_style = "color:#ffd700;font-weight:700;" if rank==1 else "color:#c0c0c0;font-weight:700;" if rank==2 else "color:#cd7f32;font-weight:700;" if rank==3 else "color:#6b8f74;"
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.5rem 0.75rem;border-bottom:1px solid #1a2420;gap:1rem;">
                <div style="width:28px;font-family:'DM Mono',monospace;font-size:0.85rem;{rank_style}">{rank_display}</div>
                <div style="flex:1;">
                    <div style="font-size:0.88rem;font-weight:500;color:#e8ede9;">{row['name']}</div>
                    <div style="font-size:0.72rem;color:#6b8f74;">{row['ward']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'DM Mono',monospace;font-size:0.9rem;color:#4ade80;font-weight:600;">{row['points']:,}</div>
                    <div style="font-size:0.7rem;font-weight:600;color:{tier_color};">{row['tier']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    tiers = stats.get("tier_distribution", {})
    if tiers:
        st.markdown("**Tier Distribution**")
        fig = go.Figure(go.Bar(
            x=list(tiers.keys()), y=list(tiers.values()),
            marker_color=["#cd7f32","#c0c0c0","#ffd700","#e5e4e2"],
            hovertemplate="%{x}: %{y} citizens<extra></extra>"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af", size=11),
            margin=dict(l=0,r=0,t=10,b=0), height=200,
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="#1e2e24"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Register New Citizen**")
    with st.form("register_form"):
        name = st.text_input("Full Name")
        ward_names = [w["name"] for w in wards]
        ward_sel = st.selectbox("Ward", ward_names)
        submitted = st.form_submit_button("Register")
        if submitted and name:
            ward_obj = next(w for w in wards if w["name"] == ward_sel)
            r = requests.post(f"{API}/citizens/register",
                json={"name": name, "ward_id": ward_obj["id"], "ward_name": ward_obj["name"]})
            if r.status_code == 200:
                st.success(r.json().get("message", "Registered!"))
                st.cache_data.clear()