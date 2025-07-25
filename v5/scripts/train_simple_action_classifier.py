import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Paths
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'training_data', 'simple_action_training_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_action_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_action_label_encoder.joblib')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# 1. Load data
df = pd.read_csv(DATA_PATH)
X = df['text'].tolist()
y = df['action'].tolist()

# 2. Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 3. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# 4. Embed text
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
X_train_emb = embedder.encode(X_train)
X_test_emb = embedder.encode(X_test)

# 5. Train classifier
clf = LogisticRegression(max_iter=1000, multi_class='multinomial')
clf.fit(X_train_emb, y_train)

# 6. Evaluate
y_pred = clf.predict(X_test_emb)
print('Classification Report:')
print(classification_report(y_test, y_pred, target_names=le.classes_))
print('Confusion Matrix:')
print(confusion_matrix(y_test, y_pred))

# 7. Save model and encoder
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(clf, MODEL_PATH)
joblib.dump(le, LABEL_ENCODER_PATH)
print(f"Model saved to {MODEL_PATH}")
print(f"Label encoder saved to {LABEL_ENCODER_PATH}") 