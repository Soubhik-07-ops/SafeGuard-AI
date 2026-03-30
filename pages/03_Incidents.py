import streamlit as st
import sys
import os

from utils.styles import inject_css, risk_pill

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.nlp_engine import analyze_report
from backend.supabase_client import log_incident, fetch_incidents

st.set_page_config(page_title="Incidents - SafeGuard AI", layout="wide", page_icon="SG")

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
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_inc", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_inc", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_inc", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_inc", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_inc", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_inc", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Incidents
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Incidents"] {
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
      <h1 style="font-size:28px;font-weight:700;color:#f0f2f8;margin:0;letter-spacing:-0.02em;">Incident Analyzer</h1>
      <p style="color:#8892a4;font-size:13px;margin:6px 0 0 0;">NLP-powered incident report analysis using SBERT.</p>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 16px 0 18px 0;"></div>
    """,
    unsafe_allow_html=True,
)


def render_keyword_chips(keywords):
    chips = ''.join([
        f"<span style='display:inline-block;background:#1a2035;color:#00c4f0;"
        f"border:1px solid #2a3560;border-radius:20px;padding:3px 10px;"
        f"font-size:12px;font-family:monospace;margin:3px;'>{kw}</span>"
        for kw in keywords
    ])
    return f"<div style='margin:8px 0;'>{chips}</div>"


# Tabs
tab_analyze, tab_history = st.tabs(["Analyze Report", "Incident History"])

with tab_analyze:

    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
              Incident Report
            </p>
            """,
            unsafe_allow_html=True,
        )

        sample = st.selectbox(
            "Load a sample report",
            [
                "-- Custom --",
                "Worker fell from scaffolding due to missing harness. No PPE was worn.",
                "Fire detected in Zone C machinery area. Sprinklers failed to activate.",
                "Unauthorized person entered restricted warehouse zone B without clearance.",
                "Chemical spill caused by improper storage. Worker inhaled fumes.",
            ],
        )

        default_text = "" if sample == "-- Custom --" else sample
        report_text = st.text_area(
            "Paste or type incident report here:",
            value=default_text,
            height=250,
            placeholder="Describe the incident in detail...",
        )

        severity = st.selectbox("Severity Level", ["HIGH", "MEDIUM", "LOW"])
        analyze_btn = st.button("Analyze Report", use_container_width=True)

    with col_output:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
              Analysis Results
            </p>
            """,
            unsafe_allow_html=True,
        )

        if analyze_btn:
            if not report_text.strip():
                st.warning("Please enter an incident report.")
            else:
                with st.spinner("Analyzing report with SBERT..."):
                    result = analyze_report(report_text)

                # Summary
                st.markdown(
                    """
                    <div style="background:#141925;border:1px solid #1a2035;border-left:4px solid #00c4f0;
                                border-radius:10px;padding:14px 16px;margin-bottom:10px;">
                      <div style="display:flex;align-items:center;gap:8px;color:#00c4f0;font-weight:700;">\U0001F4D8 Summary</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='color:#cbd5e1; font-size:13px;'>{result['summary']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                # Root cause
                cause = result["cause"]
                cause_cat = cause["cause_category"].replace("_", " ").title()
                st.markdown(
                    f"""
                    <div style="background:#141925;border:1px solid #1a2035;border-left:4px solid #f5a623;
                                border-radius:10px;padding:14px 16px;margin-bottom:10px;">
                      <div style="display:flex;align-items:center;gap:8px;color:#f5a623;font-weight:700;">\U0001F9ED Root Cause</div>
                      <div style="margin-top:6px;">
                        <span style="background:#f5a62318;color:#f5a623;border:1px solid #f5a62344;
                                     border-radius:20px;padding:2px 8px;font-size:11px;font-weight:600;">
                          {cause_cat}
                        </span>
                      </div>
                      <div style="color:#cbd5e1; font-size:13px; margin:10px 0 8px;">
                        <b>Cause:</b> {cause['cause_sentence']}
                      </div>
                      <div style="color:#8892a4; font-size:11px; margin-bottom:4px;">Keywords</div>
                      {render_keyword_chips(cause['keywords'])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Rule violations
                violations = result["violations"]
                st.markdown(
                    """
                    <div style="background:#141925;border:1px solid #1a2035;border-left:4px solid #f03b3b;
                                border-radius:10px;padding:14px 16px;margin-bottom:10px;">
                      <div style="color:#f03b3b;font-weight:700;margin-bottom:10px;">\u26A0\uFE0F Rule Violations</div>
                    """,
                    unsafe_allow_html=True,
                )

                if violations:
                    for v in violations:
                        score_pct = int(v["similarity_score"] * 100)
                        st.markdown(
                            f"""
                            <div style="margin-bottom:10px;">
                              <div style="color:#cbd5e1; font-size:13px; margin-bottom:4px;">
                                <b>[{v['rule_id']}]</b> {v['rule']}
                              </div>
                              <div style="background:#1a2035; border-radius:6px; height:8px; overflow:hidden;">
                                <div style="background:linear-gradient(90deg,#f5a623,#f03b3b); width:{score_pct}%; height:8px; border-radius:6px;"></div>
                              </div>
                              <div style="color:#8892a4; font-size:11px; margin-top:2px;">Match: {score_pct}%</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        "<div style='color:#8892a4; font-size:13px;'>No violations matched.</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                log_incident(report_text, severity, result)
                st.success("Incident saved to Supabase.")

with tab_history:

    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Incident History
        </p>
        """,
        unsafe_allow_html=True,
    )

    incidents = fetch_incidents(limit=20)

    if not incidents:
        st.info("No incidents logged yet.")
    else:
        for inc in incidents:
            sev = str(inc.get("severity", "UNKNOWN")).upper()
            ts = str(inc.get("timestamp", ""))[:19]
            text = inc.get("report_text", "")

            preview = text[:80] + "..." if len(text) > 80 else text

            with st.expander(f"{sev} ? {ts} ? {preview}"):
                st.markdown(
                    f"""
                    <div style="background:#141925;border:1px solid #1a2035;border-radius:10px;padding:14px 16px;">
                      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        {risk_pill(sev)}
                        <span style="color:#4a5568;font-size:11px;" class="mono">{ts}</span>
                      </div>
                      <div style="color:#cbd5e1; font-size:13px;">{text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

