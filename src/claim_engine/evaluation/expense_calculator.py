from typing import Any


DOMICILIARY_SUBLIMIT_PERCENT = 20


def calculate_expenses(
    case: dict[str, Any],
) -> dict[str, Any]:
    treatment = case.get("treatment", {})
    expenses = case.get("expenses_inr", {})

    room = expenses.get("room", 0)
    doctor_fees = expenses.get("doctor_fees", 0)
    medicines_diagnostics = expenses.get("medicines_diagnostics", 0)
    pre_hospitalization = expenses.get("pre_hospitalization", 0)
    post_hospitalization = expenses.get("post_hospitalization", 0)
    ambulance = expenses.get("ambulance", 0)

    total_claimed = sum(
        [
            room,
            doctor_fees,
            medicines_diagnostics,
            pre_hospitalization,
            post_hospitalization,
            ambulance,
        ]
    )

    domiciliary_sublimit_percent = None
    domiciliary_sublimit_amount = None

    if treatment.get("type") == "domiciliary":
        sum_insured = case.get("sum_insured_inr")

        if sum_insured is not None and sum_insured > 0:
            domiciliary_sublimit_percent = (
                DOMICILIARY_SUBLIMIT_PERCENT
            )
            domiciliary_sublimit_amount = (
                sum_insured
                * domiciliary_sublimit_percent
                / 100
            )

    return {
        "total_claimed_inr": total_claimed,
        "expense_breakdown_inr": {
            "room": room,
            "doctor_fees": doctor_fees,
            "medicines_diagnostics": medicines_diagnostics,
            "pre_hospitalization": pre_hospitalization,
            "post_hospitalization": post_hospitalization,
            "ambulance": ambulance,
        },
        "domiciliary_sublimit_percent": domiciliary_sublimit_percent,
        "domiciliary_sublimit_amount_inr": domiciliary_sublimit_amount,
        "provisional_payable_inr": None,
        "deductions_inr": None,
        "note": (
            "This is an expense summary only. Final payable amount and "
            "deductions require verification of policy limits, admissibility, "
            "documents, and medical evidence."
        ),
    }