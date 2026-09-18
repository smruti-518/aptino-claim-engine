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
        self.model_name = model_name
        self.model = None
        self.chunks = self._load_chunks()
        self.embeddings = None

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

        return self.model

    def _load_embeddings(self):
        if self.embeddings is None:
            model = self._load_model()

            texts = [chunk["text"] for chunk in self.chunks]

            self.embeddings = model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

        return self.embeddings

    def _load_chunks(self):
        chunks = []

        with self.chunks_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    chunks.append(json.loads(line))

        return chunks

    def retrieve(self, query, top_k=5):
        model = self._load_model()
        embeddings = self._load_embeddings()

        query_embedding = model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        scores = np.dot(embeddings, query_embedding)
        ranked_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in ranked_indices:
            chunk = dict(self.chunks[index])
            chunk["score"] = float(scores[index])
            chunk["retrieval_method"] = "dense"
            results.append(chunk)

        return results