import joblib
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
MODEL_NAME = 'all-MiniLM-L6-v2'  # Must match training
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
CLASSIFIER_PATH = os.path.join(MODEL_DIR, 'intent_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'intent_label_encoder.joblib')

# -----------------------------
# LOAD MODELS
# -----------------------------
print("Loading embedding model...")
embedder = SentenceTransformer(MODEL_NAME)
print("Loading classifier and label encoder...")
clf = joblib.load(CLASSIFIER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

# -----------------------------
# INTERACTIVE LOOP
# -----------------------------
print("\nSAM Intent Classifier Test Console")
print("Type a message and see the predicted intent probabilities. Type 'exit' to quit.\n")

while True:
    user_input = input("Enter a message: ").strip()
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Exiting.")
        break
    if not user_input:
        continue
    # Compute embedding
    embedding = embedder.encode([user_input])
    # Predict probabilities
    probs = clf.predict_proba(embedding)[0]
    # Print results
    print("\nProbabilities:")
    for label, prob in zip(label_encoder.classes_, probs):
        print(f"  {label:7}: {prob:.3f}")
    print("") 