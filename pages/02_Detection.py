import streamlit as st
import cv2
import numpy as np
import tempfile
import sys
import os

from utils.styles import inject_css

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.supabase_client import log_detection
from backend.risk_engine import predict_risk

st.set_page_config(
    page_title="Detection - SafeGuard AI",
    layout="wide",
    page_icon="SG",
)

inject_css()

# Sidebar
st.sidebar.markdown(
    """
    <!-- Logo -->
    <div style="padding:20px 16px 16px; border-bottom:1px solid #1a2035;">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#00c4f022,#00c4f044);
                    border:1px solid #00c4f066; border-radius:8px;
                    display:flex;align-items:center;justify-content:center;font-size:18px;">\U0001F6E1\uFE0F</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#f0f2f8;letter-spacing:-0.02em;">SafeGuard AI</div>
          <div style="font-size:10px;color:#4a5568;letter-spacing:0.05em;text-transform:uppercase;">
            Industrial Safety</div>
        </div>
      </div>
    </div>

    <!-- Nav items -->

    <!-- Footer -->
    <div style="margin-top:24px;
                padding:16px; border-top:1px solid #1a2035;">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:11px;color:#4a5568;">v1.0.0</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <div style="width:7px;height:7px;border-radius:50%;background:#00e5a0;
                      animation:live-blink 1.8s infinite;" class="live-dot"></div>
          <span style="font-size:11px;color:#00e5a0;font-weight:500;">Live</span>
        </div>
      </div>
      <div style="margin-top:8px;font-size:10px;color:#4a5568;letter-spacing:0.05em;text-transform:uppercase;">
        Industrial Safety Intelligence
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar nav (reliable routing)
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_det", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_det", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_det", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_det", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_det", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_det", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Detection
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Detection"] {
      background:#00c4f010 !important;
      box-shadow: inset 3px 0 0 #00c4f0 !important;
      color:#00c4f0 !important;
      font-weight:600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state
if "last_risk_label" not in st.session_state:
    st.session_state.last_risk_label = "CLEAR"
if "last_risk_conf" not in st.session_state:
    st.session_state.last_risk_conf = 0.0
if "total_detections" not in st.session_state:
    st.session_state.total_detections = 0
if "polygon_points" not in st.session_state:
    st.session_state.polygon_points = [(200, 100), (700, 100), (700, 400), (200, 400)]
if "polygon_set" not in st.session_state:
    st.session_state.polygon_set = False
if "last_log_text" not in st.session_state:
    st.session_state.last_log_text = "? Logged #0"

# Header
st.markdown(
    """
    <div style="padding:8px 0 10px;">
      <h1 style="font-size:28px;font-weight:700;color:#f0f2f8;margin:0;letter-spacing:-0.02em;">Live Detection</h1>
      <p style="color:#8892a4;font-size:13px;margin:6px 0 0 0;">Select a model and source. Risk is calculated and logged for every detection.</p>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 16px 0 18px 0;"></div>
    """,
    unsafe_allow_html=True,
)

# Sidebar settings
st.sidebar.markdown(
    """
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:12px 0 8px 0;">
      Detection Settings
    </p>
    """,
    unsafe_allow_html=True,
)

model_choice = st.sidebar.selectbox(
    "Detection Model",
    ["Fire & Smoke Detection", "PPE Detection", "Intrusion Detection", "Fall Detection"],
)

zone_choice = st.sidebar.selectbox(
    "Zone",
    ["Zone A - Entry", "Zone B - Warehouse", "Zone C - Machinery", "Zone D - Exit"],
)

conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 0.9, 0.5, 0.05)
log_every = st.sidebar.slider("Log to Supabase every N frames", 5, 60, 15)

if model_choice == "PPE Detection":
    input_source = st.sidebar.radio("Input Source", ["Upload Image", "Upload Video"])
else:
    input_source = st.sidebar.radio("Input Source", ["Webcam", "Upload Video", "Upload Image"])

run_btn = st.sidebar.button("Start Detection", use_container_width=True)

# Layout
col_feed, col_stats = st.columns([3, 1])

with col_feed:
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          \U0001F4E1 Detection Feed
        </p>
        """,
        unsafe_allow_html=True,
    )
    frame_window = st.image([])

