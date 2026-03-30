# backend/nlp_engine.py
# Wrapper — points to backend/services/nlp_engine.py

from .services.nlp_engine import analyze_report

__all__ = ["analyze_report"]
