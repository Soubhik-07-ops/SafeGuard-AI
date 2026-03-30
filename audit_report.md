---
# SafeGuard AI — Project Audit Report
Generated: 2026-03-30 22:11:55 +05:30
Root: D:\VIT\EPICS\SafeGuard-AI\

## Summary
| Category | Status | Issues Found |
|----------|--------|-------------|
| Model Files | ⚠️ | 1 issue |
| Backend Paths | ⚠️ | 1 issue |
| Page Imports | ✅ | 0 issues |
| Orphan Files | ⚠️ | 5 issues |
| Security | ❌ | 2 issues |
| Requirements | ⚠️ | 7 issues |
| .gitignore | ⚠️ | 2 issues |

**Overall Status: NEEDS FIXES**

---

## 1. Model Files (models/)

### fire_detector.py
- Status: ✅ OK
- Class name: ✅ FireDetector
- Model path: ✅ cv_models/fire_best.onnx
- Fix required:
  ```python
  # No change required
  ```

### intrusion_detector.py
- Status: ✅ OK
- Class name: ✅ IntrusionDetector
- Model path: ✅ cv_models/yolov8m.pt
- Fix required:
  ```python
  # No change required
  ```

### fall_detector.py
- Status: ⚠️ Needs review
- Class name: ✅ FallDetector
- Model path: ⚠️ Uses cv_models/yolov10s.pt (spec expects yolov8n.pt or best.pt)
- Fix required:
  ```python
  def __init__(self):
      project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      model_path = os.path.join(project_root, "cv_models", "yolov8n.pt")
      self.model = YOLO(model_path)
  ```

### ppe_detector.py
- Status: ✅ OK
- Class name: ✅ PPEDetector
- Model path: ✅ cv_models/best.pt (allowed by spec)
- Fix required:
  ```python
  # No change required
  ```

---

## 2. Backend Services

### backend/services/risk_engine.py
- MODELS_DIR: ✅ ml_models/
- Fix:
  ```python
  ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  MODELS_DIR = os.path.join(ROOT, 'ml_models')
  ```

### backend/services/nlp_engine.py
- MODELS_DIR: ✅ ml_models/
- Fix:
  ```python
  ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  MODELS_DIR = os.path.join(ROOT, 'ml_models')
  ```

### backend/risk_engine.py (wrapper)
- Status: ⚠️ Non-conforming pattern
- Issue: Wrapper uses package-relative import (works) but does NOT match the required sys.path pattern.
- Fix:
  ```python
  import os, sys
  _SERVICE = os.path.join(os.path.dirname(__file__), 'services')
  sys.path.insert(0, _SERVICE)
  from risk_engine import predict_risk
  ```

### backend/nlp_engine.py (wrapper)
- Status: ⚠️ Non-conforming pattern
- Issue: Wrapper uses package-relative import (works) but does NOT match the required sys.path pattern.
- Fix:
  ```python
  import os, sys
  _SERVICE = os.path.join(os.path.dirname(__file__), 'services')
  sys.path.insert(0, _SERVICE)
  from nlp_engine import analyze_report
  ```

### backend/supabase_client.py
- Hardcoded secrets: ✅ None
- Fix: None required

---

## 3. Page Import Issues

### pages/01_Dashboard.py
- ROOT setup: ✅
- Backend imports: ✅
- Utils import + inject_css(): ✅
- Specific imports: ✅ plotly, pandas, fetch_recent_detections, fetch_incidents

### pages/02_Detection.py
- ROOT setup: ✅
- Detector imports: ✅ (models.*)
- Backend imports: ✅ (log_detection, predict_risk)
- Utils import + inject_css(): ✅

### pages/03_Incidents.py
- ROOT setup: ✅
- Backend imports: ✅ (analyze_report, log_incident, fetch_incidents)
- Utils import + inject_css(): ✅

### pages/04_Analytics.py
- ROOT setup: ✅
- Backend imports: ✅ (fetch_recent_detections, fetch_incidents)
- Utils import + inject_css(): ✅
- Specific imports: ✅ plotly, pandas

### pages/05_Copilot.py
- ROOT setup: ✅
- Backend imports: ✅ (fetch_recent_detections, fetch_incidents)
- Utils import + inject_css(): ✅
- Specific imports: ✅ requests

