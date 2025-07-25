import joblib
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Paths to the trained models (now in v4/models/)
CLASSIFIER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'intent_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'intent_label_encoder.joblib')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'  # Must match training

class IntentClassifier:
    def __init__(self):
        # Load embedding model
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        # Load classifier and label encoder
        self.clf = joblib.load(CLASSIFIER_PATH)
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)

    def classify(self, text):
        """
        Classify a text string. Returns (top_class, probabilities_dict)
        """
        embedding = self.embedder.encode([text])
        probs = self.clf.predict_proba(embedding)[0]
        top_idx = np.argmax(probs)
        top_class = self.label_encoder.classes_[top_idx]
        prob_dict = {label: float(prob) for label, prob in zip(self.label_encoder.classes_, probs)}
        return top_class, prob_dict 