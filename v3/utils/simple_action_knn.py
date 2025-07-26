import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

EMBEDDINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'simple_action_embeddings.pkl')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

class SimpleActionKNN:
    def __init__(self, k=3):
        # Load precomputed action embeddings
        with open(EMBEDDINGS_PATH, 'rb') as f:
            self.action_embeddings = pickle.load(f)  # {action_name: embedding}
        self.action_names = list(self.action_embeddings.keys())
        self.emb_matrix = np.stack([self.action_embeddings[name] for name in self.action_names])
        self.k = k
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def get_top_k(self, text: str) -> List[Tuple[str, float]]:
        """
        Given a user input string, return the top K most similar actions and their cosine similarity scores.
        Returns a list of (action_name, score), sorted by score descending.
        """
        query_emb = self.embedder.encode([text])[0]
        # Normalize for cosine similarity
        query_emb_norm = query_emb / np.linalg.norm(query_emb)
        emb_matrix_norm = self.emb_matrix / np.linalg.norm(self.emb_matrix, axis=1, keepdims=True)
        sims = np.dot(emb_matrix_norm, query_emb_norm)
        top_k_idx = np.argsort(sims)[::-1][:self.k]
        return [(self.action_names[i], float(sims[i])) for i in top_k_idx] 