import streamlit as st
import requests

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header { visibility: visible; }
.stApp { background: #0a0f0d; color: #e8ede9; }
.block-container { padding: 1.5rem 2rem; max-width: 900px; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
.stButton > button { background: #111a15 !important; color: #6b8f74 !important; border: 1px solid #1e2e24 !important; border-radius: 8px !important; font-size: 0.8rem !important; font-weight: 400 !important; padding: 0.35rem 0.9rem !important; transition: all 0.15s !important; }
.stButton > button:hover { color: #4ade80 !important; border-color: #166534 !important; }
.stTextInput > div > div > input { background: #111a15 !important; border: 1px solid #1e2e24 !important; color: #e8ede9 !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; padding: 0.75rem 1rem !important; }
.stTextInput > div > div > input:focus { border-color: #166534 !important; box-shadow: 0 0 0 3px rgba(22,101,52,0.15) !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.msg-user { background:#0d2818; border:1px solid #166534; border-radius:14px 14px 4px 14px; padding:0.75rem 1rem; margin:0.5rem 0 0.5rem 3rem; font-size:0.9rem; color:#dcfce7; line-height:1.6; }
.msg-assistant { background:#111a15; border:1px solid #1e2e24; border-radius:14px 14px 14px 4px; padding:0.75rem 1rem; margin:0.5rem 3rem 0.5rem 0; font-size:0.9rem; color:#e8ede9; line-height:1.6; }
.msg-label { font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.25rem; }
.msg-label.user { color:#4ade80; text-align:right; margin-right:0; }
.msg-label.assistant { color:#6b8f74; }
.thinking { color:#2d4a36; font-style:italic; font-size:0.85rem; }
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

st.markdown('<div class="page-header"><h1>AI Assistant</h1><span>Llama 3.1 via Groq</span></div>', unsafe_allow_html=True)

# Init chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Namaste! I'm your CycleIQ assistant — I can help you analyze waste data, identify problem areas, and give you actionable insights for Delhi's waste management. What would you like to know?"
    })

# Suggested queries
try:
    suggestions = requests.get(f"{API}/dashboard/suggested-queries", timeout=3).json()
except:
    suggestions = [
        "Which wards need urgent waste collection today?",
        "What is the waste composition trend this week?",
        "How can we improve citizen segregation rates?",
    ]

if len(st.session_state.messages) == 1:
    st.markdown("**Suggested queries**")
    cols = st.columns(3)
    for i, q in enumerate(suggestions[:6]):
        with cols[i % 3]:
            if st.button(q, key=f"sugg_{i}"):
                st.session_state.pending_query = q
                st.rerun()

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-label user">You</div><div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-label assistant">CycleIQ Assistant</div><div class="msg-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

# Input
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
col_input, col_btn = st.columns([6, 1])
with col_input:
    user_input = st.text_input("Ask anything about Delhi's waste data...", key="chat_input", label_visibility="collapsed")
with col_btn:
    send = st.button("Send", use_container_width=True)

# Handle pending (from suggestion buttons)
if "pending_query" in st.session_state:
    user_input = st.session_state.pending_query
    del st.session_state.pending_query
    send = True

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner(""):
        try:
            r = requests.post(f"{API}/dashboard/query", json={"message": user_input}, timeout=30)
            reply = r.json().get("response", "Sorry, I couldn't process that.")
        except Exception as e:
            reply = f"Connection error: {e}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# Clear button
if len(st.session_state.messages) > 1:
    if st.button("Clear conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()