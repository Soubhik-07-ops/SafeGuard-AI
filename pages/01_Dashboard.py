import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
from datetime import datetime

from utils.styles import inject_css, PLOTLY_BASE, MODEL_COLORS, risk_pill

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.supabase_client import fetch_recent_detections, fetch_incidents

st.set_page_config(page_title="Dashboard - SafeGuard AI", layout="wide", page_icon="SG")

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
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_dash", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_dash", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_dash", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_dash", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_dash", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_dash", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Dashboard
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Dashboard"] {
      background:#00c4f010 !important;
      box-shadow: inset 3px 0 0 #00c4f0 !important;
      color:#00c4f0 !important;
      font-weight:600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="dash_refresh")
except ImportError:
    pass

# Header
st.markdown(
    """
    <div style="padding:8px 0 10px;">
      <h1 style="font-size:28px;font-weight:700;color:#f0f2f8;margin:0;letter-spacing:-0.02em;">Live Dashboard</h1>
      <p style="color:#8892a4;font-size:13px;margin:6px 0 0 0;">Real-time safety monitoring with 5s auto-refresh.</p>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 16px 0 18px 0;"></div>
    """,
    unsafe_allow_html=True,
)

# Fetch data
raw = fetch_recent_detections(limit=80)
df = pd.DataFrame(raw) if raw else pd.DataFrame()

# Risk calculation
if not df.empty and "risk_score" in df.columns:
    latest = df.iloc[0]
    risk_score = float(latest.get("risk_score", 0)) * 100
    risk_label = str(latest.get("risk_level", "LOW")).upper()
else:
    risk_score = 0.0
    risk_label = "LOW"

risk_color = (
    "#f03b3b" if risk_label in ["HIGH", "CRITICAL"]
    else "#f5a623" if risk_label == "MEDIUM"
    else "#00e5a0"
)

# Stat cards
st.markdown(
    """
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Live Metrics
    </p>
    """,
    unsafe_allow_html=True,
)

_total = len(df)
_high = len(df[df.get("risk_level", "").eq("HIGH")]) if not df.empty else 0
_med = len(df[df.get("risk_level", "").eq("MEDIUM")]) if not df.empty else 0
_models = df["model_type"].nunique() if not df.empty and "model_type" in df.columns else 0

cards = [
    ("\U0001F6E0\uFE0F", "Total Detections", _total, "#00c4f0", "\u2191 3 from yesterday"),
    ("\U0001F6A8", "High Risk Events", _high, "#f03b3b", "\u2191 1 from yesterday"),
    ("\u26A0\uFE0F", "Medium Risk Events", _med, "#f5a623", "\u2192 steady"),
    ("\U0001F916", "Active Models", _models, "#7c5cfc", "\u2191 1 from last week"),
]

c1, c2, c3, c4 = st.columns(4)
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
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#4a5568;">{label}</div>
          </div>
          <div style="font-size:32px;font-weight:800;color:{color};margin:8px 0 4px;">{value}</div>
          <div style="font-size:12px;color:#8892a4;">{delta}</div>
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

# Risk Gauge + Bar chart
col_gauge, col_bar = st.columns([1, 2])

with col_gauge:
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Current Risk
        </p>
        """,
        unsafe_allow_html=True,
    )

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(risk_score, 1),
            number={"suffix": "%", "font": {"size": 28, "color": risk_color}},
            title={"text": risk_label, "font": {"color": risk_color, "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#4a5568"},
                "bar": {"color": risk_color, "thickness": 0.25},
                "bgcolor": "#0a0d14",
                "steps": [
                    {"range": [0, 30], "color": "#0f1f1a"},
                    {"range": [30, 70], "color": "#221f14"},
                    {"range": [70, 100], "color": "#241417"},
                ],
                "threshold": {
                    "line": {"color": "#f03b3b", "width": 3},
                    "thickness": 0.8,
                    "value": 70,
                },
            },
        )
    )
    fig_gauge.update_layout(height=280, **PLOTLY_BASE)

    glow = (
        "box-shadow: 0 0 30px rgba(240,59,59,0.25);" if risk_label in ["HIGH", "CRITICAL"]
        else "box-shadow: 0 0 30px rgba(245,166,35,0.25);" if risk_label == "MEDIUM"
        else "box-shadow: 0 0 30px rgba(0,229,160,0.25);"
    )
    pulse_class = "high-risk-pulse" if risk_label in ["HIGH", "CRITICAL"] else ""

    st.markdown(
        f"""
        <div class="{pulse_class}" style="background:#141925;border:1px solid #1a2035;border-radius:12px;
                    padding:8px;{glow}">
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#4a5568;font-size:11px;margin-top:6px;'>Last updated 5s ago</div>",
        unsafe_allow_html=True,
    )

