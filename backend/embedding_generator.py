from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle
from backend.config import EMBEDDING_MODEL_NAME, VECTOR_DB_PATH, CHUNKS_STORE_PATH

class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.chunks = []  

    def generate_embeddings(self, texts):
        return np.array(self.model.encode(texts))

    def create_vector_store(self, texts):
        embeddings = self.generate_embeddings(texts)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        faiss.write_index(self.index, VECTOR_DB_PATH)

        self.chunks = texts
        with open(CHUNKS_STORE_PATH, "wb") as f:
            pickle.dump(self.chunks, f)

        return embeddings

    def load_vector_store(self):
        if os.path.exists(VECTOR_DB_PATH):
            self.index = faiss.read_index(VECTOR_DB_PATH)
        if os.path.exists(CHUNKS_STORE_PATH):
            with open(CHUNKS_STORE_PATH, "rb") as f:
                self.chunks = pickle.load(f)

    def search_similar_chunks(self, query, k=5):
        if not self.index:
            raise ValueError("❌ Vector store not loaded. Run create_vector_store() or load_vector_store().")

        query_embedding = self.generate_embeddings([query])
        distances, indices = self.index.search(query_embedding, k=k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append({"chunk": self.chunks[idx], "distance": float(distances[0][i])})
        return results
