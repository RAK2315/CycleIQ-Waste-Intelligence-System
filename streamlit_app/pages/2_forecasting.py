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
.stSelectbox > div > div > div { background: #111a15 !important; border: 1px solid #1e2e24 !important; color: #e8ede9 !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000/api"

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