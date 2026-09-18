from src.claim_engine.agents.models import (
    AgentDecision,
    ClaimInput,
    Evidence,
)
from src.claim_engine.retrieval.bm25_retriever import BM25Retriever


class HospitalizationAgent:
    """
    Checks whether the claim contains sufficient information
    about hospitalization requirements.
    """

    def __init__(self):
        self.retriever = BM25Retriever()

    def analyze(self, claim: ClaimInput) -> AgentDecision:
        query = (
            f"{claim.diagnosis} {claim.treatment} "
            "hospitalization minimum 24 hours inpatient care"
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

        combined_text = " ".join(
            item["text"].lower()
            for item in retrieved
        )

        hospitalization_found = (
            "hospitalization" in combined_text
            or "in-patient" in combined_text
            or "inpatient" in combined_text
        )

        applicable_limits = []
        missing_evidence = [
            "Confirm admission and discharge dates.",
            "Verify the actual duration of hospitalization.",
            "Obtain admission records, discharge summary, and treatment notes.",
        ]

        key_findings = [
            "Hospitalization-related policy evidence was retrieved.",
        ]

        if "24 hours" in combined_text or "24 consecutive hours" in combined_text:
            applicable_limits.append(
                "Hospitalization generally requires a minimum stay of "
                "24 consecutive hours, subject to policy exceptions."
            )

            key_findings.append(
                "Retrieved policy evidence refers to a 24-hour "
                "hospitalization requirement."
            )

        if not hospitalization_found:
            return AgentDecision(
                agent_name="HospitalizationAgent",
                decision="INSUFFICIENT_EVIDENCE",
                reasoning=(
                    "The retrieved policy evidence does not clearly establish "
                    "the hospitalization requirements."
                ),
                evidence=evidence,
                confidence=0.25,
                key_findings=key_findings,
                applicable_limits=applicable_limits,
                missing_evidence=missing_evidence,
                policy_citations=policy_citations,
            )

        if claim.treatment and "hospital" in claim.treatment.lower():
            key_findings.append(
                "The treatment description mentions hospital-based care."
            )

            return AgentDecision(
                agent_name="HospitalizationAgent",
                decision="NEEDS_REVIEW",
                reasoning=(
                    "The claim mentions hospital treatment, and relevant "
                    "hospitalization policy evidence was found. Admission "
                    "duration and supporting documents must be verified."
                ),
                evidence=evidence,
                confidence=0.60,
                key_findings=key_findings,
                applicable_limits=applicable_limits,
                missing_evidence=missing_evidence,
                policy_citations=policy_citations,
            )

        key_findings.append(
            "The treatment description does not clearly establish "
            "inpatient hospitalization."
        )

        return AgentDecision(
            agent_name="HospitalizationAgent",
            decision="NEEDS_REVIEW",
            reasoning=(
                "Hospitalization-related policy evidence was found, but "
                "the claim details are insufficient for a final decision."
            ),
            evidence=evidence,
            confidence=0.45,
            key_findings=key_findings,
            applicable_limits=applicable_limits,
            missing_evidence=missing_evidence,
            policy_citations=policy_citations,
        )