import time

from src.claim_engine.agents.models import (
    AgentDecision,
    ClaimInput,
    FinalDecision,
)
from src.claim_engine.agents.coverage_agent import CoverageAgent
from src.claim_engine.agents.hospitalization_agent import HospitalizationAgent
from src.claim_engine.agents.documentation_agent import DocumentationAgent


class ClaimDecisionEngine:
    """
    Runs multiple specialized agents and combines their decisions.
    """

    def __init__(self):
        self.coverage_agent = CoverageAgent()
        self.hospitalization_agent = HospitalizationAgent()
        self.documentation_agent = DocumentationAgent()

    def analyze(self, claim: ClaimInput) -> FinalDecision:
        start_time = time.perf_counter()

        execution_trace = [
            "Received and validated claim input.",
            "Started CoverageAgent analysis.",
        ]

        coverage_decision = self.coverage_agent.analyze(claim)

        execution_trace.append(
            "CoverageAgent completed policy retrieval and coverage analysis. "
            f"Retrieved {len(coverage_decision.evidence)} policy chunks."
        )
        execution_trace.append(
            "Started HospitalizationAgent analysis."
        )

        hospitalization_decision = self.hospitalization_agent.analyze(claim)

        execution_trace.append(
            "HospitalizationAgent completed hospitalization analysis. "
            f"Retrieved {len(hospitalization_decision.evidence)} policy chunks."
        )
        execution_trace.append(
            "Started DocumentationAgent analysis."
        )

        documentation_decision = self.documentation_agent.analyze(claim)

        execution_trace.append(
            "DocumentationAgent completed documentation analysis. "
            f"Retrieved {len(documentation_decision.evidence)} policy chunks."
        )

        agent_decisions: list[AgentDecision] = [
            coverage_decision,
            hospitalization_decision,
            documentation_decision,
        ]

        decisions = [
            agent_decision.decision
            for agent_decision in agent_decisions
        ]

        if "INSUFFICIENT_EVIDENCE" in decisions:
            final_decision = "INSUFFICIENT_EVIDENCE"
            reasoning = (
                "The claim cannot be assessed because required claim "
                "information or policy evidence is missing."
            )
            abstention_reason = (
                "At least one specialized agent found insufficient evidence."
            )

        elif "NEEDS_REVIEW" in decisions:
            final_decision = "NEEDS_REVIEW"
            reasoning = (
                "The specialized agents found relevant policy information, "
                "but manual review is required before a final determination."
            )
            abstention_reason = (
                "The available evidence does not support a reliable "
                "automatic approval or rejection."
            )

        else:
            final_decision = "NEEDS_REVIEW"
            reasoning = (
                "No automatic approval or rejection rule was satisfied."
            )
            abstention_reason = (
                "The decision engine defaults to manual review."
            )

        confidence = round(
            sum(agent.confidence for agent in agent_decisions)
            / len(agent_decisions),
            3,
        )

        key_findings: list[str] = []
        applicable_limits: list[str] = []
        missing_evidence: list[str] = []

        for agent_decision in agent_decisions:
            if agent_decision.reasoning:
                key_findings.append(
                    f"{agent_decision.agent_name}: "
                    f"{agent_decision.reasoning}"
                )

            key_findings.extend(agent_decision.key_findings)
            applicable_limits.extend(agent_decision.applicable_limits)
            missing_evidence.extend(agent_decision.missing_evidence)

        citations = sorted(
            {
                evidence.chunk_id
                for agent_decision in agent_decisions
                for evidence in agent_decision.evidence
            }
        )

        execution_trace.append(
            "Aggregated specialized-agent decisions."
        )

        elapsed_seconds = time.perf_counter() - start_time

        execution_trace.append(
            "Validation status: input validated successfully."
        )
        execution_trace.append(
            f"Elapsed analysis time: {elapsed_seconds:.3f} seconds."
        )

        execution_trace.append(
            f"Final decision generated: {final_decision}."
        )

        return FinalDecision(
            claim_id=claim.claim_id,
            decision=final_decision,
            reasoning=reasoning,
            confidence=confidence,
            key_findings=key_findings,
            applicable_limits=sorted(set(applicable_limits)),
            missing_evidence=sorted(set(missing_evidence)),
            agent_decisions=agent_decisions,
            citations=citations,
            policy_citations=citations,
            execution_trace=execution_trace,
            abstention_reason=abstention_reason,
        )