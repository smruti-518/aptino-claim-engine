from src.claim_engine.agents.models import (
    AgentDecision,
    ClaimInput,
    Evidence,
)
from src.claim_engine.retrieval.bm25_retriever import BM25Retriever


class DocumentationAgent:
    """
    Checks whether the claim contains enough information
    for further claim assessment.
    """

    def __init__(self):
        self.retriever = BM25Retriever()

    def analyze(self, claim: ClaimInput) -> AgentDecision:
        query = (
            f"{claim.diagnosis} {claim.treatment} "
            "claim form bills receipts medical records documents"
        )

        retrieved = self.retriever.search(query, top_k=5)

        evidence = [
            Evidence(**item)
            for item in retrieved
        ]

        policy_citations = [
            item["chunk_id"]
            for item in retrieved
        ]

        missing_fields = []

        if claim.claimed_amount is None:
            missing_fields.append("claimed amount")

        if not claim.admission_date:
            missing_fields.append("admission date")

        if not claim.discharge_date:
            missing_fields.append("discharge date")

        if not claim.hospital_name:
            missing_fields.append("hospital name")

        key_findings = []
        applicable_limits = []
        missing_evidence = []

        if missing_fields:
            key_findings.append(
                "Required claim information is incomplete."
            )

            missing_evidence.extend(missing_fields)
            missing_evidence.extend(
                [
                    "Original bills and receipts.",
                    "Medical records and treatment notes.",
                    "Discharge summary, where applicable.",
                ]
            )

            return AgentDecision(
                agent_name="DocumentationAgent",
                decision="INSUFFICIENT_EVIDENCE",
                reasoning=(
                    "The following claim details are missing: "
                    + ", ".join(missing_fields)
                    + "."
                ),
                evidence=evidence,
                confidence=0.85,
                key_findings=key_findings,
                applicable_limits=applicable_limits,
                missing_evidence=missing_evidence,
                policy_citations=policy_citations,
            )

        key_findings.extend(
            [
                "Basic claim details are present.",
                "Supporting documents still require verification.",
            ]
        )

        missing_evidence.extend(
            [
                "Original bills and receipts.",
                "Medical records and treatment notes.",
                "Claim form and supporting certificates.",
                "Hospital admission and discharge records.",
            ]
        )

        return AgentDecision(
            agent_name="DocumentationAgent",
            decision="NEEDS_REVIEW",
            reasoning=(
                "Basic claim details are present. Original bills, receipts, "
                "medical records, and other supporting documents must still "
                "be verified."
            ),
            evidence=evidence,
            confidence=0.60,
            key_findings=key_findings,
            applicable_limits=applicable_limits,
            missing_evidence=missing_evidence,
            policy_citations=policy_citations,
        )