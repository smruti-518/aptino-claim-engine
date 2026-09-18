import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.claim_engine.evaluation.public_case_rules import evaluate_public_case
from src.claim_engine.evaluation.expense_calculator import calculate_expenses


PUBLIC_CASES_PATH = PROJECT_ROOT / "data/claims/public_test_cases.json"
ADDITIONAL_CASES_PATH = (
    PROJECT_ROOT / "data/additional_cases/additional_test_cases.json"
)
OUTPUT_PATH = PROJECT_ROOT / "artifacts/evaluation_results.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    public_cases = load_json(PUBLIC_CASES_PATH)
    additional_cases = load_json(ADDITIONAL_CASES_PATH)

    test_cases = public_cases + additional_cases
    results = []

    print(f"Loaded {len(public_cases)} public cases.")
    print(f"Loaded {len(additional_cases)} additional cases.")
    print(f"Total cases: {len(test_cases)}\n")

    for index, case in enumerate(test_cases, start=1):
        case_id = case.get("case_id", "UNKNOWN")

        try:
            result = evaluate_public_case(case)
            result["expense_summary"] = calculate_expenses(case)
            results.append(result)

            reasons = "; ".join(result.get("reasons", []))

            print(
                f"{index}. {case_id}: "
                f"{result['decision']} — {reasons}"
            )

        except Exception as error:
            error_result = {
                "case_id": case_id,
                "decision": "ERROR",
                "reasons": [str(error)],
                "required_checks": [],
            }

            results.append(error_result)
            print(f"{index}. {case_id}: ERROR: {error}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"\nSaved results to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()