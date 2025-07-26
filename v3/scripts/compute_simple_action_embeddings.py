import os
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

# Path to v3 action schema
SCHEMA_PATH = os.path.join('v3', 'action_schema.py')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
OUTPUT_PATH = 'simple_action_embeddings.pkl'

# --- Load the ACTIONS dict from the schema ---
ACTIONS = None
with open(SCHEMA_PATH, 'r') as f:
    code = f.read()
    # Evaluate only the ACTIONS dict
    ns = {}
    exec(code, ns)
    ACTIONS = ns['ACTIONS']

# --- Define which actions are 'simple' ---
# For now, all except 'unknown' and 'greeting' (customize as needed)
SIMPLE_ACTIONS = [
    name for name in ACTIONS.keys()
    if name not in ('unknown', 'greeting')
]

# --- Prepare strings to embed ---
action_strings = {
    name: f"{name}: {ACTIONS[name]['description']}"
    for name in SIMPLE_ACTIONS
}

# --- Compute embeddings ---
print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
print(f"Computing embeddings for {len(action_strings)} actions...")
embeddings = embedder.encode(list(action_strings.values()), show_progress_bar=True)

# --- Store as dict {action_name: embedding} ---
action_embeddings = {
    name: emb for name, emb in zip(action_strings.keys(), embeddings)
}

with open(OUTPUT_PATH, 'wb') as f:
    pickle.dump(action_embeddings, f)

print(f"Saved embeddings for {len(action_embeddings)} actions to {OUTPUT_PATH}") 