import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

from utils.styles import inject_css, PLOTLY_BASE, MODEL_COLORS, RISK_COLORS

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.supabase_client import fetch_recent_detections, fetch_incidents

st.set_page_config(page_title="Analytics - SafeGuard AI", layout="wide", page_icon="SG")

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
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_an", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_an", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_an", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_an", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_an", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_an", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Analytics
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Analytics"] {
      background:#00c4f010 !important;
      box-shadow: inset 3px 0 0 #00c4f0 !important;
      color:#00c4f0 !important;
      font-weight:600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div style="padding:8px 0 10px;">
      <h1 style="font-size:28px;font-weight:700;color:#f0f2f8;margin:0;letter-spacing:-0.02em;">Analytics</h1>
      <p style="color:#8892a4;font-size:13px;margin:6px 0 0 0;">Detection trends, risk distribution, and incident history.</p>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 16px 0 18px 0;"></div>
    """,
    unsafe_allow_html=True,
)

# Fetch data
raw = fetch_recent_detections(limit=200)
incidents = fetch_incidents(limit=50)

_df = pd.DataFrame(raw) if raw else pd.DataFrame()
_dfi = pd.DataFrame(incidents) if incidents else pd.DataFrame()

# Top stats
st.markdown(
    """
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Summary
    </p>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

stats = [
    ("Total Detections", len(_df), "#00c4f0"),
    ("Total Incidents", len(_dfi), "#f5a623"),
    ("High Risk Events", len(_df[_df.get("risk_level", "").eq("HIGH")]) if not _df.empty else 0, "#f03b3b"),
    ("Avg Risk Score", f"{_df['risk_score'].mean()*100:.1f}%" if not _df.empty and "risk_score" in _df.columns else "N/A", "#7c5cfc"),
]

for col, (label, value, color) in zip([c1, c2, c3, c4], stats):
    col.markdown(
        f"""
        <div class="metric-card" style="--glow:{color}; --glow-shadow:{color}33;
                    background:#141925;border:1px solid #1a2035;border-radius:10px;padding:18px;">
          <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#4a5568;">{label}</div>
          <div style="font-size:28px;font-weight:800;color:{color};margin-top:6px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0 16px 0;"></div>
    """,
    unsafe_allow_html=True,
)

# Charts
if not _df.empty:

    if "timestamp" in _df.columns:
        _df["timestamp"] = pd.to_datetime(_df["timestamp"], errors="coerce")
        _df = _df.dropna(subset=["timestamp"])
        _df["date"] = _df["timestamp"].dt.date
        _df["hour"] = _df["timestamp"].dt.hour

    col1, col2 = st.columns(2)

    # Risk distribution pie
    with col1:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
              Risk Distribution
            </p>
            """,
            unsafe_allow_html=True,
        )
        if "risk_level" in _df.columns:
            risk_counts = _df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            fig_pie = px.pie(
                risk_counts,
                names="Risk Level",
                values="Count",
                color="Risk Level",
                color_discrete_map=RISK_COLORS,
                hole=0.4,
            )
            fig_pie.update_layout(height=300, **PLOTLY_BASE)
            st.markdown("<div style='background:#141925;border:1px solid #1a2035;border-radius:10px;padding:6px;'>", unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No risk level data.")

    # Detections by model bar
    with col2:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
              Detections by Model
            </p>
            """,
            unsafe_allow_html=True,
        )
        if "model_type" in _df.columns:
            model_counts = _df["model_type"].value_counts().reset_index()
            model_counts.columns = ["Model", "Count"]
            fig_bar = px.bar(
                model_counts,
                x="Model",
                y="Count",
                color="Model",
                color_discrete_map=MODEL_COLORS,
            )
            fig_bar.update_layout(height=300, showlegend=False, **PLOTLY_BASE)
            st.markdown("<div style='background:#141925;border:1px solid #1a2035;border-radius:10px;padding:6px;'>", unsafe_allow_html=True)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No model data.")

    # Timeline
    st.markdown(
        """
        <div style="height:1px; background:linear-gradient(90deg,
          transparent, #1a2035 20%, #1a2035 80%, transparent);
          margin: 24px 0 16px 0;"></div>
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Detection Timeline
        </p>
        """,
        unsafe_allow_html=True,
    )
    if "date" in _df.columns:
        timeline = (
            _df.groupby(["date", "risk_level"]).size().reset_index(name="Count")
            if "risk_level" in _df.columns
            else _df.groupby("date").size().reset_index(name="Count")
        )

        if "risk_level" in timeline.columns:
            fig_line = px.line(
                timeline,
                x="date",
                y="Count",
                color="risk_level",
                color_discrete_map=RISK_COLORS,
                markers=True,
            )
        else:
            fig_line = px.line(timeline, x="date", y="Count", markers=True)

        fig_line.update_traces(marker=dict(size=8, line=dict(width=1, color="#0f1420")))
        fig_line.update_layout(height=300, **PLOTLY_BASE)
        st.markdown("<div style='background:#141925;border:1px solid #1a2035;border-radius:10px;padding:6px;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Hourly heatmap
    if "hour" in _df.columns and "model_type" in _df.columns:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:16px 0 12px 0;">
              Hourly Activity
            </p>
            """,
            unsafe_allow_html=True,
        )
        hourly = _df.groupby(["hour", "model_type"]).size().reset_index(name="Count")
        fig_heat = px.density_heatmap(
            hourly,
            x="hour",
            y="model_type",
            z="Count",
            color_continuous_scale=["#141925", "#f03b3b"],
        )
        fig_heat.update_layout(height=280, **PLOTLY_BASE)
        st.markdown("<div style='background:#141925;border:1px solid #1a2035;border-radius:10px;padding:6px;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No detection data available yet. Run some detections first.")

# Full data table + export
st.markdown(
    """
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 24px 0 16px 0;"></div>
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
      Full Detection Log
    </p>
    """,
    unsafe_allow_html=True,
)

col_table, col_btn = st.columns([4, 1])

with col_table:
    if not _df.empty:
        show_cols = [c for c in ["timestamp", "model_type", "label", "confidence", "risk_level", "risk_score"] if c in _df.columns]
        st.dataframe(_df[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No data yet.")

with col_btn:
    if not _df.empty:
        csv = _df.to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv,
            file_name="safeguard_detections.csv",
            mime="text/csv",
            use_container_width=True,
        )

# Incidents table
st.markdown(
    """
    <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
               text-transform:uppercase; color:#4a5568; margin:16px 0 12px 0;">
      Incident Log
    </p>
    """,
    unsafe_allow_html=True,
)
if not _dfi.empty:
    show_inc = [c for c in ["timestamp", "severity", "report_text"] if c in _dfi.columns]
    st.dataframe(_dfi[show_inc], use_container_width=True, hide_index=True)

    csv_inc = _dfi.to_csv(index=False)
    st.download_button(
        label="Export Incidents CSV",
        data=csv_inc,
        file_name="safeguard_incidents.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.info("No incidents logged yet.")

