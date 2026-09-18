import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.claim_engine.evaluation.public_case_rules import evaluate_public_case
from src.claim_engine.evaluation.expense_calculator import calculate_expenses

def make_case(**overrides):
    case = {
        "case_id": "TEST-001",
        "policy_start_date": "2026-01-01",
        "claim_date": "2026-03-15",
        "continuous_coverage_months": 2,
        "prior_insurer_continuous_years": 0,
        "patient": {"age": 40},
        "hospital": {"name": "Test Hospital"},
        "treatment": {
            "type": "inpatient",
            "admission_hours": 48,
            "pre_existing": False,
            "experimental": False,
        },
        "expenses_inr": {},
        "documents": [],
    }

    case.update(overrides)
    return case


def test_initial_waiting_period():
    case = make_case(
        claim_date="2026-01-15",
    )

    result = evaluate_public_case(case)

    assert result["decision"] == "REJECT"
    assert "30-day waiting period" in result["reasons"][0]


def test_inpatient_claim_requires_review():
    case = make_case()

    result = evaluate_public_case(case)

    assert result["decision"] == "NEEDS_REVIEW"


def test_experimental_treatment_is_rejected():
    case = make_case(
        treatment={
            "type": "inpatient",
            "admission_hours": 48,
            "pre_existing": False,
            "experimental": True,
        }
    )

    result = evaluate_public_case(case)

    assert result["decision"] == "REJECT"


def test_domiciliary_treatment_requires_review():
    case = make_case(
        treatment={
            "type": "domiciliary",
            "admission_hours": 0,
            "pre_existing": False,
            "experimental": False,
            "hospital_room_unavailable": True,
            "patient_cannot_be_moved": False,
        }
    )

    result = evaluate_public_case(case)

    assert result["decision"] == "NEEDS_REVIEW"
    assert result["domiciliary_sublimit_percent"] == 20


def test_day_care_requires_review():
    case = make_case(
        treatment={
            "type": "day_care",
            "admission_hours": 8,
            "pre_existing": False,
            "experimental": False,
        }
    )

    result = evaluate_public_case(case)

    assert result["decision"] == "NEEDS_REVIEW"
    

def test_expense_calculator_totals_claimed_amount():
    case = {
        "treatment": {"type": "inpatient"},
        "expenses_inr": {
            "room": 10000,
            "doctor_fees": 20000,
            "medicines_diagnostics": 30000,
            "pre_hospitalization": 5000,
            "post_hospitalization": 7000,
            "ambulance": 1000,
        },
    }

    result = calculate_expenses(case)

    assert result["total_claimed_inr"] == 73000


def test_expense_calculator_domiciliary_sublimit():
    case = {
        "sum_insured_inr": 500000,
        "treatment": {"type": "domiciliary"},
        "expenses_inr": {
            "doctor_fees": 25000,
            "medicines_diagnostics": 80000,
        },
    }

    result = calculate_expenses(case)

    assert result["domiciliary_sublimit_percent"] == 20
    assert result["domiciliary_sublimit_amount_inr"] == 100000


def test_expense_calculator_non_domiciliary_has_no_sublimit():
    case = {
        "sum_insured_inr": 500000,
        "treatment": {"type": "inpatient"},
        "expenses_inr": {
            "room": 10000,
        },
    }

    result = calculate_expenses(case)

    assert result["domiciliary_sublimit_percent"] is None
    assert result["domiciliary_sublimit_amount_inr"] is None