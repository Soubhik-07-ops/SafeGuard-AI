import streamlit as st
import requests
import json
import re
import sys
import os
from datetime import datetime
from collections import Counter

from utils.styles import inject_css, MODEL_COLORS, RISK_COLORS

# Path setup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.supabase_client import fetch_recent_detections, fetch_incidents

st.set_page_config(
    page_title="AI Copilot ? SafeGuard AI",
    layout="wide",
    page_icon="\U0001F916"
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
                    display:flex;align-items:center;justify-content:center;font-size:18px;">\U0001F6E1</div>
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
if st.sidebar.button("\U0001F6E1\uFE0F  Home", key="nav_home_cp", use_container_width=True):
    st.switch_page("app.py")
if st.sidebar.button("\U0001F4CA  Dashboard", key="nav_dash_cp", use_container_width=True):
    st.switch_page("pages/01_Dashboard.py")
if st.sidebar.button("\U0001F4F7  Detection", key="nav_det_cp", use_container_width=True):
    st.switch_page("pages/02_Detection.py")
if st.sidebar.button("\U0001F4C4  Incidents", key="nav_inc_cp", use_container_width=True):
    st.switch_page("pages/03_Incidents.py")
if st.sidebar.button("\U0001F4C8  Analytics", key="nav_an_cp", use_container_width=True):
    st.switch_page("pages/04_Analytics.py")
if st.sidebar.button("\U0001F916  Copilot", key="nav_cp_cp", use_container_width=True):
    st.switch_page("pages/05_Copilot.py")

# Active highlight for Copilot
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button[aria-label*="Copilot"] {
      background:#00c4f010 !important;
      box-shadow: inset 3px 0 0 #00c4f0 !important;
      color:#00c4f0 !important;
      font-weight:600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Page-specific CSS
st.markdown(
    """
    <style>
      .chat-row { display:flex; margin:8px 0; }
      .chat-row.user { justify-content:flex-end; }
      .chat-row.ai { justify-content:flex-start; }
      .chat-bubble-user {
        max-width:75%; background:#0d1e2e; border:1px solid #00c4f033;
        border-radius:16px 16px 4px 16px; padding:12px 16px;
        color:#f0f2f8; font-size:14px; line-height:1.6;
      }
      .chat-bubble-ai {
        max-width:80%; background:#141925; border:1px solid #1a2035;
        border-left:3px solid #7c5cfc; border-radius:0 12px 12px 12px;
        padding:14px 16px; color:#e0e8f0; font-size:14px; line-height:1.8;
        box-shadow:0 2px 12px rgba(0,0,0,0.3);
      }
      .avatar {
        width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;
        font-size:14px;flex-shrink:0;border:1px solid transparent;
      }
      .avatar.user { background:#00c4f020; border:1px solid #00c4f044; margin-left:8px; }
      .avatar.ai { background:#7c5cfc20; border:1px solid #7c5cfc44; margin-right:8px; margin-top:4px; }

      .quick-chips { display:flex; flex-wrap:wrap; gap:6px; }
      .quick-chips .stButton { display:inline-block; }
      .quick-chips .stButton > button {
        width:auto !important; padding:6px 14px !important; font-size:12px !important;
        border-radius:20px !important; margin:0 !important;
        background:#1a2035 !important; color:#00c4f0 !important; border:1px solid #2a3560 !important;
      }

      .context-card {
        background:#141925; border:1px solid #1a2035; border-radius:10px; padding:12px;
        margin-bottom:10px; font-size:12px; color:#8892a4;
      }
      .context-metric { font-size:22px; font-weight:800; color:#f0f2f8; }
      .model-bar { height:6px; border-radius:6px; background:#1a2035; overflow:hidden; }
      .model-bar > div { height:6px; border-radius:6px; }

      .send-button .stButton > button {
        background:#00c4f0 !important; color:#0a0d14 !important; border:1px solid #00c4f0 !important;
        border-radius:10px !important; font-weight:700 !important; height:40px;
      }
      .stTextInput input {
        background:#141925 !important; color:#f0f2f8 !important; border:1px solid #1a2035 !important;
        border-radius:10px !important; height:40px !important;
      }

      .thinking-dots { display:flex; align-items:center; gap:4px; padding:12px 0; }
      .thinking-dots div {
        width:8px;height:8px;border-radius:50%;background:#7c5cfc;
        animation:dot-bounce 1.4s ease-in-out infinite;
      }
      .thinking-dots div:nth-child(2) { animation-delay:0.2s; }
      .thinking-dots div:nth-child(3) { animation-delay:0.4s; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Config
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL_ID = "z-ai/glm-4.5-air:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fetch live data
detections = fetch_recent_detections(limit=50)
incidents = fetch_incidents(limit=10)


def build_analytics(detections, incidents):
    if not detections:
        return {"total": 0, "risk_counts": {}, "model_counts": {},
                "high_events": [], "avg_conf": 0, "time_range": "",
                "inc_sev": {}, "total_inc": len(incidents),
                "top_model": ("None", 0)}
    risk_counts = Counter(d.get("risk_level", "UNKNOWN") for d in detections)
    model_counts = Counter(d.get("model_type", "?") for d in detections)
    high_events = [d for d in detections if d.get("risk_level") == "HIGH"]
    timestamps = []
    for d in detections:
        ts = d.get("timestamp", "")
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(str(ts)[:19]))
            except Exception:
                pass
    time_range = ""
    if len(timestamps) >= 2:
        span = (max(timestamps) - min(timestamps)).total_seconds() / 60
        time_range = f"{span:.1f} minutes"
    top_model = model_counts.most_common(1)[0] if model_counts else ("None", 0)
    confs = [d.get("confidence", 0) for d in detections if d.get("confidence")]
    avg_conf = sum(confs) / len(confs) if confs else 0
    return {
        "total": len(detections), "risk_counts": dict(risk_counts),
        "model_counts": dict(model_counts), "high_events": high_events[:5],
        "top_model": top_model, "time_range": time_range,
        "inc_sev": dict(Counter(i.get("severity", "?") for i in incidents)),
        "avg_conf": avg_conf, "total_inc": len(incidents),
    }


analytics = build_analytics(detections, incidents)


def build_system_prompt():
    a = analytics

    det_table = "No detections yet."
    if detections:
        rows = []
        for d in detections[:15]:
            ts = str(d.get("timestamp", ""))[:19]
            model = d.get("model_type", "?")
            risk = d.get("risk_level", "?")
            conf = float(d.get("confidence", 0))
            rows.append(f"  [{ts}] {model:30s} | Risk: {risk:8s} | Conf: {conf:.0%}")
        det_table = "\n".join(rows)

    inc_table = "No incidents."
    if incidents:
        rows = []
        for i in incidents:
            ts = str(i.get("timestamp", ""))[:19]
            sev = i.get("severity", "?")
            text = i.get("report_text", "")[:150]
            nlp = i.get("nlp_result", {}) or {}
            cause = nlp.get("cause", {}).get("cause_category", "unknown") if isinstance(nlp, dict) else "unknown"
            rows.append(f"  [{ts}] [{sev}] Cause: {cause} | {text}")
        inc_table = "\n".join(rows)

    high_table = "None."
    if a.get("high_events"):
        rows = []
        for d in a["high_events"]:
            ts = str(d.get("timestamp", ""))[:19]
            rows.append(f"  [{ts}] {d.get('model_type', '?')} ? {float(d.get('confidence', 0)):.0%} conf")
        high_table = "\n".join(rows)

    risk_d = a.get("risk_counts", {})
    model_d = a.get("model_counts", {})
    total = a.get("total", 0)

    return f"""You are SafeGuard AI Copilot ? an industrial safety intelligence assistant.

CRITICAL INSTRUCTION: Give ONLY your final answer. Do NOT show reasoning, thinking steps,
"let me analyze", "okay so", internal monologue, or draft text.
Output ONLY the structured final response. Start directly with the answer.

SYSTEM CONTEXT:
  Platform: Real-time AI Industrial Safety Monitor
  Models: YOLOv12 Fire/Smoke, YOLOv8 PPE/Intrusion/Fall, XGBoost Risk Engine, SBERT NLP
  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LIVE DATA:
  Total detections : {total}
  Risk breakdown   : HIGH={risk_d.get('HIGH',0)} ({risk_d.get('HIGH',0)/max(total,1)*100:.0f}%) | MEDIUM={risk_d.get('MEDIUM',0)} | LOW={risk_d.get('LOW',0)}
  Avg confidence   : {a.get('avg_conf',0):.0%}
  Time span        : {a.get('time_range','unknown')}
  Top model        : {a.get('top_model',('None',0))[0]} ({a.get('top_model',('None',0))[1]} detections)
  Model breakdown  : {json.dumps(model_d)}
  Total incidents  : {a.get('total_inc',0)}
  Incident severity: {json.dumps(a.get('inc_sev',{}))}

HIGH RISK EVENTS:
{high_table}

RECENT DETECTIONS:
{det_table}

ALL INCIDENTS (with NLP root cause):
{inc_table}

RESPONSE FORMAT RULES:
- Use **bold** for section headers
- Use bullet points (- item) for lists
- Use numbers (1. 2. 3.) for steps/procedures
- Include specific timestamps and numbers from the data
- Keep under 250 words unless asked for full detail
- NEVER show internal thinking or reasoning process
- Start your response immediately with the answer content"""


def extract_final_answer(raw: str) -> str:
    if not raw:
        return "I couldn't generate a response. Please try again."

    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    if cleaned and len(cleaned) > 50:
        return cleaned

    thinking_markers = [
        "okay, let's", "okay, the user", "okay so", "let me ",
        "first, i need", "first, let me", "i need to",
        "looking at the", "wait,", "hmm,", "let's think",
        "so the answer", "the user wants", "let me start",
        "so, compiling", "possible structure", "i should",
        "let me analyze", "alright,", "so i need to",
    ]

    lines = raw.split('\n')
    answer_lines = []
    in_thinking = True
    thinking_line_count = 0

    for line in lines:
        line_lower = line.lower().strip()
        is_thinking = any(line_lower.startswith(m) for m in thinking_markers)

        if in_thinking:
            thinking_line_count += 1
            if thinking_line_count >= 3:
                is_answer_start = (
                    line.strip().startswith("**") or
                    line.strip().startswith("## ") or
                    line.strip().startswith("# ") or
                    (line.strip().startswith("1.") and not is_thinking) or
                    (line.strip().startswith("-") and not is_thinking and len(line.strip()) > 10) or
                    ("current risk" in line_lower and not is_thinking) or
                    ("summary" in line_lower[:20] and "**" in line)
                )
                if is_answer_start:
                    in_thinking = False
                    answer_lines.append(line)
        else:
            answer_lines.append(line)

    if answer_lines:
        result = '\n'.join(answer_lines).strip()
        if len(result) > 80:
            return result

    paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]
    if len(paragraphs) >= 2:
        final_paras = []
        for para in paragraphs:
            para_lower = para.lower()
            is_thinking_para = any(
                para_lower.startswith(m) for m in thinking_markers
            ) or "let me" in para_lower[:40] or "wait," in para_lower[:20]

            if not is_thinking_para or final_paras:
                final_paras.append(para)

        if final_paras:
            result = '\n\n'.join(final_paras).strip()
            if len(result) > 80:
                return result

    chars = len(raw)
    return raw[int(chars * 0.4):].strip() if chars > 200 else raw


def call_nemotron(messages: list, system_prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return ("\u26A0\uFE0F **API key not configured.**\n\n"
                "Add to `.streamlit/secrets.toml`:\n"
                "```\nOPENROUTER_API_KEY = \"sk-or-v1-...\"\n```")

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages[-10:]
        ],
        "temperature": 0.2,
        "max_tokens": 700,
        "top_p": 0.85,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://safeguard-ai.streamlit.app",
        "X-Title": "SafeGuard AI Copilot",
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            try:
                err = resp.json()
            except Exception:
                err = {"error": {"message": resp.text}}
            msg = err.get("error", {}).get("message", "Unknown error")
            return f"\u26A0\uFE0F OpenRouter error ({resp.status_code}): {msg}"

        data = resp.json()

        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})

        raw = message.get("content", "")

        if not raw:
            for block in message.get("reasoning_details", []):
                if block.get("type") == "text":
                    raw = block.get("text", "")
                    break

        if not raw:
            parts = [b.get("text", "") for b in message.get("reasoning_details", [])
                     if b.get("type") == "text" and b.get("text", "").strip()]
            raw = "\n".join(parts)

        if not raw:
            return "I couldn't generate a response. The model returned empty output."

        return extract_final_answer(raw)

    except requests.exceptions.Timeout:
        return "\u23F1\uFE0F Request timed out. The model may be busy ? please retry in a moment."
    except Exception as e:
        return f"? Error: {str(e)}"


def format_response(text: str) -> str:
    lines = text.split('\n')
    html = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append("<br>")
            continue

        stripped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)

        if stripped.startswith('- ') or stripped.startswith('? '):
            if not in_list:
                html.append("<ul style='margin:6px 0; padding-left:18px;'>")
                in_list = True
            html.append(f"<li style='margin:3px 0; color:#ccc;'>{stripped[2:]}</li>")

        elif re.match(r'^\d+\.', stripped):
            if not in_list:
                html.append("<ol style='margin:6px 0; padding-left:18px;'>")
                in_list = True
            content = re.sub(r'^\d+\.\s*', '', stripped)
            html.append(f"<li style='margin:3px 0; color:#ccc;'>{content}</li>")

        else:
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<p style='margin:4px 0;'>{stripped}</p>")

    if in_list:
        html.append("</ul>")

    return ''.join(html)


# Header
st.markdown(
    """
    <div style="padding:8px 0 10px;">
      <h1 style="font-size:28px;font-weight:800;color:#f0f2f8;margin:0;letter-spacing:-0.02em;">\U0001F916 AI Safety Copilot</h1>
      <p style="color:#8892a4;font-size:13px;margin:6px 0 0 0;">
        Powered by <b style="color:#7c5cfc;">nvidia/nemotron-nano-9b-v2</b> via OpenRouter ?
        Live Supabase context ? Industrial safety intelligence
      </p>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,
      transparent, #1a2035 20%, #1a2035 80%, transparent);
      margin: 16px 0 18px 0;"></div>
    """,
    unsafe_allow_html=True,
)

col_chat, col_ctx = st.columns([3, 1])

with col_ctx:
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 12px 0;">
          Live Context
        </p>
        """,
        unsafe_allow_html=True,
    )

    a = analytics
    HIGH = a.get("risk_counts", {}).get("HIGH", 0)
    MEDIUM = a.get("risk_counts", {}).get("MEDIUM", 0)
    LOW = a.get("risk_counts", {}).get("LOW", 0)
    total = a.get("total", 0)

    if total > 0:
        st.markdown(
            f"""
            <div class="context-card">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#4a5568;">Detection Summary</div>
              <div class="context-metric">{total}</div>
              <div style="display:flex;gap:8px;align-items:center;margin-top:6px;">
                <span style="color:#f03b3b;font-weight:700;">HIGH {HIGH}</span>
                <span style="color:#f5a623;font-weight:700;">MED {MEDIUM}</span>
                <span style="color:#00e5a0;font-weight:700;">LOW {LOW}</span>
              </div>
              <div style="font-size:11px;color:#8892a4;margin-top:6px;">Avg conf {a.get('avg_conf',0):.0%}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='context-card'>No detections yet.</div>", unsafe_allow_html=True)

    if detections:
        latest = detections[0]
        rl = latest.get("risk_level", "?")
        rc = "#f03b3b" if rl == "HIGH" else "#f5a623" if rl == "MEDIUM" else "#00e5a0"
        st.markdown(
            f"""
            <div class="context-card">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#4a5568;">Latest Detection</div>
              <div style="font-size:18px;font-weight:800;color:{rc};margin-top:4px;">{rl}</div>
              <div style="color:#f0f2f8;font-size:12px;">{latest.get('model_type','?')}</div>
              <div style="color:#4a5568;font-size:11px;" class="mono">{str(latest.get('timestamp',''))[:19]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if a.get("model_counts") and total > 0:
        st.markdown(
            """
            <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                       text-transform:uppercase; color:#4a5568; margin:12px 0 8px 0;">
              Model Activity
            </p>
            """,
            unsafe_allow_html=True,
        )
        for model, count in sorted(a["model_counts"].items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            short = model.replace(" Detection", "").replace(" & Smoke", "")
            color = MODEL_COLORS.get(model, "#00c4f0")
            st.markdown(
                f"""
                <div style="margin-bottom:8px;">
                  <div style="display:flex; justify-content:space-between; color:#8892a4; font-size:11px; margin-bottom:4px;">
                    <span>{short}</span><span>{count}</span>
                  </div>
                  <div class="model-bar">
                    <div style="width:{pct:.0f}%; background:{color};"></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:1px;background:#1a2035;margin:16px 0;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style="font-size:11px; font-weight:500; letter-spacing:0.1em;
                   text-transform:uppercase; color:#4a5568; margin:0 0 8px 0;">
          Quick Questions
        </p>
        """,
        unsafe_allow_html=True,
    )

    quick_prompts = [
        "What is the current risk level and trend?",
        "Give a full detection summary with numbers",
        "Which model triggered the most HIGH risk alerts?",
        "List all HIGH risk events with timestamps",
        "Analyze all incidents and identify root causes",
        "What urgent safety actions are needed right now?",
        "Are there dangerous patterns in the detection data?",
        "Compare activity across all detection models",
    ]

    st.markdown("<div class='quick-chips'>", unsafe_allow_html=True)
    for qp in quick_prompts:
        if st.button(qp, key=f"qp_{qp}"):
            st.session_state.messages.append({"role": "user", "content": qp})
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:#1a2035;margin:16px 0;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

# Chat panel
with col_chat:

    if not st.session_state.messages:
        st.markdown(
            f"""
            <div style="text-align:center; padding:50px 20px;">
              <div style="font-size:52px; margin-bottom:16px;">\U0001F916</div>
              <h3 style="color:#7c5cfc; margin:0;">SafeGuard AI Copilot</h3>
              <p style="color:#8892a4; margin:10px 0 0 0; font-size:13px; line-height:1.8;">
                I have live access to your Supabase safety data.<br>
                Monitoring <b style="color:#00c4f0;">{total} detections</b>
                and <b style="color:#f5a623;">{a.get('total_inc',0)} incidents</b>.<br>
                Ask me anything ? I'll give you direct, data-driven answers.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class="chat-row user">
                      <div class="chat-bubble-user">{msg['content']}</div>
                      <div class="avatar user">\U0001F464</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                formatted = format_response(msg["content"])
                st.markdown(
                    f"""
                    <div class="chat-row ai">
                      <div class="avatar ai">\U0001F916</div>
                      <div class="chat-bubble-ai">{formatted}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if (st.session_state.messages and st.session_state.messages[-1]["role"] == "user"):
        thinking_ph = st.markdown(
            """
            <div class="thinking-dots">
              <div></div><div></div><div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        system_prompt = build_system_prompt()
        response = call_nemotron(st.session_state.messages, system_prompt)

        thinking_ph.empty()
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_in, col_send = st.columns([5, 1])

    with col_in:
        user_input = st.text_input(
            "msg",
            placeholder="Ask about detections, risk levels, incidents...",
            label_visibility="collapsed",
            key="chat_input"
        )
    with col_send:
        st.markdown("<div class='send-button'>", unsafe_allow_html=True)
        send_btn = st.button("Send", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if (send_btn or user_input) and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.rerun()

if not OPENROUTER_API_KEY:
    st.markdown(
        """
        <div style='background:#2a1a1a; border:1px solid #ff4d4d55;
                    border-radius:10px; padding:14px; margin-top:16px;'>
          <h4 style='color:#ff4d4d; margin:0 0 8px 0;'>\u26A0\uFE0F OpenRouter API Key Required</h4>
          <p style='color:#ccc; font-size:13px; margin:0 0 8px 0;'>
            Create <code>.streamlit\\secrets.toml</code>:
          </p>
          <pre style='background:#1a1a1a; padding:10px; border-radius:6px;
                      color:#7c5cfc; font-size:12px; margin:0;'>OPENROUTER_API_KEY = "sk-or-v1-your-key-here"</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


