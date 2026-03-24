import streamlit as st
import tempfile
import os
import requests as _req





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
.page-header { display:flex; align-items:baseline; gap:0.75rem; margin-bottom:1rem; padding-bottom:1rem; border-bottom:1px solid #1e2e24; }
.page-header h1 { font-size:1.6rem; font-weight:700; color:#e8ede9; margin:0; }
.page-header span { font-size:0.8rem; color:#4ade80; font-family:'DM Mono',monospace; background:#0d2818; padding:2px 10px; border-radius:20px; border:1px solid #166534; }
.stButton > button { background: #166534 !important; color: #dcfce7 !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

import os as _os, requests as _req2
def _get_api():
    render = _os.getenv("API_URL", "https://cycleiq-api.onrender.com") + "/api"
    local  = "http://localhost:8000/api"
    try:
        _req2.get(f"{local}/health", timeout=2)
        return local
    except:
        return render
API = _get_api()

st.markdown('<div class="page-header"><h1>Bin Monitor</h1><span>Segregation Detection</span></div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:#0d2010;border:1px solid #4ade8030;border-radius:10px;
            padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:#86efac;">
    Upload a top-down video of waste being sorted into bins.
    CycleIQ detects what's being thrown, which bin it lands in, and whether it's correct.
    Ward points are awarded for correct segregation.
</div>
""", unsafe_allow_html=True)

# ── Bin configuration ────────────────────────────────────────────────────────
BIN_CONFIG = [
    {"label": "Plastic & Metal",    "color": (96, 165, 250),   "hex": "#60a5fa", "emoji": "🔵", "top_offset": 0.08},
    {"label": "Glass & Ceramic",    "color": (52, 211, 153),   "hex": "#34d399", "emoji": "🟢", "top_offset": 0.02},
    {"label": "Hazardous & E-Waste","color": (248, 113, 113),  "hex": "#f87171", "emoji": "🔴", "top_offset": 0.02},
    {"label": "Paper & Cardboard",  "color": (251, 191, 36),   "hex": "#fbbf24", "emoji": "🟡", "top_offset": 0.08},
]

# YOLO class → (correct bin index, display name)
YOLO_WASTE_MAP = {
    "bottle":       (0, "Plastic Bottle"),
    "cup":          (0, "Plastic Cup"),
    "can":          (0, "Metal Can"),
    "fork":         (0, "Metal Fork"),
    "knife":        (0, "Metal Knife"),
    "spoon":        (0, "Metal Spoon"),
    "wine glass":   (1, "Glass"),
    "vase":         (1, "Glass Vase"),
    "bowl":         (1, "Glass Bowl"),
    "book":         (3, "Paper/Book"),
    "scissors":     (3, "Cardboard/Paper"),
    "suitcase":     (3, "Cardboard Box"),
    "cell phone":   (2, "E-Waste"),
    "laptop":       (2, "E-Waste"),
    "remote":       (2, "E-Waste"),
    "keyboard":     (2, "E-Waste"),
    "mouse":        (2, "E-Waste"),
    "tv":           (2, "E-Waste"),
    "banana":       (-1, "Organic ❌"),
    "apple":        (-1, "Organic ❌"),
    "orange":       (-1, "Organic ❌"),
    "sandwich":     (-1, "Organic ❌"),
    "pizza":        (-1, "Organic ❌"),
    "carrot":       (-1, "Organic ❌"),
    "broccoli":     (-1, "Organic ❌"),
}

# ── Sidebar config ───────────────────────────────────────────────────────────

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
# ── Upload ───────────────────────────────────────────────────────────────────
uploaded_video = st.file_uploader(
    "Upload bin sorting video", 
    type=["mp4","avi","mov","webm"],
    label_visibility="collapsed"
)

if not uploaded_video:
    st.markdown("""
    <div style="background:#111a15;border:2px dashed #1e2e24;border-radius:12px;
                padding:3rem;text-align:center;color:#6b8f74;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">📹</div>
        <div style="font-size:0.9rem;">Upload a top-down video of waste being sorted into bins</div>
        <div style="font-size:0.75rem;margin-top:0.4rem;">MP4, AVI, MOV supported</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Process video ────────────────────────────────────────────────────────────
if st.button("▶ Analyse Video", use_container_width=False):
    import cv2
    import numpy as np
    confidence_threshold = 0.15
    process_every_n = 2

    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_video.read())
        tmp_path = tmp.name

    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
        yolo_available = True
    except Exception as e:
        st.warning(f"YOLOv8 not available locally: {e}. Using simulation mode.")
        yolo_available = False

    cap = cv2.VideoCapture(tmp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Zone boundaries — 4 equal vertical strips
    zone_boundaries = [
        (0,                  frame_w // 4),
        (frame_w // 4,       frame_w // 2),
        (frame_w // 2,       3 * frame_w // 4),
        (3 * frame_w // 4,   frame_w),
    ]

    # Capture baseline frame (empty bins)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, baseline_frame = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    if not ret:
        baseline_frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)

    # Tracking state
    events = []          # list of detection events
    bin_counts = [0, 0, 0, 0]       # items correctly in each bin
    bin_wrong = [0, 0, 0, 0]        # wrong items in each bin
    bin_fill_px = [0, 0, 0, 0]      # pixel fill estimate
    total_correct = 0
    total_wrong = 0
    processed_frames = []

    progress = st.progress(0, text="Analysing video...")
    frame_display = st.empty()
    status_cols = st.columns(4)

    frame_idx = 0
    last_detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        progress.progress(min(frame_idx / total_frames, 1.0),
                         text=f"Analysing frame {frame_idx}/{total_frames}...")

        # Draw zone overlays on every frame
        annotated = frame.copy()

        # Draw bin zone overlays
        for i, (x1, x2) in enumerate(zone_boundaries):
            cfg = BIN_CONFIG[i]
            color = cfg["color"]
            top_off = int(frame_h * cfg.get("top_offset", 0.02))
            bin_bottom = int(frame_h * 0.50)
            # Semi-transparent zone fill
            overlay = annotated.copy()
            cv2.rectangle(overlay, (x1, top_off), (x2, bin_bottom), color, -1)
            cv2.addWeighted(overlay, 0.12, annotated, 0.88, 0, annotated)
            # Zone border line
            cv2.line(annotated, (x2, top_off), (x2, bin_bottom), color, 2)
            cv2.line(annotated, (x1, top_off), (x2, top_off), color, 1)
            cv2.line(annotated, (x1, bin_bottom), (x2, bin_bottom), color, 1)
            # Bin label
            label = cfg["label"]
            cv2.rectangle(annotated, (x1 + 4, top_off + 4), (x1 + 4 + len(label)*11 + 8, top_off + 34), (10, 16, 12), -1)
            cv2.putText(annotated, label, (x1 + 8, top_off + 26),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        # Run YOLO every N frames
        if frame_idx % process_every_n == 0 and yolo_available:
            try:
                results = model(frame, verbose=False, conf=confidence_threshold)
                last_detections = []
                for result in results:
                    for box in result.boxes:
                        cls_name = result.names[int(box.cls)].lower()
                        conf = float(box.conf)
                        x1b, y1b, x2b, y2b = map(int, box.xyxy[0])
                        center_x = (x1b + x2b) // 2
                        center_y = (y1b + y2b) // 2

                        # Only care about items in the lower half (being held/thrown)
                        if center_y < frame_h * 0.45:
                            continue

                        if cls_name in YOLO_WASTE_MAP:
                            correct_bin, item_name = YOLO_WASTE_MAP[cls_name]
                            last_detections.append({
                                "cls": cls_name,
                                "item": item_name,
                                "conf": conf,
                                "box": (x1b, y1b, x2b, y2b),
                                "center_x": center_x,
                                "center_y": center_y,
                                "correct_bin": correct_bin,
                            })
            except Exception as e:
                pass

        # Draw last detections
        for det in last_detections:
            x1b, y1b, x2b, y2b = det["box"]
            correct_bin = det["correct_bin"]
            center_x = det["center_x"]
            center_y = det["center_y"]

            # Determine which zone item is in
            item_zone = -1
            for zi, (zx1, zx2) in enumerate(zone_boundaries):
                if zx1 <= center_x < zx2:
                    item_zone = zi
                    break

            if correct_bin == -1:
                # Organic — always wrong
                box_color = (239, 68, 68)
                label_text = f"{det['item']} WRONG BIN!"
                is_correct = False
            elif item_zone == correct_bin:
                box_color = BIN_CONFIG[correct_bin]["color"]
                label_text = f"{det['item']} ✓ {BIN_CONFIG[correct_bin]['label']}"
                is_correct = True
            elif item_zone >= 0:
                box_color = (239, 68, 68)
                label_text = f"{det['item']} ✗ Should→{BIN_CONFIG[correct_bin]['label']}"
                is_correct = False
            else:
                continue

            # Draw bounding box
            cv2.rectangle(annotated, (x1b, y1b), (x2b, y2b), box_color, 2)
            # Label background
            label_w = len(label_text) * 9 + 8
            cv2.rectangle(annotated, (x1b, y2b + 2), (x1b + label_w, y2b + 24), (10, 16, 12), -1)
            cv2.putText(annotated, label_text, (x1b + 4, y2b + 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)

            # Log event (avoid duplicate events — only log if item crossing bin boundary)
            if frame_idx % (process_every_n * 5) == 0 and item_zone >= 0:
                events.append({
                    "frame": frame_idx,
                    "time": f"{frame_idx/fps:.1f}s",
                    "item": det["item"],
                    "zone": item_zone,
                    "correct_bin": correct_bin,
                    "correct": is_correct,
                    "conf": det["conf"],
                })
                if is_correct:
                    bin_counts[item_zone] += 1
                    total_correct += 1
                else:
                    if item_zone >= 0:
                        bin_wrong[item_zone] += 1
                    total_wrong += 1

        # HUD — top bar
        hud_h = 55
        cv2.rectangle(annotated, (0, frame_h - hud_h), (frame_w, frame_h), (8, 16, 12), -1)
        score_pct = int(total_correct / max(total_correct + total_wrong, 1) * 100)
        hud_text = f"CycleIQ Bin Monitor  |  Correct: {total_correct}  Wrong: {total_wrong}  |  Score: {score_pct}%"
        cv2.putText(annotated, hud_text, (12, frame_h - 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (74, 222, 128), 2)

        # Estimate fill levels — compare current frame bin zone to baseline (first frame)
        for i, (zx1, zx2) in enumerate(zone_boundaries):
            bin_region = frame[20:int(frame_h * 0.42), zx1+5:zx2-5]
            base_region = baseline_frame[20:int(frame_h * 0.42), zx1+5:zx2-5]
            # Diff against baseline — new objects in bin show up as changed pixels
            diff = cv2.absdiff(bin_region, base_region)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            changed_px = np.sum(diff_gray > 30)
            total_px = diff_gray.shape[0] * diff_gray.shape[1]
            bin_fill_px[i] = min(int(changed_px / total_px * 100 * 2.5), 95)

        # Store every 15th annotated frame for playback
        if frame_idx % 15 == 0:
            small = cv2.resize(annotated, (960, 540))
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            processed_frames.append(rgb)

        # Show live preview every 30 frames
        if frame_idx % 30 == 0 and processed_frames:
            frame_display.image(processed_frames[-1], use_container_width=True)

    cap.release()
    os.unlink(tmp_path)
    progress.empty()
    frame_display.empty()

    # ── Results ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Analysis Results")

    score_pct = int(total_correct / max(total_correct + total_wrong, 1) * 100)
    seg_label = "Excellent 🌟" if score_pct >= 80 else "Good ✅" if score_pct >= 65 else "Fair ⚠️" if score_pct >= 50 else "Poor ❌"
    score_color = "#4ade80" if score_pct >= 65 else "#f59e0b" if score_pct >= 50 else "#ef4444"

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Correct Disposals", total_correct)
    with c2: st.metric("Wrong Disposals", total_wrong)
    with c3: st.metric("Segregation Score", f"{score_pct}%")
    with c4: st.metric("Grade", seg_label.split()[0])

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # Bin summary cards
    st.markdown("**Per-Bin Summary**")
    bin_cols = st.columns(4)
    for i, (col, cfg) in enumerate(zip(bin_cols, BIN_CONFIG)):
        with col:
            fill = bin_fill_px[i]
            correct = bin_counts[i]
            wrong = bin_wrong[i]
            st.markdown(f"""
            <div style="background:#111a15;border:1px solid {cfg['hex']}40;border-radius:12px;padding:1rem;">
                <div style="font-size:0.7rem;color:{cfg['hex']};font-weight:700;text-transform:uppercase;
                            letter-spacing:0.05em;margin-bottom:0.5rem;">{cfg['emoji']} {cfg['label']}</div>
                <div style="font-size:1.4rem;font-weight:700;color:{cfg['hex']};
                            font-family:'DM Mono',monospace;">{fill}%</div>
                <div style="font-size:0.7rem;color:#6b8f74;margin-bottom:0.5rem;">fill level</div>
                <div style="background:#1e2e24;border-radius:3px;height:5px;margin-bottom:0.75rem;">
                    <div style="background:{cfg['hex']};width:{fill}%;height:5px;border-radius:3px;"></div>
                </div>
                <div style="font-size:0.75rem;color:#4ade80;">✓ {correct} correct</div>
                <div style="font-size:0.75rem;color:#ef4444;">✗ {wrong} wrong</div>
            </div>
            """, unsafe_allow_html=True)

    # Event log
    if events:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("**Detection Event Log**")
        for ev in events[-15:]:
            is_correct = ev["correct"]
            bin_cfg = BIN_CONFIG[ev["zone"]] if ev["zone"] >= 0 else {"hex": "#6b8f74", "label": "Unknown", "emoji": "?"}
            status_color = "#4ade80" if is_correct else "#ef4444"
            status_text = "✓ Correct" if is_correct else "✗ Wrong bin"
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.5rem 0.75rem;
                        background:#111a15;border:1px solid {'#4ade8030' if is_correct else '#ef444430'};
                        border-radius:8px;margin-bottom:0.3rem;gap:1rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#6b8f74;min-width:50px;">{ev['time']}</div>
                <div style="font-size:0.82rem;color:#e8ede9;flex:1;">{ev['item']}</div>
                <div style="font-size:0.75rem;color:{bin_cfg['hex']};">{bin_cfg['emoji']} {bin_cfg['label']}</div>
                <div style="font-size:0.75rem;font-weight:600;color:{status_color};">{status_text}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#6b8f74;">{ev['conf']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

    # Points award
    pts = score_pct * 5
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    if score_pct >= 50:
        st.markdown(f"""
        <div style="background:#0d2010;border:1px solid #4ade8040;border-radius:10px;
                    padding:1rem 1.2rem;font-size:0.85rem;color:#86efac;">
            🎯 <b>Ward {ward_id}</b> earned <span style="color:#4ade80;font-family:'DM Mono',monospace;
            font-weight:700;font-size:1rem;">{pts} points</span> for this segregation session.
            Grade: <b>{seg_label}</b>
        </div>
        """, unsafe_allow_html=True)

        # Post to API
        try:
            _req.post(f"{API}/waste/classify",
                files={"file": ("bin_monitor.png", b"", "image/png")},
                params={
                    "ward_id": ward_id,
                    "organic_pct": 10, "plastic_pct": 30, "paper_pct": 20,
                    "metal_pct": 15, "glass_pct": 15, "hazardous_pct": 10,
                },
                timeout=10)
        except:
            pass
    else:
        st.markdown(f"""
        <div style="background:#1a0800;border:1px solid #ef444440;border-radius:10px;
                    padding:1rem 1.2rem;font-size:0.85rem;color:#fca5a5;">
            ⚠ Segregation score too low ({score_pct}%) — no points awarded.
            Improve sorting accuracy to earn ward points.
        </div>
        """, unsafe_allow_html=True)

    # Processed video frames viewer
    if processed_frames:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("**Processed Video Frames**")
        frame_idx_slider = st.slider("Browse frames", 0, len(processed_frames)-1, 0)
        st.image(processed_frames[frame_idx_slider], use_container_width=True)