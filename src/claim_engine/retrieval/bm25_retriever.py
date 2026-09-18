from pathlib import Path
import json

from rank_bm25 import BM25Okapi


CHUNKS_PATH = Path("artifacts/policy_chunks.jsonl")


class BM25Retriever:
    def __init__(self, chunks_path: Path = CHUNKS_PATH):
        self.chunks = self._load_chunks(chunks_path)

        self.tokenized_corpus = [
            chunk["text"].lower().split()
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

    @staticmethod
    def _load_chunks(chunks_path: Path):
        if not chunks_path.exists():
            raise FileNotFoundError(
                f"Chunks file not found: {chunks_path}"
            )

        chunks = []

        with chunks_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    chunks.append(json.loads(line))

        if not chunks:
            raise ValueError("No policy chunks were found.")

        return chunks

    def search(self, query: str, top_k: int = 5):
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            result = dict(self.chunks[index])
            result["score"] = float(scores[index])
            result["retrieval_method"] = "bm25"
            results.append(result)

        return results


if __name__ == "__main__":
    retriever = BM25Retriever()

    results = retriever.search(
        "hospitalization room rent eligibility",
        top_k=3,
    )

    for result in results:
        print("\n--- RESULT ---")
        print("Chunk ID:", result["chunk_id"])
        print("Page:", result["page"])
        print("Section:", result["section"])
        print("Score:", result["score"])
        print("Retrieval method:", result["retrieval_method"])
        print("Text:", result["text"][:500])