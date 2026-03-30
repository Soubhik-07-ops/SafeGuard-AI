# ML & NLP Model Files

Trained model files (.pkl) are excluded from this repository.
JSON data files are included.

## Included Files
- `safety_rules.json` — Safety rule database for NLP matching
- `cause_categories.json` — Incident cause category definitions

## Excluded Files (regenerate locally)

| File | Description | Notebook |
|------|-------------|----------|
| `risk_model.pkl` | XGBoost risk classifier | `notebooks/risk_engine_training.ipynb` |
| `risk_label_encoder.pkl` | Label encoder | Same notebook |
| `risk_features.pkl` | Feature list | Same notebook |
| `nlp_rule_embeddings.pkl` | SBERT rule embeddings | `notebooks/nlp_model_training.ipynb` |

## Regenerate Instructions

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Risk Engine notebook
jupyter notebook notebooks/risk_engine_training.ipynb

# 3. Run NLP Model notebook
jupyter notebook notebooks/nlp_model_training.ipynb

# Files will be saved to ml_models/ automatically
```
