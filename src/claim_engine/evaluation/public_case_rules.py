from datetime import date
from typing import Any


INITIAL_WAITING_DAYS = 30
PRE_EXISTING_WAITING_MONTHS = 48
DOMICILIARY_SUBLIMIT_PERCENT = 20


def days_between(start_date: str, end_date: str) -> int:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    return (end - start).days


def months_between(start_date: str, end_date: str) -> int:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    return (
        (end.year - start.year) * 12
        + end.month
        - start.month
    )


def evaluate_public_case(case: dict[str, Any]) -> dict[str, Any]:
    treatment = case.get("treatment", {})
    evidence_context = case.get("evidence_context") or {}

    policy_start = case["policy_start_date"]
    claim_date = case["claim_date"]

    coverage_months = case.get("continuous_coverage_months", 0)
    prior_coverage_years = case.get("prior_insurer_continuous_years", 0)
    prior_coverage_months = prior_coverage_years * 12

    elapsed_days = days_between(policy_start, claim_date)
    elapsed_months = months_between(policy_start, claim_date)

    effective_coverage_months = (
        coverage_months + prior_coverage_months
    )

    reasons = []
    required_checks = []
    decision = "NEEDS_REVIEW"

    treatment_type = treatment.get("type")
    admission_hours = treatment.get("admission_hours", 0)
    pre_existing = treatment.get("pre_existing", False)
    experimental = treatment.get("experimental", False)

    has_qualifying_previous_coverage = prior_coverage_years > 0

    # Initial waiting period: 30 days.
    if (
        elapsed_days < INITIAL_WAITING_DAYS
        and not has_qualifying_previous_coverage
    ):
        decision = "REJECT"
        reasons.append(
            "The claim date falls within the initial 30-day waiting period."
        )

    # Pre-existing disease waiting period: 48 months,
    # reduced by qualifying previous continuous coverage.
    elif (
        pre_existing
        and effective_coverage_months < PRE_EXISTING_WAITING_MONTHS
    ):
        decision = "REJECT"
        reasons.append(
            "The condition is marked pre-existing and the effective "
            "continuous coverage period is below 48 months."
        )

    # Experimental treatment exclusion.
    elif experimental:
        decision = "REJECT"
        reasons.append(
            "The treatment is marked as experimental. Verify the policy's "
            "experimental-treatment exclusion."
        )

    # Inpatient hospitalization.
    elif treatment_type == "inpatient":
        if admission_hours < 24:
            decision = "NEEDS_REVIEW"
            reasons.append(
                "The admission is below 24 hours. Verify whether the "
                "procedure qualifies as listed day-care treatment."
            )
        else:
            decision = "NEEDS_REVIEW"
            reasons.append(
                "The inpatient treatment satisfies the 24-hour threshold, "
                "but admissibility, medical necessity, and expense limits "
                "require verification."
            )

    # Day-care treatment.
    elif treatment_type == "day_care":
        decision = "NEEDS_REVIEW"
        reasons.append(
            "Verify that the procedure is a listed eligible day-care "
            "procedure and is not ordinary outpatient treatment."
        )

    # Domiciliary treatment.
    elif treatment_type == "domiciliary":
        hospital_room_unavailable = (
            treatment.get("hospital_room_unavailable") is True
        )
        patient_cannot_be_moved = (
            treatment.get("patient_cannot_be_moved") is True
        )

        if hospital_room_unavailable or patient_cannot_be_moved:
            decision = "NEEDS_REVIEW"
            reasons.append(
                "The claim describes domiciliary treatment. Verify the "
                "medical evidence, medical necessity, applicable policy "
                "limits, and supporting documents before determining "
                "the payable amount."
            )
        else:
            decision = "REJECT"
            reasons.append(
                "The required domiciliary-treatment conditions have not "
                "been established."
            )

    else:
        decision = "NEEDS_REVIEW"
        reasons.append(
            "Treatment type is not recognized and requires manual review."
        )

    # Missing evidence should not override a clear rejection.
    if evidence_context.get("hospital_registered") is None:
        required_checks.append("Confirm hospital registration.")

    if evidence_context.get("medical_necessity_confirmed") is None:
        required_checks.append("Confirm medical necessity.")

    if required_checks and decision != "REJECT":
        decision = "NEEDS_REVIEW"

    return {
        "case_id": case["case_id"],
        "decision": decision,
        "reasons": reasons,
        "required_checks": required_checks,
        "elapsed_policy_days": elapsed_days,
        "elapsed_policy_months": elapsed_months,
        "coverage_months": coverage_months,
        "prior_coverage_months": prior_coverage_months,
        "effective_coverage_months": effective_coverage_months,
        "domiciliary_sublimit_percent": DOMICILIARY_SUBLIMIT_PERCENT,
        "domiciliary_sublimit_amount_inr": None,
    }