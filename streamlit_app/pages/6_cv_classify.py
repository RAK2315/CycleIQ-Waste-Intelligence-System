import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import io, time

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0a0f0d; color: #e8ede9; }
.block-container { padding: 1.5rem 2rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: #0d1410 !important; border-right: 1px solid #1e2e24; }
[data-testid="metric-container"] { background: #111a15 !important; border: 1px solid #1e2e24 !important; border-radius: 12px !important; padding: 1rem !important; }
[data-testid="metric-container"] label { color: #6b8f74 !important; font-size: 0.72rem !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8ede9 !important; font-size: 1.6rem !important; font-weight: 600 !important; font-family: 'DM Mono', monospace !important; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; padding: 0.6rem 1.5rem !important; }
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.live-badge { display:inline-flex; align-items:center; gap:0.4rem; background:#1a0000; border:1px solid #ef444440; border-radius:20px; padding:3px 12px; font-size:0.75rem; color:#ef4444; font-weight:600; }
.score-excellent { color:#4ade80; font-weight:700; }
.score-good { color:#86efac; font-weight:700; }
.score-fair { color:#fbbf24; font-weight:700; }
.score-poor { color:#ef4444; font-weight:700; }
.info-box { background:#0d2818; border:1px solid #166534; border-radius:10px; padding:0.75rem 1rem; font-size:0.82rem; color:#86efac; margin-bottom:1rem; }
.warn-box { background:#1a1200; border:1px solid #f59e0b40; border-radius:10px; padding:0.75rem 1rem; font-size:0.78rem; color:#fbbf24; margin-top:0.75rem; }
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

@st.cache_data(ttl=60)
def load_collection_points():
    return requests.get(f"{API}/waste/collection-points", timeout=5).json()

st.markdown('<div class="page-header"><h1>Waste Classifier</h1><span>YOLOv8 + Live Camera</span></div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    AI-vision waste classification at source. Classifies waste into biodegradable, recyclable, and hazardous categories.
    Results are linked to collection points — triggering route updates and citizen segregation scoring.
</div>
""", unsafe_allow_html=True)

# Mode selector
mode = st.radio("Input Mode", ["📷 Live Camera", "🖼️ Upload Image"],
                horizontal=True, label_visibility="collapsed")

try:
    points = load_collection_points()
    point_names = [p["name"] for p in points]
except:
    points = []
    point_names = ["Connaught Place Point 1"]

col_main, col_settings = st.columns([3, 2], gap="large")

with col_settings:
    st.markdown("**Collection Point**")
    selected_name = st.selectbox("Point", point_names, label_visibility="collapsed")
    selected_point = next((p for p in points if p["name"] == selected_name), {"id": "", "ward_id": "W001", "ward_name": "Unknown", "fill_level": 0})

    st.markdown(f"""
    <div style="background:#0a0f0d;border:1px solid #1e2e24;border-radius:10px;padding:0.8rem 1rem;
                font-size:0.78rem;color:#6b8f74;line-height:2;margin-bottom:1rem;">
        <div>Ward: <span style="color:#e8ede9;">{selected_point.get('ward_name','—')}</span></div>
        <div>Current Fill: <span style="color:#{'ef4444' if selected_point.get('fill_level',0)>75 else 'fbbf24' if selected_point.get('fill_level',0)>50 else '4ade80'};">{selected_point.get('fill_level',0):.0f}%</span></div>
        <div>Model: <span style="color:#e8ede9;">YOLOv8n</span></div>
        <div>Categories: <span style="color:#e8ede9;">Biodegradable · Recyclable · Hazardous</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Results placeholder — updated after classification
    result_placeholder = st.empty()

with col_main:
    if "📷 Live Camera" in mode:
        st.markdown("**Live Camera Feed**")
        try:
            from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
            import av
            import numpy as np
            import threading

            # Shared state for live results
            if "live_results" not in st.session_state:
                st.session_state.live_results = None
            if "frame_count" not in st.session_state:
                st.session_state.frame_count = 0

            class WasteVideoProcessor(VideoProcessorBase):
                def __init__(self):
                    self.results = None
                    self.frame_count = 0
                    self._lock = threading.Lock()
                    # Load YOLO
                    try:
                        from ultralytics import YOLO
                        self.model = YOLO("yolov8n.pt")
                    except:
                        self.model = None

                    self.YOLO_TO_WASTE = {
                        "bottle": "recyclable", "wine glass": "recyclable", "cup": "recyclable",
                        "can": "recyclable", "fork": "recyclable", "knife": "recyclable",
                        "spoon": "recyclable", "book": "recyclable", "scissors": "recyclable",
                        "banana": "biodegradable", "apple": "biodegradable", "sandwich": "biodegradable",
                        "orange": "biodegradable", "broccoli": "biodegradable", "carrot": "biodegradable",
                        "pizza": "biodegradable", "donut": "biodegradable", "potted plant": "biodegradable",
                        "remote": "hazardous", "cell phone": "hazardous", "laptop": "hazardous",
                        "tv": "hazardous", "keyboard": "hazardous", "mouse": "hazardous",
                    }
                    self.COLORS = {
                        "biodegradable": (74, 222, 128),    # green
                        "recyclable": (96, 165, 250),       # blue
                        "hazardous": (248, 113, 113),       # red
                    }

                def recv(self, frame):
                    import cv2
                    img = frame.to_ndarray(format="bgr24")
                    self.frame_count += 1

                    # Run YOLO every 10 frames for performance
                    if self.frame_count % 10 == 0 and self.model:
                        try:
                            results = self.model(img, verbose=False)
                            category_counts = {"biodegradable": 0, "recyclable": 0, "hazardous": 0}
                            for result in results:
                                for box in result.boxes:
                                    cls_name = result.names[int(box.cls)].lower()
                                    conf = float(box.conf)
                                    if conf >= 0.3:
                                        waste_cat = self.YOLO_TO_WASTE.get(cls_name)
                                        if waste_cat:
                                            category_counts[waste_cat] += 1
                                            # Draw bounding box
                                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                                            color = self.COLORS[waste_cat]
                                            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                                            label = f"{waste_cat} {conf:.0%}"
                                            cv2.putText(img, label, (x1, y1-8),
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                            total = sum(category_counts.values()) or 1
                            with self._lock:
                                self.results = {k: round(v/total*100, 1) for k, v in category_counts.items()}
                        except Exception as e:
                            pass

                    # Draw overlay HUD on frame
                    h, w = img.shape[:2]

                    # Solid dark top bar for title
                    cv2.rectangle(img, (0, 0), (w, 55), (8, 16, 12), -1)
                    cv2.putText(img, "CycleIQ LIVE", (12, 24),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (74, 222, 128), 2)
                    cv2.putText(img, "YOLOv8 Waste Detection", (12, 46),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 220, 190), 1)

                    # Draw results panel with solid background
                    with self._lock:
                        if self.results:
                            panel_x = w - 220
                            panel_h = len(self.results) * 32 + 20
                            # Solid dark background for results panel
                            cv2.rectangle(img, (panel_x - 8, 60), (w - 4, 60 + panel_h), (8, 16, 12), -1)
                            cv2.rectangle(img, (panel_x - 8, 60), (w - 4, 60 + panel_h), (30, 60, 40), 1)
                            y_pos = 85
                            for cat, pct in self.results.items():
                                color = self.COLORS.get(cat, (200,200,200))
                                # Category label
                                cv2.putText(img, f"{cat.upper()[:4]}", (panel_x, y_pos),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                                # Bar background
                                cv2.rectangle(img, (panel_x + 52, y_pos - 12), (w - 10, y_pos - 2), (30, 40, 35), -1)
                                # Bar fill
                                bar_w = max(0, int((w - 10 - panel_x - 52) * pct / 100))
                                cv2.rectangle(img, (panel_x + 52, y_pos - 12), (panel_x + 52 + bar_w, y_pos - 2), color, -1)
                                # Percentage text with background
                                pct_text = f"{pct:.0f}%"
                                cv2.putText(img, pct_text, (w - 48, y_pos),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)
                                y_pos += 32

                    return av.VideoFrame.from_ndarray(img, format="bgr24")

            ctx = webrtc_streamer(
                key="waste-classifier",
                video_processor_factory=WasteVideoProcessor,
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )

            if ctx.video_processor:
                # Live updating results panel
                result_placeholder.markdown("""
                <div style="background:#111a15;border:1px solid #1e2e24;border-radius:12px;padding:1rem;">
                    <div style="font-size:0.7rem;color:#4ade80;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.75rem;">
                        Live Classification
                        <span style="display:inline-block;width:6px;height:6px;background:#ef4444;border-radius:50%;margin-left:6px;"></span>
                    </div>
                    <div style="font-size:0.82rem;color:#6b8f74;">Point camera at waste items — results update every 10 frames</div>
                </div>
                """, unsafe_allow_html=True)

                # Capture & save button
                if st.button("Capture & Save Classification"):
                    try:
                        with ctx.video_processor._lock:
                            live_res = dict(ctx.video_processor.results) if ctx.video_processor.results else None
                    except Exception:
                        live_res = None

                    if live_res:
                        bio = live_res.get("biodegradable", 0)
                        rec = live_res.get("recyclable", 0)
                        haz = live_res.get("hazardous", 0)
                        total = bio + rec + haz or 100

                        # Build a minimal PNG to send to the classify endpoint
                        import numpy as np
                        from PIL import Image
                        import io as _io
                        # Create a small dummy image so the endpoint accepts it
                        dummy = Image.fromarray(np.zeros((10,10,3), dtype=np.uint8))
                        buf = _io.BytesIO()
                        dummy.save(buf, format="PNG")
                        buf.seek(0)

                        try:
                            resp = requests.post(
                                f"{API}/waste/classify",
                                files={"file": ("live_capture.png", buf, "image/png")},
                                params={
                                    "ward_id": selected_point.get("ward_id", "W001"),
                                    "collection_point_id": selected_point.get("id", ""),
                                    "organic_pct": round(bio * 0.7, 2),
                                    "plastic_pct": round(rec * 0.5, 2),
                                    "paper_pct": round(rec * 0.3, 2),
                                    "metal_pct": round(rec * 0.2, 2),
                                    "glass_pct": 0,
                                    "hazardous_pct": round(haz, 2),
                                },
                                timeout=10
                            )
                            result = resp.json()
                            st.session_state.last_result = result
                            pts = result.get("points_awarded_to_ward", 0)
                            st.success(f"Saved! Segregation: {result.get('segregation_label','—')} · {pts} pts awarded to ward")
                        except Exception as e:
                            st.error(f"API error: {e}")
                    else:
                        st.warning("No classification data yet — point camera at waste and wait a moment.")

        except ImportError:
            st.markdown("""
            <div class="warn-box">
                <strong>streamlit-webrtc not installed.</strong><br>
                Run: <code>pip install streamlit-webrtc</code> then restart Streamlit.
            </div>
            """, unsafe_allow_html=True)
            st.info("Use 'Upload Image' mode below while you install the package.")

    else:
        # Upload mode
        st.markdown("**Upload Waste Image**")
        uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"],
                                     label_visibility="collapsed")
        if uploaded:
            from PIL import Image
            img = Image.open(uploaded)
            st.image(img, use_container_width=True, caption="Uploaded image")

        if st.button("Classify Waste") and uploaded:
            with st.spinner("Running YOLOv8 inference..."):
                try:
                    uploaded.seek(0)
                    files = {"file": (uploaded.name, uploaded.read(), uploaded.type)}
                    params = {"ward_id": selected_point.get("ward_id","W001"),
                              "collection_point_id": selected_point.get("id","")}
                    r = requests.post(f"{API}/waste/classify", files=files,
                                      params=params, timeout=30)
                    result = r.json()
                    st.session_state.last_result = result
                except Exception as e:
                    st.error(f"Classification failed: {e}")

# Show results
if "last_result" in st.session_state:
    result = st.session_state.last_result
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    dominant_map = {
        "organic_pct": "Biodegradable", "plastic_pct": "Recyclable (Plastic)",
        "paper_pct": "Recyclable (Paper)", "metal_pct": "Recyclable (Metal)",
        "glass_pct": "Recyclable (Glass)", "hazardous_pct": "Hazardous"
    }
    pct_keys = ["organic_pct","plastic_pct","paper_pct","metal_pct","glass_pct","hazardous_pct"]
    dominant_key = max(pct_keys, key=lambda k: result.get(k, 0))
    with c1: st.metric("Dominant Category", dominant_map[dominant_key])
    with c2: st.metric("Confidence", f"{result.get('confidence_score',0)*100:.1f}%")
    seg_score = result.get("segregation_score", 0)
    seg_label = result.get("segregation_label", "—")
    score_color = "score-excellent" if seg_score>=80 else "score-good" if seg_score>=65 else "score-fair" if seg_score>=50 else "score-poor"
    with c3: st.metric("Segregation Score", f"{seg_score:.0f}/100")
    with c4: st.metric("Segregation Quality", seg_label)

    col_bars, col_chart = st.columns(2, gap="large")
    categories = {
        "Biodegradable (Organic)": (result.get("organic_pct",0), "#4ade80"),
        "Recyclable — Plastic": (result.get("plastic_pct",0), "#60a5fa"),
        "Recyclable — Paper": (result.get("paper_pct",0), "#fbbf24"),
        "Recyclable — Metal": (result.get("metal_pct",0), "#a78bfa"),
        "Recyclable — Glass": (result.get("glass_pct",0), "#34d399"),
        "Hazardous": (result.get("hazardous_pct",0), "#f87171"),
    }

    with col_bars:
        st.markdown("**Waste Breakdown**")
        for cat, (pct, color) in sorted(categories.items(), key=lambda x: x[1][0], reverse=True):
            st.markdown(f"""
            <div style="margin-bottom:0.7rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:0.82rem;color:#e8ede9;">{cat}</span>
                    <span style="font-family:'DM Mono',monospace;font-size:0.82rem;color:{color};font-weight:600;">{pct:.1f}%</span>
                </div>
                <div style="background:#1e2e24;border-radius:4px;height:7px;">
                    <div style="background:{color};width:{min(int(pct),100)}%;height:7px;border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if result.get("points_awarded_to_ward", 0) > 0:
            st.markdown(f"""
            <div style="margin-top:1rem;background:#0d2818;border:1px solid #166534;border-radius:8px;
                        padding:0.6rem 0.9rem;font-size:0.8rem;color:#4ade80;">
                +{result['points_awarded_to_ward']} points awarded to citizens in {result.get('ward_id','this ward')}
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        fig = go.Figure(go.Pie(
            labels=[c.split("—")[-1].strip() if "—" in c else c for c in categories.keys()],
            values=[v[0] for v in categories.values()],
            hole=0.5,
            marker_colors=[v[1] for v in categories.values()],
            textinfo="label+percent",
            textfont=dict(family="DM Sans", size=11),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#9ca3af"),
            margin=dict(l=0,r=0,t=20,b=0), height=300,
            showlegend=False,
            annotations=[dict(text=dominant_map[dominant_key].split("(")[0].strip(),
                              x=0.5, y=0.5, font_size=12, font_color="#4ade80", showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

        mode_tag = result.get("mode","unknown")
        mode_color = "#4ade80" if mode_tag=="yolo" else "#60a5fa" if mode_tag=="image-aware" else "#f59e0b"
        st.markdown(f"""
        <div style="background:#0a0f0d;border:1px solid #1e2e24;border-radius:8px;padding:0.6rem 0.9rem;
                    font-size:0.75rem;color:#6b8f74;">
            Inference mode: <span style="color:{mode_color};font-weight:600;">{mode_tag}</span><br>
            <span style="font-size:0.7rem;">{result.get('note','')}</span>
        </div>
        """, unsafe_allow_html=True)

# Recent classifications
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown("**Recent Classifications**")
try:
    recent = requests.get(f"{API}/waste/classifications?limit=10", timeout=5).json()
    if recent:
        for i, r in enumerate(recent[:8]):
            recyclable = r["plastic_pct"] + r["paper_pct"] + r["metal_pct"] + r["glass_pct"]
            bio = r["organic_pct"]
            haz = r["hazardous_pct"]
            if bio >= recyclable and bio >= haz:
                dominant, dom_color = "Biodegradable", "#4ade80"
            elif haz > recyclable and haz > bio:
                dominant, dom_color = "Hazardous", "#f87171"
            else:
                dominant, dom_color = "Recyclable", "#60a5fa"
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.55rem 0.9rem;
                        background:#111a15;border:1px solid #1e2e24;border-radius:8px;
                        margin-bottom:0.4rem;gap:1rem;">
                <div style="font-size:0.7rem;color:#6b8f74;font-family:'DM Mono',monospace;min-width:24px;">#{i+1}</div>
                <div style="min-width:110px;">
                    <div style="font-size:0.82rem;color:{dom_color};font-weight:600;">{dominant}</div>
                    <div style="font-size:0.7rem;color:#6b8f74;">Ward {r['ward_id']}</div>
                </div>
                <div style="display:flex;gap:1.2rem;font-family:'DM Mono',monospace;font-size:0.78rem;">
                    <div style="text-align:center;">
                        <div style="color:#4ade80;font-weight:600;">{bio:.0f}%</div>
                        <div style="color:#6b8f74;font-size:0.65rem;">Bio</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="color:#60a5fa;font-weight:600;">{recyclable:.0f}%</div>
                        <div style="color:#6b8f74;font-size:0.65rem;">Recyclable</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="color:#f87171;font-weight:600;">{haz:.0f}%</div>
                        <div style="color:#6b8f74;font-size:0.65rem;">Hazardous</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="color:#e8ede9;font-weight:600;">{r['confidence_score']*100:.0f}%</div>
                        <div style="color:#6b8f74;font-size:0.65rem;">Confidence</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
except:
    st.info("No recent classifications.")