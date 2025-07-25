import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import numpy as np
print("Numpy version at training time:", np.__version__)

# -----------------------------
# CONFIGURATION
# -----------------------------
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'training_data', 'SAM classifier training data - Sheet1 (2).csv')  # Path to your labeled CSV
default_model_name = 'all-MiniLM-L6-v2'  # Embedding model
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models'))
os.makedirs(MODEL_DIR, exist_ok=True)
CLASSIFIER_PATH = os.path.join(MODEL_DIR, 'intent_classifier.joblib')  # Where to save the trained classifier
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'intent_label_encoder.joblib')  # Where to save the label encoder
print("Saving classifier to:", CLASSIFIER_PATH)
print("Saving label encoder to:", LABEL_ENCODER_PATH)

# -----------------------------
# 1. LOAD DATA
# -----------------------------
print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)
assert 'text' in df.columns and 'label' in df.columns, "CSV must have 'text' and 'label' columns."

# -----------------------------
# 2. COMPUTE EMBEDDINGS
# -----------------------------
print(f"Loading embedding model: {default_model_name} ...")
embedder = SentenceTransformer(default_model_name)
print("Computing sentence embeddings...")
embeddings = embedder.encode(df['text'].tolist(), show_progress_bar=True)

# -----------------------------
# 3. ENCODE LABELS
# -----------------------------
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['label'])

# -----------------------------
# 4. TRAIN/VALIDATION SPLIT
# -----------------------------
X_train, X_val, y_train, y_val = train_test_split(embeddings, y, test_size=0.2, random_state=42, stratify=y)

# -----------------------------
# 5. TRAIN CLASSIFIER
# -----------------------------
print("Training logistic regression classifier...")
clf = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000, random_state=42)
clf.fit(X_train, y_train)

# -----------------------------
# 6. EVALUATE
# -----------------------------
print("Evaluating on validation set...")
y_pred = clf.predict(X_val)
print(classification_report(y_val, y_pred, target_names=label_encoder.classes_))
print(f"Validation accuracy: {accuracy_score(y_val, y_pred):.3f}")

# -----------------------------
# 7. SAVE MODELS
# -----------------------------
print(f"Saving classifier to {CLASSIFIER_PATH}")
joblib.dump(clf, CLASSIFIER_PATH, protocol=4)
print(f"Saving label encoder to {LABEL_ENCODER_PATH}")
joblib.dump(label_encoder, LABEL_ENCODER_PATH, protocol=4)

print("\nTraining complete! You can now use these models for inference in your SAM pipeline.")

# -----------------------------
# USAGE NOTES
# -----------------------------
# At inference time, load the same embedding model, the classifier, and the label encoder.
# For a new input:
#   1. Compute its embedding.
#   2. Use clf.predict([embedding]) to get the class index.
#   3. Use label_encoder.inverse_transform([class_index]) to get the class label. 