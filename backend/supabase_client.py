from supabase import create_client
import streamlit as st
import os

# Try Streamlit secrets first, fallback to env vars
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# DO NOT hardcode credentials in source code
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def log_detection(model_type, label, confidence, risk_level, risk_score):
    if supabase is None:
        return
    try:
        supabase.table("detections").insert({
            "model_type": model_type,
            "label":      label,
            "confidence": round(float(confidence), 3),
            "risk_level": risk_level,
            "risk_score": round(float(risk_score), 3),
        }).execute()
    except Exception as e:
        print(f"[Supabase] log_detection error: {e}")


def fetch_recent_detections(limit=50):
    if supabase is None:
        return []
    try:
        res = supabase.table("detections") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
        return res.data
    except Exception as e:
        print(f"[Supabase] fetch_recent_detections error: {e}")
        return []


def log_incident(report_text, severity, nlp_result):
    if supabase is None:
        return
    try:
        supabase.table("incidents").insert({
            "report_text": report_text,
            "severity":    severity,
            "nlp_result":  nlp_result,
        }).execute()
    except Exception as e:
        print(f"[Supabase] log_incident error: {e}")


def fetch_incidents(limit=20):
    if supabase is None:
        return []
    try:
        res = supabase.table("incidents") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
        return res.data
    except Exception as e:
        print(f"[Supabase] fetch_incidents error: {e}")
        return []
