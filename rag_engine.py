from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = []
        self.index = None

    def build_index(self, triples):
        corpus = [f"{s} {r} {o}" for s, r, o in triples]
        embeddings = self.model.encode(corpus)

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))
        self.texts = corpus

    def query(self, question):
        q_embed = self.model.encode([question])
        D, I = self.index.search(np.array(q_embed), k=3)
        return [self.texts[i] for i in I[0]]