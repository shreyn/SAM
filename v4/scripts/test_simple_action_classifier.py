import joblib
from sentence_transformers import SentenceTransformer
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_action_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_action_label_encoder.joblib')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# Load model and encoder
clf = joblib.load(MODEL_PATH)
le = joblib.load(LABEL_ENCODER_PATH)
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

print("Type 'exit' to quit.")
while True:
    text = input("Enter a user command: ").strip()
    if text.lower() in ["exit", "quit", "bye"]:
        break
    emb = embedder.encode([text])
    pred = clf.predict(emb)[0]
    label = le.inverse_transform([pred])[0]
    print(f"Predicted action: {label}") 