---

## 4. Orphaned Files

| File | Used By | Action |
|------|---------|--------|
| cv_models/yolov8n.pt | Nothing | ⚠️ Remove or switch Fall/PPE detector to use it |
| assets/1.mp4 | Nothing | ⚠️ Gitignore or remove before push |
| assets/fall5.mp4 | Nothing | ⚠️ Gitignore or remove before push |
| assets/fall_test.mp4 | Nothing | ⚠️ Gitignore or remove before push |
| assets/fall_test1.mp4 | Nothing | ⚠️ Gitignore or remove before push |

---

## 5. Security Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| .streamlit/secrets.toml | 5-9 | Hardcoded OpenRouter and Supabase credentials | Delete file and rotate keys |
| .streamlit/secrets.toml.example | N/A | Missing example template | Create placeholder-only example file |

---

## 6. Requirements.txt Gaps

Missing packages:
- torch → required by ultralytics/YOLO inference

Unused packages (not imported anywhere):
- streamlit-autorefresh
- opencv-python-headless
- transformers
- python-dotenv
- PyYAML
- Pillow
- xgboost (not directly imported, but may be required to deserialize model)

---

## 7. .gitignore Gaps

Missing entries:
- *.mp4
- assets/*.mp4

---

## 8. Complete Fix Script

```python
# Run this script to auto-fix all path issues
# D:\VIT\EPICS\SafeGuard-AI\fix_paths.py

import os

ROOT = r"D:\VIT\EPICS\SafeGuard-AI"

fixes = {
    "models/fall_detector.py": [
        ("yolov10s.pt", "yolov8n.pt"),
    ],
    "backend/risk_engine.py": [
        ("from .services.risk_engine import predict_risk",
         "import os, sys\n_SERVICE = os.path.join(os.path.dirname(__file__), 'services')\nsys.path.insert(0, _SERVICE)\nfrom risk_engine import predict_risk"),
    ],
    "backend/nlp_engine.py": [
        ("from .services.nlp_engine import analyze_report",
         "import os, sys\n_SERVICE = os.path.join(os.path.dirname(__file__), 'services')\nsys.path.insert(0, _SERVICE)\nfrom nlp_engine import analyze_report"),
    ],
    ".gitignore": [
        ("# ── Streamlit ───────────────────────────\n.streamlit/secrets.toml\n",
         "# ── Streamlit ───────────────────────────\n.streamlit/secrets.toml\n\n# ── Media ───────────────────────────────\n*.mp4\nassets/*.mp4\n"),
    ],
    "requirements.txt": [
        ("# ── Computer Vision ─────────────────────\n",
         "# ── Computer Vision ─────────────────────\n"),
        ("ultralytics>=8.3.0\n", "ultralytics>=8.3.0\ntorch>=2.1.0\n"),
    ],
}

for filepath, replacements in fixes.items():
    full_path = os.path.join(ROOT, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {filepath}")
```

---

## 9. Files to Restore from Backup

Backup path check:
- D:\VIT\EPICS\PART-A\ was not found (deleted in current workspace).

| New File | Backup Source | Status |
|----------|--------------|--------|
| models/fire_detector.py | PART-A\Smoke_detection\fire_module.py | ⚠️ Backup missing |
| models/intrusion_detector.py | PART-A\Intrusion_detection\intrusion.py | ⚠️ Backup missing |
| models/fall_detector.py | PART-A\Fall_detection\fall_module.py | ⚠️ Backup missing |
| models/ppe_detector.py | PART-A\PPE_detection\ppe_module.py | ⚠️ Backup missing |

---

## 10. Pre-Push Final Checklist

- [ ] All model paths use cv_models/ (no absolute paths)
- [ ] All ML paths use ml_models/ (no absolute paths)
- [ ] No hardcoded API keys or Supabase credentials
- [ ] .mp4 files added to .gitignore
- [ ] yolov10s.pt orphan resolved (use or remove)
- [ ] best.pt identified and assigned to correct detector
- [ ] All page imports use models.X and backend.X
- [ ] streamlit run app.py runs without ImportError
- [ ] audit_report.md committed to repo as documentation
---
