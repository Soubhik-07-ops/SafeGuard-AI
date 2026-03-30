import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

from utils.styles import inject_css, risk_pill

# Path setup
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.supabase_client import fetch_recent_detections, fetch_incidents

st.set_page_config(
    page_title="SafeGuard AI",
    page_icon="SG",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Sidebar (custom)
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
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_app", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_app", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_app", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_app", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_app", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_app", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Home
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Home"] {
      background:#00c4f010 !important;
      box-shadow: inset 3px 0 0 #00c4f0 !important;
      color:#00c4f0 !important;
      font-weight:600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Data
recent = fetch_recent_detections(limit=200)
incidents = fetch_incidents(limit=50)

_df = pd.DataFrame(recent) if recent else pd.DataFrame()
_dfi = pd.DataFrame(incidents) if incidents else pd.DataFrame()

# Metrics
_total = len(_df)
_high = len(_df[_df.get("risk_level", "").eq("HIGH")]) if not _df.empty else 0
_models = _df["model_type"].nunique() if not _df.empty and "model_type" in _df.columns else 0

_inc_today = 0
if not _dfi.empty and "timestamp" in _dfi.columns:
    _dfi["timestamp"] = pd.to_datetime(_dfi["timestamp"], errors="coerce")
    _inc_today = int((_dfi["timestamp"].dt.date == datetime.now().date()).sum())

# Hero
st.markdown(
    """
    <div style="padding:40px 0 32px;">
      <div style="display:inline-flex;align-items:center;gap:8px;
                  background:#00e5a015;border:1px solid #00e5a033;
                  border-radius:20px;padding:4px 12px;margin-bottom:16px;">
        <div style="width:6px;height:6px;border-radius:50%;background:#00e5a0;
                    animation:live-blink 1.8s infinite;"></div>
        <span style="font-size:11px;color:#00e5a0;font-weight:500;
                     letter-spacing:0.05em;text-transform:uppercase;">
          System Online</span>
      </div>
      <h1 style="font-size:48px;font-weight:800;color:#f0f2f8;
                 letter-spacing:-0.04em;margin:0;line-height:1.1;">
        SafeGuard <span style="color:#00c4f0;">AI</span>
      </h1>
      <p style="font-size:18px;color:#8892a4;margin:10px 0 0;font-weight:300;">
        Industrial Safety Intelligence for real-time detection, risk, and response.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# System health row
h1, h2, h3, h4 = st.columns(4)
health_items = [
    ("\U0001F7E2", "Video Feeds", "24/24 Online"),
    ("\U0001F7E2", "Risk Engine", "Stable"),
    ("\U0001F7E2", "NLP Copilot", "Online"),
    ("\U0001F7E2", "Alert Bus", "Realtime"),
]
for col, (icon, label, value) in zip([h1, h2, h3, h4], health_items):
    col.markdown(
        f"""
        <div style="background:#0f1420;border:1px solid #1a2035;border-radius:10px;
                    padding:12px 14px;">
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#4a5568;">
            {label}
          </div>
          <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
            <span style="font-size:14px;">{icon}</span>
            <span style="color:#f0f2f8;font-size:13px;font-weight:600;">{value}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0;"></div>
    """,
    unsafe_allow_html=True,
)

# Live stats row
st.markdown(
    """
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Live Stats
    </p>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("\U0001F50D", "Total Detections", _total, "#00c4f0", "\u2191 3 from yesterday"),
    ("\U0001F534", "HIGH Risk Events", _high, "#f03b3b", "\u2191 1 from yesterday"),
    ("\U0001F4C4", "Incidents Today", _inc_today, "#f5a623", "\u2192 steady"),
    ("\U0001F916", "Models Active", _models, "#7c5cfc", "\u2191 1 from last week"),
]

for col, (icon, label, value, color, delta) in zip([c1, c2, c3, c4], cards):
    col.markdown(
        f"""
        <div class="metric-card" style="--glow:{color}; --glow-shadow:{color}33;
                    background:#141925;border:1px solid #1a2035;border-radius:10px;
                    padding:20px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:50%;
                        background:{color}22;border:1px solid {color}55;
                        display:flex;align-items:center;justify-content:center;">{icon}</div>
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#4a5568;">
              {label}
            </div>
          </div>
          <div style="font-size:32px;font-weight:800;color:{color};margin:8px 0 4px;">{value}</div>
          <div style="font-size:12px;color:#8892a4;">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Nav cards
st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0;"></div>
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Navigation
    </p>
    """,
    unsafe_allow_html=True,
)

n1, n2, n3, n4 = st.columns(4)
nav_cards = [
    ("\U0001F4CA", "Dashboard", "Risk gauge, alert stream, and recent detections.", "#00c4f0"),
    ("\U0001F4F7", "Detection", "Live video inference and zone-based monitoring.", "#00e5a0"),
    ("\U0001F4C4", "Incidents", "NLP incident analysis and root cause insights.", "#f5a623"),
    ("\U0001F4C8", "Analytics", "Trends, distribution, and export-ready logs.", "#f03b3b"),
]

for col, (icon, title, desc, color) in zip([n1, n2, n3, n4], nav_cards):
    glow_shadow = "rgba(0,196,240,0.18)" if color == "#00c4f0" else \
                  "rgba(0,229,160,0.18)" if color == "#00e5a0" else \
                  "rgba(245,166,35,0.18)" if color == "#f5a623" else \
                  "rgba(240,59,59,0.18)"
    col.markdown(
        f"""
        <div class="nav-card" style="--glow:{color}; --glow-shadow:{glow_shadow};
                    min-height:180px; background:#0f1420; border:1px solid #1a2035;
                    border-radius:12px; padding:18px; text-align:center;">
          <div style="font-size:40px;margin-bottom:8px;">{icon}</div>
          <div style="font-size:15px;font-weight:700;color:{color};">{title}</div>
          <div style="font-size:12px;color:#8892a4;margin-top:6px;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Recent activity
st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0;"></div>
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Recent Activity
    </p>
    """,
    unsafe_allow_html=True,
)

if _df.empty:
    st.info("No detections logged yet.")
else:
    recent_rows = _df.head(5)
    for _, row in recent_rows.iterrows():
        ts = str(row.get("timestamp", ""))[:19]
        model = row.get("model_type", "?")
        conf = float(row.get("confidence", 0))
        risk = str(row.get("risk_level", "UNKNOWN"))
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;
                        border-radius:8px;background:#0f1420;border:1px solid #1a2035;
                        margin-bottom:8px;">
              {risk_pill(risk)}
              <div style="color:#f0f2f8;font-size:13px;flex:1;">{model}</div>
              <div style="color:#8892a4;font-size:12px;" class="mono">{conf:.0%}</div>
              <div style="color:#4a5568;font-size:11px;" class="mono">{ts}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

