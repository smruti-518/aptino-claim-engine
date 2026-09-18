from pathlib import Path
import json

import numpy as np
from sentence_transformers import SentenceTransformer


class DenseRetriever:
    def __init__(
        self,
        chunks_path="artifacts/policy_chunks.jsonl",
        model_name="all-MiniLM-L6-v2",
    ):
        self.chunks_path = Path(chunks_path)
        self.model = SentenceTransformer(model_name)
        self.chunks = self._load_chunks()

        texts = [chunk["text"] for chunk in self.chunks]
        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def _load_chunks(self):
        chunks = []

        with self.chunks_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    chunks.append(json.loads(line))

        return chunks

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        scores = np.dot(self.embeddings, query_embedding)
        ranked_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in ranked_indices:
            chunk = dict(self.chunks[index])
            chunk["score"] = float(scores[index])
            chunk["retrieval_method"] = "dense"
            results.append(chunk)

        return results