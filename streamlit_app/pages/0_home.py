import streamlit as st
import sys, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)
from data.real_data import get_all_wards_summary, DELHI_TOTAL_WASTE_TPD

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header { visibility: visible; }
.stApp { background: #0a0f0d; color: #e8ede9; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.6rem 1.5rem !important; font-size: 0.9rem !important; }
</style>
""", unsafe_allow_html=True)

city = get_all_wards_summary()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding:3rem 0 2rem 0;border-bottom:1px solid #1e2e24;margin-bottom:2rem;">
    <div style="font-size:0.8rem;color:#4ade80;font-family:'DM Mono',monospace;
                letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.75rem;">
        India Innovates 2026 · Urban Solutions Track
    </div>
    <div style="font-size:3rem;font-weight:700;color:#e8ede9;line-height:1.1;margin-bottom:1rem;">
        CycleIQ
    </div>
    <div style="font-size:1.2rem;color:#6b8f74;max-width:600px;line-height:1.6;margin-bottom:1.5rem;">
        AI-powered circular waste intelligence for Delhi.
        Turning 10,500 tonnes of daily waste from a problem into a resource.
    </div>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
        <div style="background:#0d2010;border:1px solid #4ade8040;border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#4ade80;">
            🟢 {city['daily_waste_monitored_tonnes']:,} tonnes/day monitored
        </div>
        <div style="background:#0d1a2e;border:1px solid #60a5fa40;border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#60a5fa;">
            🔵 20 Delhi wards · {city['total_population_covered']:,} residents
        </div>
        <div style="background:#1a0800;border:1px solid #f8717140;border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#f87171;">
            🔴 {city['daily_landfill_reduction']} t/day diverted from landfill
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Problem ───────────────────────────────────────────────────────────────────
st.markdown("### The Problem")
col1, col2, col3 = st.columns(3)
problems = [
    ("10,500 t/day", "Delhi's daily waste", "Only 23% currently segregated at source", "#ef4444"),
    ("3 overflowing landfills", "Ghazipur · Bhalswa · Okhla", "All exceeding capacity, creating health crises", "#f59e0b"),
    ("₹1,800 Cr/year", "MCD waste management spend", "Trucks run fixed schedules regardless of bin levels", "#60a5fa"),
]
for col, (stat, label, desc, color) in zip([col1, col2, col3], problems):
    with col:
        st.markdown(f"""
        <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1.25rem;height:140px;">
            <div style="font-size:1.4rem;font-weight:700;color:{color};font-family:'DM Mono',monospace;">{stat}</div>
            <div style="font-size:0.82rem;font-weight:600;color:#e8ede9;margin:0.3rem 0;">{label}</div>
            <div style="font-size:0.75rem;color:#6b8f74;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Solution ──────────────────────────────────────────────────────────────────
st.markdown("### How CycleIQ Works")
steps = [
    ("📡", "IoT Sensors", "Ultrasonic sensors on bins report fill levels every 30 seconds. No manual inspection needed."),
    ("🤖", "AI Classification", "YOLOv8 camera at collection points identifies waste type. 3-bin system: Green · Blue · Red."),
    ("📈", "Smart Forecasting", "Prophet ML predicts overflow 48hrs before it happens — before festivals, weekends."),
    ("🚛", "Route Optimisation", "OR-Tools sends trucks only where needed. 22% fewer km driven. Real CO₂ reduction."),
    ("🏆", "Citizen Incentives", "Wards that segregate well earn points. Citizens redeem for DMRC credits, bill discounts."),
    ("♻️", "Circular Economy", "Every classification feeds a live material flow tracker showing real diverted tonnage."),
]
col_a, col_b, col_c = st.columns(3)
for i, (icon, title, desc) in enumerate(steps):
    col = [col_a, col_b, col_c][i % 3]
    with col:
        st.markdown(f"""
        <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;
                    padding:1.1rem;margin-bottom:0.75rem;">
            <div style="font-size:1.4rem;margin-bottom:0.4rem;">{icon}</div>
            <div style="font-size:0.88rem;font-weight:600;color:#e8ede9;margin-bottom:0.3rem;">{title}</div>
            <div style="font-size:0.75rem;color:#6b8f74;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Navigation guide ──────────────────────────────────────────────────────────
st.markdown("### Explore the Dashboard")
nav_items = [
    ("🏠", "Overview", "Live KPIs, fill levels, hazardous alerts across all 20 wards"),
    ("🗺️", "Waste Map", "Real-time Folium map — toggle Fill / Hazardous / Both layers"),
    ("📈", "Forecasting", "7-day Prophet forecast per ward — see which wards will overflow"),
    ("🚛", "Route Optimizer", "OR-Tools optimised truck routes — live fill data, CO₂ calculated"),
    ("🤖", "AI Assistant", "Ask anything about Delhi waste — backed by real ward data via Groq/Llama 3.1"),
    ("👥", "Citizens & Rewards", "Leaderboard, rewards redemption, ward report card, community nudges"),
    ("📷", "Waste Classifier", "Upload image or use live camera — YOLOv8 identifies waste type + correct bin"),
    ("♻️", "Circular Economy", "Real CPCB data — before vs after, per-ward landfill reduction, CO₂ impact"),
    ("🚛", "Driver View", "Simplified route card for truck drivers — same routes as optimizer"),
    ("🎥", "Bin Monitor", "Upload sorting video — zone-based detection, correct/wrong bin, fill estimation"),
]
col1, col2 = st.columns(2)
for i, (icon, title, desc) in enumerate(nav_items):
    col = col1 if i % 2 == 0 else col2
    with col:
        st.markdown(f"""
        <div style="display:flex;gap:0.75rem;padding:0.6rem 0.75rem;background:#111a15;
                    border:1px solid #1e2e24;border-radius:8px;margin-bottom:0.4rem;">
            <div style="font-size:1.1rem;flex-shrink:0;">{icon}</div>
            <div>
                <div style="font-size:0.82rem;font-weight:600;color:#e8ede9;">{title}</div>
                <div style="font-size:0.72rem;color:#6b8f74;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Deployment model ──────────────────────────────────────────────────────────
st.markdown("### Deployment & Business Model")
col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    st.markdown("""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1.25rem;">
        <div style="font-size:0.75rem;color:#4ade80;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.75rem;">💰 Funding</div>
        <div style="font-size:0.8rem;color:#6b8f74;line-height:1.8;">
            <div>• Smart Cities Mission (MoHUA)</div>
            <div>• AMRUT 2.0 municipal grants</div>
            <div>• MCD annual sanitation budget</div>
            <div style="margin-top:0.5rem;color:#e8ede9;font-weight:600;">Pilot cost: ~₹45L for 1 ward</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_d2:
    st.markdown("""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1.25rem;">
        <div style="font-size:0.75rem;color:#60a5fa;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.75rem;">🔧 Hardware</div>
        <div style="font-size:0.8rem;color:#6b8f74;line-height:1.8;">
            <div>• IoT fill sensor: ₹8,000/point</div>
            <div>• CV camera unit: ₹12,000/point</div>
            <div>• 3 collection points/ward avg</div>
            <div>• Installation + connectivity: ₹5,000</div>
            <div style="margin-top:0.5rem;color:#e8ede9;font-weight:600;">₹75,000 hardware per ward</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_d3:
    st.markdown("""
    <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1.25rem;">
        <div style="font-size:0.75rem;color:#fbbf24;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.75rem;">📊 ROI</div>
        <div style="font-size:0.8rem;color:#6b8f74;line-height:1.8;">
            <div>• 22% truck route reduction</div>
            <div>• ₹2.1L/month saved per ward</div>
            <div>• Landfill life extended ~8 yrs</div>
            <div>• Carbon credits: ₹800/tonne CO₂</div>
            <div style="margin-top:0.5rem;color:#e8ede9;font-weight:600;">ROI breakeven: 18 months</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Team ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1rem 1.5rem;
            display:flex;align-items:center;justify-content:space-between;">
    <div>
        <div style="font-size:0.75rem;color:#6b8f74;text-transform:uppercase;letter-spacing:0.08em;">Team Sigmoid · JSS University</div>
        <div style="font-size:0.88rem;color:#e8ede9;margin-top:0.3rem;">
            Rehaan Ahmad Khan &nbsp;·&nbsp; Krishna Agarwaal &nbsp;·&nbsp; Daksh Kumar
        </div>
    </div>
    <div style="font-size:0.75rem;color:#4ade80;font-family:'DM Mono',monospace;text-align:right;">
        India Innovates 2026<br>
        <span style="color:#6b8f74;">Bharat Mandapam, New Delhi</span>
    </div>
</div>
""", unsafe_allow_html=True)