"""
Machine Learning and Rule-Based Priority Engine for TicketFlow.
Integrates TF-IDF Vectorization, Logistic Regression, and Heuristic Priority Detection.
"""

import os
import pickle
from typing import Tuple, Dict, Any, Optional
import streamlit as st

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_FILE = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")

# Department mapping as defined in project specifications
DEPARTMENT_MAPPING = {
    "Technical": "Technical Support",
    "Billing": "Billing Support",
    "Account": "Account Support",
    "Service": "Customer Service"
}

# Rule keywords for priority detection
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "immediately", "critical", "emergency", "asap",
    "crash", "crashed", "hacked", "unauthorized", "locked out",
    "charged twice", "overcharged", "stolen", "broken", "server down",
    "down", "severe", "blocker"
]

MEDIUM_PRIORITY_KEYWORDS = [
    "error", "bug", "issue", "delay", "delayed", "refund",
    "freeze", "slow", "timeout", "declined", "cancel",
    "warning", "unable", "problem", "failed", "failure"
]


def detect_priority(text: str) -> str:
    """
    Assigns ticket priority (High, Medium, Low) based on keyword heuristics.
    Preserves existing rule logic and keyword triggers.
    """
    clean_text = text.lower()

    for word in HIGH_PRIORITY_KEYWORDS:
        if word in clean_text:
            return "High"

    for word in MEDIUM_PRIORITY_KEYWORDS:
        if word in clean_text:
            return "Medium"

    return "Low"


@st.cache_resource(show_spinner=False)
def load_model_artifacts() -> Tuple[Optional[Any], Optional[Any]]:
    """
    Loads saved Logistic Regression model and TF-IDF vectorizer from disk.
    Cached with @st.cache_resource so it executes once and never re-reads files on reruns.
    """
    if not os.path.exists(MODEL_FILE) or not os.path.exists(VECTORIZER_FILE):
        try:
            from train_model import train_and_save_model
            train_and_save_model()
        except Exception:
            return None, None

    try:
        with open(MODEL_FILE, "rb") as f_model:
            model = pickle.load(f_model)

        with open(VECTORIZER_FILE, "rb") as f_vec:
            vectorizer = pickle.load(f_vec)

        return model, vectorizer
    except Exception:
        # If unpickling fails due to sklearn version differences, retrain automatically
        try:
            from train_model import train_and_save_model
            train_and_save_model()
            with open(MODEL_FILE, "rb") as f_model:
                model = pickle.load(f_model)
            with open(VECTORIZER_FILE, "rb") as f_vec:
                vectorizer = pickle.load(f_vec)
            return model, vectorizer
        except Exception:
            return None, None


def classify_complaint(text: str) -> Dict[str, Any]:
    """
    Performs full ticket triage on input complaint text:
    1. Feature extraction via TF-IDF
    2. Category classification via Logistic Regression
    3. Probability scores across all 4 categories
    4. Heuristic priority detection
    5. Support department routing
    """
    model, vectorizer = load_model_artifacts()
    if model is None or vectorizer is None:
        raise RuntimeError("Model artifacts (model.pkl / tfidf_vectorizer.pkl) not available.")

    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Complaint text cannot be empty.")

    # 1. Feature extraction
    tfidf_features = vectorizer.transform([clean_text])

    # 2. Category prediction
    predicted_cat = model.predict(tfidf_features)[0]

    # 3. Class probabilities
    probabilities = {}
    confidence = 0.0
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(tfidf_features)[0]
        for cls_name, prob in zip(model.classes_, probs):
            probabilities[cls_name] = round(float(prob) * 100, 1)
        confidence = probabilities.get(predicted_cat, 0.0)

    # 4. Priority detection
    priority = detect_priority(clean_text)

    # 5. Department routing
    department = DEPARTMENT_MAPPING.get(predicted_cat, "Customer Service")

    return {
        "category": predicted_cat,
        "priority": priority,
        "department": department,
        "confidence": confidence,
        "probabilities": probabilities
    }
