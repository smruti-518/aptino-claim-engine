from sentence_transformers import CrossEncoder


class PolicyReranker:
    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = CrossEncoder(self.model_name)

        return self.model

    def rerank(self, query, results, top_k=5):
        if not results:
            return []

        model = self._load_model()

        pairs = [
            (query, result["text"])
            for result in results
        ]

        scores = model.predict(pairs)

        reranked = []

        for result, score in zip(results, scores):
            updated_result = dict(result)
            updated_result["rerank_score"] = float(score)
            reranked.append(updated_result)

        reranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return reranked[:top_k]