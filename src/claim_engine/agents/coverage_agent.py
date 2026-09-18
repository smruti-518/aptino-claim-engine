from src.claim_engine.agents.models import AgentDecision, ClaimInput
from src.claim_engine.retrieval.hybrid_retriever import HybridRetriever


class CoverageAgent:
    def __init__(self):
        self.retriever = HybridRetriever()

    def analyze(self, claim: ClaimInput) -> AgentDecision:
        query = (
            f"diagnosis: {claim.diagnosis}; "
            f"treatment: {claim.treatment}; "
            f"notes: {claim.notes or ''}"
        )

        retrieved_chunks = self.retriever.retrieve(
            query,
            top_k=3,
        )

        evidence_text = " ".join(
            chunk["text"].lower()
            for chunk in retrieved_chunks
        )

        exclusion_terms = [
            "experimental",
            "cosmetic",
            "self-inflicted",
            "alcohol",
        ]

        matched_exclusions = [
            term
            for term in exclusion_terms
            if term in evidence_text
        ]

        evidence = []

        for chunk in retrieved_chunks:
            evidence.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk["page"],
                    "section": chunk["section"],
                    "text": chunk["text"],
                    "score": float(
                        chunk.get("rerank_score")
                        or chunk.get("hybrid_score")
                        or chunk.get("score")
                        or 0.0
                    ),
                }
            )

        policy_citations = [
            chunk["chunk_id"]
            for chunk in retrieved_chunks
        ]

        key_findings = [
            "Policy evidence was retrieved and reranked.",
            f"Diagnosis considered: {claim.diagnosis}.",
            f"Treatment considered: {claim.treatment}.",
        ]

        applicable_limits = []
        missing_evidence = []

        if matched_exclusions:
            reasoning = (
                "Potential policy exclusion found in retrieved evidence: "
                + ", ".join(matched_exclusions)
                + "."
            )

            key_findings.append(
                "Potential exclusion terms found: "
                + ", ".join(matched_exclusions)
                + "."
            )

            missing_evidence.extend(
                [
                    "Confirm whether the identified exclusion applies "
                    "to the actual treatment.",
                    "Obtain supporting clinical documentation and diagnosis "
                    "details.",
                ]
            )
        else:
            reasoning = (
                "Retrieved and reranked policy evidence for coverage "
                "assessment. Coverage eligibility and exclusions require "
                "verification."
            )

            key_findings.append(
                "No direct exclusion was conclusively established by "
                "the retrieved evidence."
            )

            missing_evidence.extend(
                [
                    "Verify policy eligibility and coverage status.",
                    "Verify whether any specific exclusion or waiting "
                    "period applies.",
                ]
            )

        return AgentDecision(
            agent_name="CoverageAgent",
            decision="NEEDS_REVIEW",
            confidence=0.65 if matched_exclusions else 0.55,
            reasoning=reasoning,
            evidence=evidence,
            key_findings=key_findings,
            applicable_limits=applicable_limits,
            missing_evidence=missing_evidence,
            policy_citations=policy_citations,
        )