GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

*:not(.material-icons):not(.material-symbols-outlined):not(.material-symbols-rounded) {
  font-family: 'Inter', -apple-system, 'Segoe UI', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif !important;
}
code, .mono { font-family: 'JetBrains Mono', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', monospace !important; }
.material-icons,
.material-symbols-outlined,
.material-symbols-rounded {
  font-family: 'Material Icons' !important;
  font-weight: normal !important;
  font-style: normal !important;
}

[data-testid="stAppViewContainer"] {
  background: radial-gradient(ellipse at 20% 0%, #0c1128 0%, #08090e 60%) !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0c0f1a 0%, #080b14 100%) !important;
  border-right: 1px solid #1a2035 !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"]     { background: transparent !important; box-shadow: none !important; }
#MainMenu, footer            { display: none !important; }

/* Sidebar toggle button icon */
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] i {
  font-family: 'Material Icons' !important;
  font-size: 20px !important;
}

/* Disable collapsible sidebar controls entirely */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
  display: none !important;
}
/* Final fix: hide glyph text everywhere and draw SVG arrows on the button itself */
[data-testid="stSidebarCollapseButton"] * {
  display: none !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] * {
  color: transparent !important;
  font-size: 0 !important;
  text-shadow: none !important;
}
[data-testid="stSidebarCollapseButton"] {
  position: relative !important;
}
[data-testid="stSidebarCollapseButton"]::after {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  width: 18px;
  height: 18px;
  background: no-repeat center/contain;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 18 18' fill='none' stroke='%23cbd5e1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M7 4l-4 5 4 5'/><path d='M15 4l-4 5 4 5'/></svg>");
}
/* Collapsed control lives in the header area: show >> */
[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"]::after {
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 18 18' fill='none' stroke='%23cbd5e1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M11 4l4 5-4 5'/><path d='M3 4l4 5-4 5'/></svg>");
}
/* Some Streamlit versions use a different wrapper when collapsed */
[data-testid="stSidebarCollapsedControl"] * {
  display: none !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"] * {
  color: transparent !important;
  font-size: 0 !important;
  text-shadow: none !important;
}
[data-testid="stSidebarCollapsedControl"] {
  position: relative !important;
}
[data-testid="stSidebarCollapsedControl"]::after {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  width: 18px;
  height: 18px;
  background: no-repeat center/contain;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 18 18' fill='none' stroke='%23cbd5e1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M11 4l4 5-4 5'/><path d='M3 4l4 5-4 5'/></svg>");
}

/* Scrollbar */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f1420; }
::-webkit-scrollbar-thumb { background: #2a3560; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a4570; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]   { background: transparent !important; gap: 4px; }
.stTabs [data-baseweb="tab"]        { background: #141925 !important; color: #8892a4 !important;
                                       border-radius: 8px 8px 0 0 !important;
                                       border: 1px solid #1a2035 !important; }
.stTabs [aria-selected="true"]      { background: #1a2540 !important; color: #00c4f0 !important;
                                       border-bottom-color: #1a2540 !important; }

/* Selectbox */
.stSelectbox > div > div { background: #141925 !important; border-color: #1a2035 !important;
                            color: #f0f2f8 !important; border-radius: 8px !important; }

/* Slider */
.stSlider [data-baseweb="slider"] div { background: #00c4f0 !important; }

/* Buttons */
.stButton > button { background: #00c4f015 !important; border: 1px solid #00c4f044 !important;
                      color: #00c4f0 !important; border-radius: 8px !important;
                      font-weight: 500 !important; transition: all 200ms ease !important; }
.stButton > button:hover { background: #00c4f025 !important;
                            box-shadow: 0 0 12px rgba(0,196,240,0.15) !important; }
.stDownloadButton > button { background: #00c4f015 !important; border: 1px solid #00c4f044 !important;
                             color: #00c4f0 !important; border-radius: 8px !important;
                             font-weight: 500 !important; transition: all 200ms ease !important; }
.stDownloadButton > button:hover { background: #00c4f025 !important;
                                   box-shadow: 0 0 12px rgba(0,196,240,0.15) !important; }

/* Sidebar nav hover */
section[data-testid="stSidebar"] div[style*="cursor:pointer"]:hover {
  background: #00c4f010 !important;
}

/* Home nav cards */
.nav-card { transition: all 200ms ease; }
.nav-card:hover {
  transform: translateY(-4px);
  border-color: var(--glow, #2a3560) !important;
  box-shadow: 0 8px 24px var(--glow-shadow, rgba(0,196,240,0.18));
}

/* Sidebar links */
.sg-nav {
  display:flex;
  align-items:center;
  gap:10px;
  margin:4px 8px 0;
  padding:10px 12px;
  border-radius:8px;
  border-left:3px solid transparent;
  text-decoration:none !important;
  transition: all 200ms ease;
}
.sg-nav span { text-decoration:none !important; }
.sg-nav:hover { background:#00c4f010; }
.sg-nav.active {
  background:#00c4f010;
  border-left-color:#00c4f0;
}
.sg-nav.active .sg-nav-label { color:#00c4f0 !important; font-weight:600; }
.sg-nav .sg-nav-label { color:#8892a4 !important; font-size:13px; font-weight:400; }

/* Sidebar nav buttons (switch_page) */
[data-testid="stSidebar"] .stButton > button {
  width: 100% !important;
  text-align: left !important;
  justify-content: flex-start !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  color: #8892a4 !important;
  padding: 10px 12px !important;
  border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #00c4f010 !important;
  box-shadow: inset 3px 0 0 #00c4f0 !important;
  color: #00c4f0 !important;
}

/* Metric card hover */
.metric-card { transition: all 200ms ease; }
.metric-card:hover {
  transform: translateY(-2px);
  border-color: var(--glow, #2a3560) !important;
  box-shadow: 0 8px 20px var(--glow-shadow, rgba(0,196,240,0.18));
}

/* File uploader */
[data-testid="stFileUploadDropzone"] { background: #141925 !important;
                                        border: 1px dashed #2a3560 !important;
                                        border-radius: 10px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }

/* Number input */
.stNumberInput input { background: #141925 !important; border: 1px solid #1a2035 !important;
                        color: #f0f2f8 !important; border-radius: 6px !important; }

/* Radio */
.stRadio label { color: #8892a4 !important; }

/* Expander */
.streamlit-expanderHeader { background: #141925 !important; border: 1px solid #1a2035 !important;
                              border-radius: 8px !important; color: #f0f2f8 !important; }
/* Remove material icon text in expander headers */
[data-testid="stExpander"] .material-icons,
[data-testid="stExpander"] .material-symbols-outlined,
[data-testid="stExpander"] .material-symbols-rounded {
  display: none !important;
}

/* Metric */
[data-testid="metric-container"] { background: #141925 !important;
                                     border: 1px solid #1a2035 !important;
                                     border-radius: 10px !important; }
[data-testid="stMetricValue"]    { color: #f0f2f8 !important; }
[data-testid="stMetricLabel"]    { color: #8892a4 !important; }

/* Textarea (Incidents) */
.stTextArea textarea {
  background: #141925 !important;
  border: 1px solid #1a2035 !important;
  color: #f0f2f8 !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
}
.stTextArea textarea:focus {
  border-color: #00c4f0 !important;
  box-shadow: 0 0 0 2px rgba(0,196,240,0.1) !important;
}

/* Animations */
@keyframes pulse-glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(240,59,59,0.3); }
  50%      { box-shadow: 0 0 24px 4px rgba(240,59,59,0.12); }
}
@keyframes live-blink {
  0%,100% { opacity: 1; } 50% { opacity: 0.15; }
}
@keyframes fade-up {
  from { opacity:0; transform:translateY(10px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes dot-bounce {
  0%,80%,100% { transform:scale(0.6); opacity:0.3; }
  40%          { transform:scale(1);   opacity:1; }
}
.high-risk-pulse { animation: pulse-glow 2s ease-in-out infinite; }
.live-dot        { animation: live-blink 1.8s ease-in-out infinite; }
.fade-up         { animation: fade-up 0.35s ease forwards; }
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

PLOTLY_BASE = dict(
    paper_bgcolor="#08090e",
    plot_bgcolor="#0f1420",
    font=dict(family="Inter", color="#8892a4", size=12),
    margin=dict(t=30, b=40, l=50, r=20),
    xaxis=dict(gridcolor="#1a2035", linecolor="#1a2035",
               tickcolor="#4a5568", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#1a2035", linecolor="#1a2035",
               tickcolor="#4a5568", tickfont=dict(size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4", size=11)),
)

MODEL_COLORS = {
    "Fire & Smoke Detection": "#f03b3b",
    "Intrusion Detection":    "#f5a623",
    "Fall Detection":         "#7c5cfc",
    "PPE Detection":          "#00c4f0",
    "Fire Detection":         "#f03b3b",
}

RISK_COLORS = {
    "HIGH": "#f03b3b", "CRITICAL": "#cc1f1f",
    "MEDIUM": "#f5a623", "medium": "#f5a623",
    "LOW": "#00e5a0", "low": "#00e5a0", "high": "#ff6b6b",
}

def risk_pill(level: str) -> str:
    colors = {
        "HIGH":     ("#f03b3b", "#f03b3b18", "#f03b3b44"),
        "CRITICAL": ("#cc1f1f", "#cc1f1f18", "#cc1f1f44"),
        "MEDIUM":   ("#f5a623", "#f5a62318", "#f5a62344"),
        "medium":   ("#f5a623", "#f5a62318", "#f5a62344"),
        "LOW":      ("#00e5a0", "#00e5a018", "#00e5a044"),
        "low":      ("#00e5a0", "#00e5a018", "#00e5a044"),
        "high":     ("#ff6b6b", "#ff6b6b18", "#ff6b6b44"),
    }
    c, bg, br = colors.get(level, ("#8892a4", "#8892a418", "#8892a444"))
    return (f"<span style='background:{bg};color:{c};border:1px solid {br};"
            f"border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;"
            f"text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;'>"
            f"{level.upper()}</span>")