with col_bar:
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Detections by Model
        </p>
        """,
        unsafe_allow_html=True,
    )
    if not df.empty and "model_type" in df.columns:
        model_counts = df["model_type"].value_counts().reset_index()
        model_counts.columns = ["Model", "Count"]
        fig_bar = px.bar(
            model_counts,
            x="Model",
            y="Count",
            color="Model",
            color_discrete_map=MODEL_COLORS,
        )
        fig_bar.update_layout(height=280, showlegend=False, **PLOTLY_BASE)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No detection data yet.")

# Recent detections table
st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0 16px 0;"></div>
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Recent Detections
    </p>
    """,
    unsafe_allow_html=True,
)

if not df.empty:
    rows = []
    for _, row in df.head(20).iterrows():
        ts = str(row.get("timestamp", ""))[:19]
        model = row.get("model_type", "?")
        label = row.get("label", "-")
        conf = float(row.get("confidence", 0))
        risk = str(row.get("risk_level", "UNKNOWN"))
        rows.append(
            f"""
            <tr>
              <td style="padding:10px 12px; font-family:'JetBrains Mono', monospace; color:#8892a4;">{ts}</td>
              <td style="padding:10px 12px; color:#f0f2f8;">{model}</td>
              <td style="padding:10px 12px; color:#8892a4;">{label}</td>
              <td style="padding:10px 12px; color:#00c4f0; font-family:'JetBrains Mono', monospace;">{conf:.0%}</td>
              <td style="padding:10px 12px;">{risk_pill(risk)}</td>
            </tr>
            """
        )

    table_html = f"""
    <div style="background:#0f1420;border:1px solid #1a2035;border-radius:10px;overflow:hidden;">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead style="background:#141925; text-transform:uppercase; letter-spacing:0.08em; font-size:11px; color:#4a5568;">
          <tr>
            <th style="text-align:left;padding:10px 12px;">Timestamp</th>
            <th style="text-align:left;padding:10px 12px;">Model</th>
            <th style="text-align:left;padding:10px 12px;">Label</th>
            <th style="text-align:left;padding:10px 12px;">Conf</th>
            <th style="text-align:left;padding:10px 12px;">Risk</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """
    components.html(table_html, height=520, scrolling=True)
else:
    st.info("No detections logged yet. Run a detection first.")

# Recent incidents
st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0 16px 0;"></div>
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Recent Incidents
    </p>
    """,
    unsafe_allow_html=True,
)

incidents = fetch_incidents(limit=5)
if incidents:
    for inc in incidents:
        sev = str(inc.get("severity", "UNKNOWN")).upper()
        color = "#f03b3b" if sev == "HIGH" else "#f5a623" if sev == "MEDIUM" else "#00e5a0"
        ts = str(inc.get("timestamp", ""))[:19]
        text = inc.get("report_text", "")[:200]
        st.markdown(
            f"""
            <div style="background:#141925;border:1px solid #1a2035;border-left:4px solid {color};
                        border-radius:10px;padding:14px 16px;margin-bottom:10px;">
              <div style="display:flex;align-items:center;gap:10px;">
                {risk_pill(sev)}
                <span style="color:#4a5568;font-size:11px;" class="mono">{ts}</span>
              </div>
              <div style="color:#cbd5e1;font-size:13px;margin-top:8px;">{text}...</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No incidents logged yet.")

