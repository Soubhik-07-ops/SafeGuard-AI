# backend/services/risk_engine.py
#
# Drop risk_model.pkl, risk_label_encoder.pkl, risk_features.pkl
# into ml_models/ after running the Jupyter notebook.

import os
import pandas as pd
import joblib

# ---- Paths ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml_models")

MODEL_PATH    = os.path.join(MODELS_DIR, 'risk_model.pkl')
ENCODER_PATH  = os.path.join(MODELS_DIR, 'risk_label_encoder.pkl')
FEATURES_PATH = os.path.join(MODELS_DIR, 'risk_features.pkl')

ZONE_MAP = {
    'Zone A - Entry':     0,
    'Zone B - Warehouse': 1,
    'Zone C - Machinery': 2,
    'Zone D - Exit':      3,
}

# ---- Lazy load (only loads when first called) ----
_model    = None
_encoder  = None
_features = None


def _load():
    global _model, _encoder, _features
    if _model is None:
        _model    = joblib.load(MODEL_PATH)
        _encoder  = joblib.load(ENCODER_PATH)
        _features = joblib.load(FEATURES_PATH)


def predict_risk(detections: list) -> dict:
    """
    Predict risk level from CV model detections.

    Parameters
    ----------
    detections : list of dicts
        Each dict: { 'type': str, 'confidence': float, 'zone': str }
        type options: 'fire_smoke' | 'ppe_violation' | 'intrusion' | 'fall'

    Returns
    -------
    dict: { 'risk': str, 'confidence': float, 'features': dict }
    """
    _load()

    fire_det      = next((d for d in detections if d['type'] == 'fire_smoke'),    None)
    ppe_det       = next((d for d in detections if d['type'] == 'ppe_violation'), None)
    intrusion_det = next((d for d in detections if d['type'] == 'intrusion'),     None)
    fall_det      = next((d for d in detections if d['type'] == 'fall'),          None)

    fire_flag      = 1 if fire_det      else 0
    ppe_flag       = 1 if ppe_det       else 0
    intrusion_flag = 1 if intrusion_det else 0
    fall_flag      = 1 if fall_det      else 0

    fire_conf      = fire_det['confidence']      if fire_det      else 0.0
    ppe_conf       = ppe_det['confidence']       if ppe_det       else 0.0
    intrusion_conf = intrusion_det['confidence'] if intrusion_det else 0.0
    fall_conf      = fall_det['confidence']      if fall_det      else 0.0

    active_detections = fire_flag + ppe_flag + intrusion_flag + fall_flag
    max_confidence    = max(fire_conf, ppe_conf, intrusion_conf, fall_conf)

    zone_str = detections[0]['zone'] if detections else 'Zone A - Entry'
    zone_id  = ZONE_MAP.get(zone_str, 0)

    features = {
        'fire_smoke':         fire_flag,
        'ppe_violation':      ppe_flag,
        'intrusion':          intrusion_flag,
        'fall':               fall_flag,
        'fire_conf':          fire_conf,
        'ppe_conf':           ppe_conf,
        'intrusion_conf':     intrusion_conf,
        'fall_conf':          fall_conf,
        'active_detections':  active_detections,
        'max_confidence':     max_confidence,
        'zone_id':            zone_id,
    }

    X_input  = pd.DataFrame([features])[_features]
    pred_idx = _model.predict(X_input)[0]
    proba    = _model.predict_proba(X_input)[0]
    risk     = _encoder.classes_[pred_idx]

    return {
        'risk':       risk,
        'confidence': round(float(proba[pred_idx]), 3),
        'features':   features,
    }
