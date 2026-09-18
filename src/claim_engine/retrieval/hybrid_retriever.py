from src.claim_engine.retrieval.bm25_retriever import BM25Retriever


class HybridRetriever:
    """
    Lightweight hybrid retriever for deployment.

    Uses BM25 retrieval as the primary policy search method.
    This avoids loading large sentence-transformer and cross-encoder
    models on low-memory deployment instances.
    """

    def __init__(self):
        self.bm25 = BM25Retriever()

    def retrieve(self, query, top_k=5):
        results = self.bm25.search(query, top_k=top_k)

        for rank, result in enumerate(results, start=1):
            result["bm25_rank"] = rank
            result["dense_rank"] = None

            result["hybrid_score"] = 1 / (60 + rank)
            result["retrieval_method"] = "hybrid"

            # Keep the existing BM25 score available.
            result.setdefault("score", 0.0)

        return results