# backend/services/nlp_engine.py
#
# After running nlp_model.ipynb, copy these files to ml_models/:
#   - nlp_rule_embeddings.pkl
#   - safety_rules.json
#   - cause_categories.json

import os
import re
import json
import numpy as np
import joblib
import nltk

nltk.download('punkt',     quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus   import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# ---- Paths ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml_models")

RULES_PATH      = os.path.join(MODELS_DIR, 'safety_rules.json')
CAUSES_PATH     = os.path.join(MODELS_DIR, 'cause_categories.json')
EMBEDDINGS_PATH = os.path.join(MODELS_DIR, 'nlp_rule_embeddings.pkl')

STOP_WORDS = set(stopwords.words('english'))

# ---- Lazy-loaded globals ----
_sbert            = None
_safety_rules     = None
_rule_embeddings  = None
_cause_categories = None


def _load():
    global _sbert, _safety_rules, _rule_embeddings, _cause_categories
    if _sbert is None:
        _sbert = SentenceTransformer('all-MiniLM-L6-v2')

    if _safety_rules is None:
        try:
            with open(RULES_PATH) as f:
                _safety_rules = json.load(f)
        except FileNotFoundError:
            _safety_rules = []

    if _cause_categories is None:
        try:
            with open(CAUSES_PATH) as f:
                _cause_categories = json.load(f)
        except FileNotFoundError:
            _cause_categories = {}

    if _rule_embeddings is None:
        try:
            _rule_embeddings = joblib.load(EMBEDDINGS_PATH)
        except FileNotFoundError:
            _rule_embeddings = np.zeros((0, 384), dtype=np.float32)


# ---- Task 1: Cause Extraction ----
def extract_cause(text: str) -> dict:
    _load()
    text_lower = text.lower()

    category_scores = {}
    for category, keywords in _cause_categories.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            category_scores[category] = score

    cause_category = max(category_scores, key=category_scores.get) if category_scores else 'unknown'

    tokens   = word_tokenize(text_lower)
    keywords = [w for w in tokens if w.isalpha() and w not in STOP_WORDS and len(w) > 3]
    freq = {}
    for w in keywords:
        freq[w] = freq.get(w, 0) + 1
    top_keywords = sorted(freq, key=freq.get, reverse=True)[:8]

    cause_patterns = ['caused by', 'due to', 'resulted in', 'because', 'reason was', 'root cause']
    sentences      = sent_tokenize(text)
    cause_sentence = ''
    for sent in sentences:
        if any(p in sent.lower() for p in cause_patterns):
            cause_sentence = sent.strip()
            break
    if not cause_sentence and sentences:
        cause_sentence = sentences[0]

    return {
        'cause_category': cause_category,
        'keywords':       top_keywords,
        'cause_sentence': cause_sentence,
    }


# ---- Task 2: Rule Violation Checking ----
def check_rule_violations(text: str, top_k: int = 3, threshold: float = 0.30) -> list:
    _load()
    if _rule_embeddings is None or _rule_embeddings.size == 0 or not _safety_rules:
        return []

    report_embedding = _sbert.encode([text], convert_to_numpy=True)
    similarities     = cosine_similarity(report_embedding, _rule_embeddings)[0]

    results = []
    for i, score in enumerate(similarities):
        if score >= threshold:
            results.append({
                'rule_id':          _safety_rules[i]['id'],
                'rule':             _safety_rules[i]['rule'],
                'similarity_score': round(float(score), 3),
            })

    results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    return results[:top_k]


# ---- Task 3: Summarization ----
def summarize_report(text: str, num_sentences: int = 3) -> str:
    _load()
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text

    embeddings = _sbert.encode(sentences, convert_to_numpy=True)
    sim_matrix = cosine_similarity(embeddings)
    scores     = sim_matrix.sum(axis=1)
    scores[0] *= 1.2

    top_indices = sorted(np.argsort(scores)[-num_sentences:])
    return ' '.join([sentences[i] for i in top_indices])


# ---- Combined function ----
def analyze_report(text: str) -> dict:
    """
    Full NLP analysis of an incident report.

    Parameters
    ----------
    text : str — raw incident report text

    Returns
    -------
    dict:
    {
        'summary':    str,
        'cause':      { 'cause_category', 'keywords', 'cause_sentence' },
        'violations': [ { 'rule_id', 'rule', 'similarity_score' } ]
    }
    """
    return {
        'summary':    summarize_report(text),
        'cause':      extract_cause(text),
        'violations': check_rule_violations(text),
    }