with col_stats:
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Live Stats
        </p>
        """,
        unsafe_allow_html=True,
    )
    stats_panel = st.empty()


def get_risk_color(label):
    label = str(label).upper()
    return (
        "#f03b3b" if label in ["HIGH", "CRITICAL"]
        else "#f5a623" if label == "MEDIUM"
        else "#00e5a0"
    )


def render_stats_panel(rlabel, rconf, total_events, log_text, model, zone):
    color = get_risk_color(rlabel)
    pulse = "animation: pulse-glow 2s ease-in-out infinite; border: 2px solid #f03b3b;" if rlabel in ["HIGH", "CRITICAL"] else ""
    return f"""
    <div style="background: rgba(14,18,32,0.95); border: 1px solid rgba(255,255,255,0.06);
                backdrop-filter: blur(12px); border-radius: 12px; padding: 20px; {pulse}">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.1em; color:#4a5568;">Risk Level</div>
        <span style="background:#00e5a015;border:1px solid #00e5a044;
                     border-radius:20px;padding:2px 10px;font-size:11px;
                     color:#00e5a0;">{log_text}</span>
      </div>
      <div style="font-size:24px; color:{color}; font-weight:800; margin:10px 0 6px;">{rlabel}</div>
      <div style="color:#8892a4; font-size:12px;">{rconf*100:.1f}% confidence</div>

      <div style="height:1px; background:#1a2035; margin:14px 0;"></div>

      <div style="display:flex;align-items:center;gap:8px; color:#cbd5e1; font-size:12px; margin-bottom:8px;">
        <span style="font-size:14px;">\U0001F916</span>
        <span>{model}</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px; color:#cbd5e1; font-size:12px; margin-bottom:8px;">
        <span style="font-size:14px;">\U0001F4CD</span>
        <span>{zone}</span>
      </div>

      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:11px; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em;">Events</span>
        <span style="font-family:'JetBrains Mono', monospace; font-size:12px; color:#00c4f0;
                     background:#00c4f015;border:1px solid #00c4f044;border-radius:8px;padding:2px 8px;">
          {total_events}
        </span>
      </div>
    </div>
    """


stats_panel.markdown(
    render_stats_panel("--", 0.0, st.session_state.total_detections, st.session_state.last_log_text,
                       model_choice, zone_choice),
    unsafe_allow_html=True,
)

# File uploaders
video_file = None
image_file = None

if input_source == "Upload Video":
    video_file = st.file_uploader("Upload Video", type=["mp4", "avi"])
elif input_source == "Upload Image":
    image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# POLYGON ZONE SETUP (Intrusion only)
if model_choice == "Intrusion Detection":

    st.markdown(
        """
        <div style="background:#141925;border:1px solid #1a2035;border-left:4px solid #f5a623;
                    border-radius:10px;padding:14px 16px;">
          <div style="color:#f5a623; font-weight:700; margin-bottom:6px;">Intrusion Zone Setup</div>
          <div style="color:#8892a4; font-size:13px;">
            Draw a polygon zone. Only people whose feet land inside will trigger an alert.
            Frame size is 900 x 500.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:

        preset = st.selectbox(
            "Quick Zone Presets",
            [
                "Custom",
                "Full Frame",
                "Left Half",
                "Right Half",
                "Center Box",
                "Top Zone",
                "Bottom Zone",
                "Entry Door (top-left)",
                "Exit Door (bottom-right)",
            ],
        )

        preset_map = {
            "Full Frame": [(0, 0), (900, 0), (900, 500), (0, 500)],
            "Left Half": [(0, 0), (450, 0), (450, 500), (0, 500)],
            "Right Half": [(450, 0), (900, 0), (900, 500), (450, 500)],
            "Center Box": [(200, 100), (700, 100), (700, 400), (200, 400)],
            "Top Zone": [(0, 0), (900, 0), (900, 180), (0, 180)],
            "Bottom Zone": [(0, 320), (900, 320), (900, 500), (0, 500)],
            "Entry Door (top-left)": [(0, 0), (300, 0), (300, 250), (0, 250)],
            "Exit Door (bottom-right)": [(600, 250), (900, 250), (900, 500), (600, 500)],
        }

        if preset != "Custom" and preset in preset_map:
            st.session_state.polygon_points = preset_map[preset]

        st.markdown(
            "<div style='color:#8892a4; font-size:13px; margin:10px 0 4px 0;'>Or enter points manually:</div>",
            unsafe_allow_html=True,
        )

        num_pts = st.number_input("Number of polygon points", 3, 10, len(st.session_state.polygon_points))
        pts_input = []

        rows = [st.columns(4) for _ in range((int(num_pts) + 1) // 2)]

        for i in range(int(num_pts)):
            row = rows[i // 2]
            def_x = st.session_state.polygon_points[i][0] if i < len(st.session_state.polygon_points) else 0
            def_y = st.session_state.polygon_points[i][1] if i < len(st.session_state.polygon_points) else 0
            with row[(i % 2) * 2]:
                x = st.number_input(f"P{i+1} X", 0, 900, int(def_x), key=f"px_{i}")
            with row[(i % 2) * 2 + 1]:
                y = st.number_input(f"P{i+1} Y", 0, 500, int(def_y), key=f"py_{i}")
            pts_input.append((x, y))

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirm Zone", use_container_width=True):
                st.session_state.polygon_points = pts_input
                st.session_state.polygon_set = True
                st.success("Zone set.")
        with c2:
            if st.button("Reset Zone", use_container_width=True):
                st.session_state.polygon_points = [(200, 100), (700, 100), (700, 400), (200, 400)]
                st.session_state.polygon_set = False
                st.info("Zone reset to default.")

    with col_right:
        canvas = np.zeros((500, 900, 3), dtype=np.uint8)
        canvas[:] = (30, 33, 48)

        for x in range(0, 900, 100):
            cv2.line(canvas, (x, 0), (x, 500), (50, 55, 70), 1)
            cv2.putText(canvas, str(x), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 100), 1)
        for y in range(0, 500, 50):
            cv2.line(canvas, (0, y), (900, y), (50, 55, 70), 1)
            cv2.putText(canvas, str(y), (2, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (80, 80, 100), 1)

        if st.session_state.polygon_points:
            pts = np.array(st.session_state.polygon_points, np.int32)
            overlay = canvas.copy()
            cv2.fillPoly(overlay, [pts], (255, 170, 0))
            cv2.addWeighted(overlay, 0.25, canvas, 0.75, 0, canvas)
            cv2.polylines(canvas, [pts], True, (255, 170, 0), 2)
            for i, pt in enumerate(st.session_state.polygon_points):
                cv2.circle(canvas, pt, 7, (0, 212, 255), -1)
                cv2.putText(canvas, str(i + 1), (pt[0] + 8, pt[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        st.image(canvas, caption="Zone Preview (900 x 500)", channels="BGR", use_container_width=True)

        if st.session_state.polygon_set:
            st.success("Zone confirmed")
        else:
            st.warning("Zone not confirmed yet")

    st.markdown("<div style='height:1px;background:#1a2035;margin:24px 0;'></div>", unsafe_allow_html=True)

TYPE_MAP = {
    "Fire & Smoke Detection": "fire_smoke",
    "PPE Detection": "ppe_violation",
    "Intrusion Detection": "intrusion",
    "Fall Detection": "fall",
}


def update_risk_ui(rlabel, rconf):
    rlabel = str(rlabel).upper()
    st.session_state.last_risk_label = rlabel
    st.session_state.last_risk_conf = rconf
    st.session_state.total_detections += 1

    stats_panel.markdown(
        render_stats_panel(
            rlabel,
            rconf,
            st.session_state.total_detections,
            st.session_state.last_log_text,
            model_choice,
            zone_choice,
        ),
        unsafe_allow_html=True,
    )


def run_risk_and_log(detected, frame_count, detect_count):
    dets = [{
        "type": TYPE_MAP.get(model_choice, "fire_smoke"),
        "confidence": conf_threshold,
        "zone": zone_choice,
    }]
    risk = predict_risk(dets)
    rlabel = str(risk["risk"]).upper()
    rconf = risk["confidence"]
    update_risk_ui(rlabel, rconf)
    if frame_count % log_every == 0:
        log_detection(model_choice, "detected", conf_threshold, rlabel, rconf)
        st.session_state.last_log_text = f"? Logged #{detect_count}"
        stats_panel.markdown(
            render_stats_panel(
                rlabel,
                rconf,
                st.session_state.total_detections,
                st.session_state.last_log_text,
                model_choice,
                zone_choice,
            ),
            unsafe_allow_html=True,
        )
    return rlabel, rconf


def load_detector():
    if model_choice == "Fire & Smoke Detection":
        from models.fire_detector import FireDetector
        return FireDetector()
    elif model_choice == "PPE Detection":
        from models.ppe_detector import PPEDetector
        return PPEDetector()
    elif model_choice == "Intrusion Detection":
        from models.intrusion_detector import IntrusionDetector
        d = IntrusionDetector()
        pts = st.session_state.polygon_points
        from shapely.geometry import Polygon as ShapelyPolygon
        d.polygon_points = pts
        d.polygon = ShapelyPolygon(pts)
        d.min_confidence = conf_threshold
        return d
    elif model_choice == "Fall Detection":
        from models.fall_detector import FallDetector
        return FallDetector()


def get_video_source():
    if input_source == "Webcam":
        return cv2.VideoCapture(0)
    elif input_source == "Upload Video" and video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(video_file.read())
        return cv2.VideoCapture(tfile.name)
    return None

# MAIN DETECTION LOOP
if run_btn:

    if model_choice == "Intrusion Detection" and not st.session_state.polygon_set:
        st.warning("Please confirm the polygon zone first (click Confirm Zone).")
        st.stop()

    if input_source == "Upload Video" and not video_file:
        st.warning("Please upload a video file.")
        st.stop()
    elif input_source == "Upload Image" and not image_file:
        st.warning("Please upload an image file.")
        st.stop()

    detector = load_detector()

    # IMAGE MODE
    if input_source == "Upload Image" and image_file:
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        frame = cv2.resize(frame, (900, 500))

        frame, detected = detector.process_frame(frame)
        frame_window.image(frame, channels="BGR")

        run_risk_and_log(detected, 1, 1)

        if detected:
            st.error(f"{model_choice} - Threat detected.")
        else:
            st.success("No threats detected.")

    # VIDEO / WEBCAM MODE
    else:
        cap = get_video_source()
        if cap is None:
            st.error("Could not open video source.")
            st.stop()

        frame_count = 0
        detect_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (900, 500))
            frame_count += 1

            frame, detected = detector.process_frame(frame)

            if detected:
                detect_count += 1
                run_risk_and_log(detected, frame_count, detect_count)

            frame_window.image(frame, channels="BGR")

        cap.release()
        st.success(f"Detection completed. {detect_count} threat events detected.")

