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
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:0.25rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

@st.cache_data(ttl=30)
def load_stats():
    return requests.get(f"{API}/citizens/stats", timeout=5).json()

@st.cache_data(ttl=30)
def load_leaderboard():
    return requests.get(f"{API}/citizens/leaderboard?limit=20", timeout=5).json()

@st.cache_data(ttl=300)
def load_wards():
    return requests.get(f"{API}/forecast/wards", timeout=5).json()

@st.cache_data(ttl=60)
def load_ward_summary():
    return requests.get(f"{API}/waste/ward-summary", timeout=5).json()

@st.cache_data(ttl=30)
def load_points():
    return requests.get(f"{API}/waste/collection-points", timeout=5).json()

st.markdown("""
<div class="page-header">
    <div>
        <h1 style="margin:0;">Citizens &amp; Rewards</h1>
        <div style="font-size:0.82rem;color:#6b8f74;margin-top:0.2rem;">Gamified citizen engagement for better waste segregation</div>
    </div>
</div>
""", unsafe_allow_html=True)

try:
    stats = load_stats()
    leaderboard = load_leaderboard()
    wards = load_wards()
    ward_summary = load_ward_summary()
    points_data = load_points()
except:
    st.error("API not reachable.")
    st.stop()

ward_id_to_name = {row["ward_id"]: row["ward_name"] for row in points_data}

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Citizens", f"{stats.get('total_citizens', 0):,}")
with c2: st.metric("Points Awarded", f"{stats.get('total_points_awarded', 0):,}")
with c3: st.metric("Avg Points", f"{stats.get('avg_points', 0):.0f}")
with c4: st.metric("Top Citizen", stats.get("top_citizen", "—"))

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Pill-style tab selector ──────────────────────────────────────────────────
if "citizen_tab" not in st.session_state:
    st.session_state.citizen_tab = "Leaderboard"

tabs_def = ["🏆 Leaderboard", "🎁 Rewards", "📋 Ward Report Card", "🔔 Community Nudges"]
tab_keys = ["Leaderboard", "Rewards", "Ward Report Card", "Community Nudges"]

cols = st.columns(len(tabs_def))
for i, (col, label, key) in enumerate(zip(cols, tabs_def, tab_keys)):
    with col:
        active = st.session_state.citizen_tab == key
        if st.button(label, key=f"tab_{key}",
                     help=None,
                     use_container_width=True):
            st.session_state.citizen_tab = key
            st.rerun()

active_tab = st.session_state.citizen_tab
st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

