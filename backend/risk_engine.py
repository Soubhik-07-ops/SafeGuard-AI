# backend/risk_engine.py
# Wrapper — points to backend/services/risk_engine.py

from .services.risk_engine import predict_risk

__all__ = ["predict_risk"]
