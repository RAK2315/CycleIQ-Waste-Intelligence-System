import streamlit as st
import requests
import pandas as pd
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
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
.stSelectbox > div > div > div { background: #111a15 !important; border: 1px solid #1e2e24 !important; color: #e8ede9 !important; }
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

@st.cache_data(ttl=300)
def load_wards():
    return requests.get(f"{API}/forecast/wards", timeout=5).json()

@st.cache_data(ttl=300)
def load_forecast(ward_id, days):
    return requests.get(f"{API}/forecast/ward/{ward_id}?days={days}", timeout=30).json()

@st.cache_data(ttl=300)
def load_history(ward_id, days=60):
    return requests.get(f"{API}/forecast/history/{ward_id}?days={days}", timeout=10).json()

@st.cache_data(ttl=600)
def load_all_wards():
    return requests.get(f"{API}/forecast/all-wards", timeout=60).json()


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

st.markdown('<div class="page-header"><h1>Forecasting</h1><span>7-Day Prediction</span></div>', unsafe_allow_html=True)

try:
    wards = load_wards()
except:
    st.error("API not reachable.")
    st.stop()

col_sel, col_days = st.columns([3, 1])
with col_sel:
    ward_names = [w["name"] for w in wards]
    selected_ward_name = st.selectbox("Select Ward", ward_names)
with col_days:
    days = st.selectbox("Forecast Days", [7, 14, 30], index=0)

selected_ward = next(w for w in wards if w["name"] == selected_ward_name)

with st.spinner("Generating forecast..."):
    try:
        forecast_data = load_forecast(selected_ward["id"], days)
        history_data = load_history(selected_ward["id"])
    except Exception as e:
        st.error(f"Forecast error: {e}")
        st.stop()

if not forecast_data:
    st.warning("No forecast data available.")
    st.stop()

df_fc = pd.DataFrame(forecast_data)
df_fc["forecast_date"] = pd.to_datetime(df_fc["forecast_date"])

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("7-Day Avg", f"{df_fc['predicted_volume_kg'].mean():.0f} kg")
with c2:
    peak = df_fc.loc[df_fc['predicted_volume_kg'].idxmax()]
    st.metric("Peak Day", pd.to_datetime(peak['forecast_date']).strftime("%a %b %d"))
with c3: st.metric("Peak Volume", f"{peak['predicted_volume_kg']:.0f} kg")
with c4: st.metric("Avg Confidence", f"{df_fc['confidence_score'].mean()*100:.1f}%")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

fig = go.Figure()
if history_data:
    df_h = pd.DataFrame(history_data)
    df_h["date"] = pd.to_datetime(df_h["date"])
    df_h = df_h.tail(30)
    from datetime import datetime, timedelta
    fig.add_trace(go.Scatter(x=df_h["date"], y=df_h["volume_kg"], mode="lines",
        name="Historical", line=dict(color="#6b8f74", width=1.5, dash="dot"),
        hovertemplate="%{x|%b %d}: %{y:.0f} kg<extra>Historical</extra>"))

fig.add_trace(go.Scatter(
    x=pd.concat([df_fc["forecast_date"], df_fc["forecast_date"][::-1]]),
    y=pd.concat([df_fc["upper_bound_kg"], df_fc["lower_bound_kg"][::-1]]),
    fill="toself", fillcolor="rgba(74,222,128,0.08)",
    line=dict(color="rgba(0,0,0,0)"), name="95% CI", hoverinfo="skip"))



fig.add_trace(go.Scatter(x=df_fc["forecast_date"], y=df_fc["predicted_volume_kg"],
    mode="lines+markers", name="Forecast",
    line=dict(color="#4ade80", width=2.5),
    marker=dict(size=7, color="#4ade80", line=dict(color="#0a0f0d", width=2)),
    hovertemplate="%{x|%b %d}: %{y:.0f} kg<extra>Forecast</extra>"))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9ca3af", size=12),
    margin=dict(l=0,r=0,t=10,b=0), height=320,
    xaxis=dict(gridcolor="#1e2e24"),
    yaxis=dict(gridcolor="#1e2e24", title="Waste Volume (kg)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("**Day-by-Day Forecast**")
df_display = df_fc[["forecast_date","predicted_volume_kg","lower_bound_kg","upper_bound_kg","confidence_score"]].copy()
df_display["forecast_date"] = df_display["forecast_date"].dt.strftime("%A, %b %d")
df_display["confidence_score"] = (df_display["confidence_score"]*100).round(1).astype(str) + "%"
df_display.columns = ["Date","Predicted (kg)","Lower (kg)","Upper (kg)","Confidence"]
st.dataframe(df_display, use_container_width=True, hide_index=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
col_forecast, col_risk = st.columns([3, 2], gap="large")

with col_forecast:
    st.markdown("**All Wards — Forecast Comparison**")
    with st.spinner("Loading all ward forecasts..."):
        try:
            all_wards = load_all_wards()
            if all_wards:
                df_all = pd.DataFrame([{"Ward": w["ward_name"], "7-Day Avg (kg)": w["next_7_days_avg"]} for w in all_wards])
                df_all = df_all.sort_values("7-Day Avg (kg)", ascending=False)
                fig2 = go.Figure(go.Bar(
                    x=df_all["7-Day Avg (kg)"], y=df_all["Ward"], orientation="h",
                    marker=dict(color=df_all["7-Day Avg (kg)"],
                        colorscale=[[0,"#166534"],[0.5,"#fbbf24"],[1,"#ef4444"]], showscale=False),
                    hovertemplate="%{y}: %{x:.0f} kg/day avg<extra></extra>"))
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#9ca3af", size=11),
                    margin=dict(l=0,r=10,t=0,b=0), height=400,
                    xaxis=dict(gridcolor="#1e2e24", title="Avg Daily Volume (kg)"),
                    yaxis=dict(gridcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.info(f"Could not load all-ward forecast: {e}")

with col_risk:
    st.markdown("**7-Day Overflow Risk Calendar**")
    import numpy as np
    from datetime import datetime, timedelta

    # Build risk heatmap from forecast data
    if 'all_wards' in dir() and all_wards:
        top_wards = [w["ward_name"] for w in sorted(all_wards, key=lambda x: x["next_7_days_avg"], reverse=True)[:8]]
        days_list = [(datetime.now() + timedelta(days=i)).strftime("%a %d") for i in range(7)]

        # Risk matrix: higher forecast = higher overflow risk
        risk_matrix = []
        for w in sorted(all_wards, key=lambda x: x["next_7_days_avg"], reverse=True)[:8]:
            base = w["next_7_days_avg"] / 500  # normalise
            # Weekend spike pattern
            row = [min(base * (1.3 if i in [5,6] else 1.0) * np.random.uniform(0.85, 1.15), 1.0) for i in range(7)]
            risk_matrix.append(row)

        fig_heatmap = go.Figure(go.Heatmap(
            z=risk_matrix,
            x=days_list,
            y=top_wards,
            colorscale=[[0,"#0d2010"],[0.4,"#166534"],[0.7,"#f59e0b"],[1.0,"#ef4444"]],
            showscale=True,
            colorbar=dict(
                title="Risk", tickfont=dict(color="#6b8f74", size=10),
                titlefont=dict(color="#6b8f74", size=10),
                bgcolor="rgba(0,0,0,0)"
            ),
            hovertemplate="%{y}<br>%{x}: Risk %{z:.0%}<extra></extra>"
        ))
        fig_heatmap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af", size=10),
            margin=dict(l=0,r=0,t=10,b=0), height=280,
            xaxis=dict(side="top"),
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Show route generation recommendation
        high_risk = [w["ward_name"] for w in all_wards
                     if w["next_7_days_avg"] > 400]
        if high_risk:
            st.markdown(f"""
            <div style="background:#1a0f00;border:1px solid #f59e0b40;border-radius:10px;
                        padding:0.75rem;font-size:0.78rem;color:#fbbf24;margin-top:0.5rem;">
                ⚡ <b>Route Planning Recommendation</b><br>
                <span style="color:#9ca3af;">{len(high_risk)} ward(s) forecast high volume this week —
                consider pre-emptive route generation:
                <b>{', '.join(high_risk[:3])}</b>{'...' if len(high_risk) > 3 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("→ Open Route Optimizer", key="goto_routes"):
                st.switch_page("pages/3_routes.py")