# ── LEADERBOARD ──────────────────────────────────────────────────────────────
if active_tab == "Leaderboard":
    col_lb, col_right = st.columns([3, 2], gap="large")
    with col_lb:
        st.markdown("**Top Citizens**")
        TIER_COLORS = {"Platinum":"#e5e4e2","Gold":"#ffd700","Silver":"#c0c0c0","Bronze":"#cd7f32"}
        for row in leaderboard:
            rank = row["rank"]
            tc = TIER_COLORS.get(row["tier"], "#6b8f74")
            medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"
            rank_color = "color:#ffd700;" if rank==1 else "color:#c0c0c0;" if rank==2 else "color:#cd7f32;" if rank==3 else "color:#6b8f74;"
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.6rem 0.75rem;
                        background:#111a15;border:1px solid #1e2e24;border-radius:10px;
                        margin-bottom:0.4rem;gap:1rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.9rem;font-weight:700;
                            {rank_color}min-width:28px;">{medal}</div>
                <div style="flex:1;">
                    <div style="font-size:0.88rem;font-weight:600;color:#e8ede9;">{row['name']}</div>
                    <div style="font-size:0.72rem;color:#6b8f74;">{row['ward']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'DM Mono',monospace;font-size:0.9rem;color:#4ade80;font-weight:600;">{row['points']:,}</div>
                    <div style="font-size:0.7rem;font-weight:700;color:{tc};">{row['tier']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        tiers = stats.get("tier_distribution", {})
        if tiers:
            st.markdown("**Tier Distribution**")
            fig = go.Figure(go.Bar(
                x=list(tiers.keys()), y=list(tiers.values()),
                marker_color=["#cd7f32","#c0c0c0","#ffd700","#e5e4e2"]))
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
            if st.form_submit_button("Register"):
                if name:
                    ward_obj = next(w for w in wards if w["name"] == ward_sel)
                    r = requests.post(f"{API}/citizens/register",
                        json={"name": name, "ward_id": ward_obj["id"], "ward_name": ward_obj["name"]})
                    if r.status_code == 200:
                        st.success(r.json().get("message", "Registered!"))
                        st.cache_data.clear()

# ── REWARDS ──────────────────────────────────────────────────────────────────
elif active_tab == "Rewards":
    st.markdown("""
    <div style="background:#0d2010;border:1px solid #4ade8030;border-radius:10px;
                padding:0.75rem 1rem;margin-bottom:1.25rem;font-size:0.8rem;color:#86efac;">
        Points are earned by your ward collectively when segregation scores are high.
        Redeem individually at any MCD office or via the Delhi One portal.
    </div>
    """, unsafe_allow_html=True)

    REWARDS = [
        {"title": "DMRC Metro Credits",        "sub": "₹50 metro card top-up",           "pts": 500,  "icon": "🚇"},
        {"title": "Electricity Bill Discount",  "sub": "5% discount on next bill",        "pts": 1000, "icon": "⚡"},
        {"title": "DDA Tree Plantation",        "sub": "Plant a tree in your name",       "pts": 750,  "icon": "🌳"},
        {"title": "MCD Complaint Priority",     "sub": "Priority queue for 30 days",      "pts": 300,  "icon": "🔧"},
        {"title": "Water Bill Discount",        "sub": "₹80 off Delhi Jal Board bill",    "pts": 800,  "icon": "💧"},
        {"title": "Green Citizen Certificate",  "sub": "Digital certificate from MCD",    "pts": 200,  "icon": "🏅"},
    ]

    col_a, col_b = st.columns(2, gap="medium")
    for i, r in enumerate(REWARDS):
        col = col_a if i % 2 == 0 else col_b
        with col:
            st.markdown(f"""
            <div style="background:#111a15;border:1px solid #1e2e24;border-radius:14px;
                        padding:1.1rem 1.3rem;margin-bottom:0.75rem;
                        display:flex;align-items:center;gap:1rem;">
                <div style="font-size:1.8rem;flex-shrink:0;">{r['icon']}</div>
                <div style="flex:1;">
                    <div style="font-size:0.9rem;font-weight:600;color:#e8ede9;">{r['title']}</div>
                    <div style="font-size:0.75rem;color:#6b8f74;margin-top:1px;">{r['sub']}</div>
                    <div style="font-size:0.9rem;font-weight:700;color:#4ade80;margin-top:0.4rem;">{r['pts']} points</div>
                </div>
                <div style="background:transparent;border:1.5px solid #4ade80;color:#4ade80;
                            font-size:0.8rem;font-weight:600;padding:6px 18px;border-radius:8px;
                            cursor:pointer;flex-shrink:0;">Redeem</div>
            </div>
            """, unsafe_allow_html=True)

# ── WARD REPORT CARD ─────────────────────────────────────────────────────────
elif active_tab == "Ward Report Card":
    st.markdown("""
    <div style="font-size:0.82rem;color:#6b8f74;margin-bottom:1rem;">
        Any resident can check their ward's performance — no login required.
    </div>
    """, unsafe_allow_html=True)

    ward_names_list = [w["name"] for w in wards]
    selected_ward = st.selectbox("Search your ward", ward_names_list)
    selected_ward_obj = next((w for w in wards if w["name"] == selected_ward), None)
    ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()

    if selected_ward_obj and not ws_df.empty:
        ward_id = selected_ward_obj["id"]
        row = ws_df[ws_df["ward_id"] == ward_id]
        if not row.empty:
            r = row.iloc[0]
            organic = float(r["avg_organic"])
            recyclable = float(r["avg_plastic"]) + float(r["avg_paper"]) + float(r["avg_metal"]) + float(r["avg_glass"])
            hazardous = float(r["avg_hazardous"])
            total_cls = int(r["total_classifications"])

            dominant = max(organic, recyclable, hazardous)
            score = round((dominant/100)*80 + (1 - hazardous/100)*20, 1)
            label = "Excellent" if score >= 80 else "Good" if score >= 65 else "Fair" if score >= 50 else "Poor"
            label_icon = "🌟" if score >= 80 else "✅" if score >= 65 else "⚠️" if score >= 50 else "❌"
            score_color = "#4ade80" if score >= 65 else "#f59e0b" if score >= 50 else "#ef4444"

            st.markdown(f"""
            <div style="background:#111a15;border:1px solid #1e2e24;border-radius:14px;padding:1.5rem;margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.25rem;">
                    <div>
                        <div style="font-size:1.2rem;font-weight:700;color:#e8ede9;">{selected_ward}</div>
                        <div style="font-size:0.75rem;color:#6b8f74;margin-top:2px;">{total_cls} classifications recorded · Ward ID: {ward_id}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:2.2rem;font-weight:700;color:{score_color};font-family:'DM Mono',monospace;line-height:1;">{score}</div>
                        <div style="font-size:0.82rem;color:{score_color};margin-top:2px;">{label_icon} {label}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;">
                    <div style="background:#0d2010;border:1px solid #4ade8030;border-radius:10px;padding:0.9rem;text-align:center;">
                        <div style="font-size:0.65rem;color:#4ade80;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">🟢 Green Bin</div>
                        <div style="font-size:1.5rem;font-weight:700;color:#4ade80;font-family:'DM Mono',monospace;margin:0.3rem 0;">{organic:.0f}%</div>
                        <div style="font-size:0.68rem;color:#6b8f74;">Organic / Wet</div>
                    </div>
                    <div style="background:#0d1a2e;border:1px solid #60a5fa30;border-radius:10px;padding:0.9rem;text-align:center;">
                        <div style="font-size:0.65rem;color:#60a5fa;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">🔵 Blue Bin</div>
                        <div style="font-size:1.5rem;font-weight:700;color:#60a5fa;font-family:'DM Mono',monospace;margin:0.3rem 0;">{recyclable:.0f}%</div>
                        <div style="font-size:0.68rem;color:#6b8f74;">Dry / Recyclable</div>
                    </div>
                    <div style="background:{'#1a0800' if hazardous > 10 else '#111a15'};border:1px solid {'#ef444440' if hazardous > 10 else '#f8717130'};border-radius:10px;padding:0.9rem;text-align:center;">
                        <div style="font-size:0.65rem;color:{'#ef4444' if hazardous > 10 else '#f87171'};font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">🔴 Red Bin</div>
                        <div style="font-size:1.5rem;font-weight:700;color:{'#ef4444' if hazardous > 10 else '#f87171'};font-family:'DM Mono',monospace;margin:0.3rem 0;">{hazardous:.0f}%</div>
                        <div style="font-size:0.68rem;color:#6b8f74;">Hazardous</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if hazardous > 10:
                st.markdown(f"""
                <div style="background:#1a0800;border:1px solid #ef444440;border-radius:10px;
                            padding:0.75rem 1rem;font-size:0.8rem;color:#fca5a5;margin-bottom:0.75rem;">
                    ⚠ <b>{selected_ward}</b> has high hazardous waste ({hazardous:.1f}%).
                    Please use the <b>red bin</b> for medicines, diapers, cleaning agents and sanitary waste.
                </div>
                """, unsafe_allow_html=True)

            pts_this_week = int(score * 12) if score >= 50 else 0
            st.markdown(f"""
            <div style="background:#0d2010;border:1px solid #4ade8030;border-radius:10px;
                        padding:0.75rem 1rem;font-size:0.82rem;color:#86efac;">
                🎯 Citizens in <b>{selected_ward}</b> earned approximately
                <span style="color:#4ade80;font-family:'DM Mono',monospace;font-weight:700;">{pts_this_week} points</span>
                this week based on current segregation performance.
            </div>
            """, unsafe_allow_html=True)

# ── COMMUNITY NUDGES ─────────────────────────────────────────────────────────
elif active_tab == "Community Nudges":
    st.markdown("""
    <div style="font-size:0.8rem;color:#6b8f74;margin-bottom:1.25rem;">
        When ward data crosses thresholds, CycleIQ auto-triggers alerts to RWA group admins via WhatsApp or SMS.
    </div>
    """, unsafe_allow_html=True)

    ws_df = pd.DataFrame(ward_summary) if ward_summary else pd.DataFrame()
    nudges = []

    if not ws_df.empty:
        for _, row in ws_df.iterrows():
            wname = ward_id_to_name.get(row["ward_id"], row["ward_id"])
            haz = float(row["avg_hazardous"])
            org = float(row["avg_organic"])

            if haz > 10:
                nudges.append({
                    "ward": wname,
                    "trigger": "Hazardous >10%",
                    "channel": "WhatsApp",
                    "channel_color": "#25d366",
                    "icon": "⚠️",
                    "border": "#f59e0b",
                    "msg": f"Alert: Hazardous waste at {haz:.0f}% in your ward. Please separate medicines, batteries & cleaning agents into RED bins."
                })
            if org < 25:
                nudges.append({
                    "ward": wname,
                    "trigger": "Low organic separation",
                    "channel": "SMS",
                    "channel_color": "#60a5fa",
                    "icon": "⚠️",
                    "border": "#f59e0b",
                    "msg": f"Dear resident, organic waste separation in your ward dropped to {org:.0f}%. Please use GREEN bins for food/vegetable waste."
                })

    nudges.append({
        "ward": "All Wards",
        "trigger": "Weekly Update",
        "channel": "SMS",
        "channel_color": "#60a5fa",
        "icon": "📢",
        "border": "#4ade80",
        "msg": "CycleIQ Weekly: Delhi recycled 847 tonnes this week. Top ward: Dwarka. Keep segregating — every bin counts!"
    })

    for n in nudges[:8]:
        channel_bg = "#0d2a15" if n["channel"] == "WhatsApp" else "#0d1a2e"
        st.markdown(f"""
        <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;
                    padding:1rem 1.1rem;margin-bottom:0.6rem;">
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
                <span style="font-size:1rem;">{n['icon']}</span>
                <span style="font-size:0.9rem;font-weight:700;color:#e8ede9;">{n['ward']}</span>
                <span style="background:{channel_bg};color:{n['channel_color']};font-size:0.7rem;
                             font-weight:600;padding:2px 10px;border-radius:20px;border:1px solid {n['channel_color']}40;">
                    {n['channel']}
                </span>
                <span style="font-size:0.72rem;color:#6b8f74;">· {n['trigger']}</span>
            </div>
            <div style="font-size:0.8rem;color:#9ca3af;padding-left:1.6rem;line-height:1.5;">
                {n['icon']} {n['msg']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:10px;
                padding:0.75rem 1rem;font-size:0.75rem;color:#6b8f74;margin-top:0.5rem;">
        <b style="color:#e8ede9;">Nudge thresholds:</b>
        Hazardous &gt;10% → WhatsApp + SMS to RWA admin ·
        Organic &lt;25% → weekly SMS reminder ·
        Fill &gt;85% for 2hrs → driver dispatch alert
    </div>
    """, unsafe_allow_html=True)