from src.claim_engine.retrieval.bm25_retriever import BM25Retriever
from src.claim_engine.retrieval.dense_retriever import DenseRetriever
from src.claim_engine.retrieval.reranker import PolicyReranker


class HybridRetriever:
    def __init__(self):
        self.bm25 = BM25Retriever()
        self.dense = DenseRetriever()
        self.reranker = PolicyReranker()

    def retrieve(self, query, top_k=5):
        bm25_results = self.bm25.search(query, top_k=top_k)
        dense_results = self.dense.retrieve(query, top_k=top_k)

        combined = {}

        for rank, result in enumerate(bm25_results, start=1):
            chunk_id = result["chunk_id"]

            combined.setdefault(
                chunk_id,
                {
                    **result,
                    "bm25_rank": None,
                    "dense_rank": None,
                },
            )

            combined[chunk_id]["bm25_rank"] = rank

        for rank, result in enumerate(dense_results, start=1):
            chunk_id = result["chunk_id"]

            combined.setdefault(
                chunk_id,
                {
                    **result,
                    "bm25_rank": None,
                    "dense_rank": None,
                },
            )

            combined[chunk_id]["dense_rank"] = rank

        for result in combined.values():
            hybrid_score = 0.0

            if result["bm25_rank"] is not None:
                hybrid_score += 1 / (60 + result["bm25_rank"])

            if result["dense_rank"] is not None:
                hybrid_score += 1 / (60 + result["dense_rank"])

            result["hybrid_score"] = hybrid_score
            result["retrieval_method"] = "hybrid"

        fused_results = sorted(
            combined.values(),
            key=lambda item: item["hybrid_score"],
            reverse=True,
        )

        rerank_candidates = fused_results[: max(top_k * 2, 10)]

        return self.reranker.rerank(
            query,
            rerank_candidates,
            top_k=top_k,
        )