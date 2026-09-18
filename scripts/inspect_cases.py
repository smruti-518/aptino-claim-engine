import json
from pathlib import Path


path = Path("data/claims/public_test_cases.json")

with path.open("r", encoding="utf-8") as file:
    cases = json.load(file)

for case in cases:
    print("=" * 80)
    print("CASE:", case.get("case_id"))

    print("\nTOP-LEVEL KEYS:")
    print(list(case.keys()))

    print("\nFULL CASE:")
    print(json.dumps(case, indent=2))

    print()