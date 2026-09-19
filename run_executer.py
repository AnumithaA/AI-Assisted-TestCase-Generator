# run_executor.py
from executer import run_all_tests  # matches the renamed executor.py from Step 0
from scorer import score
import json

with open("generated_tests.json") as f:
    all_tests = json.load(f)

print(f"Loaded {len(all_tests)} test cases, running against demo API...\n")
results = run_all_tests(all_tests)

for r in results:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"[{status}] {r['method']} {r['path']} — {r['name']}")
    print(f"    expected {r['expected_status']}, got {r['actual_status']}")
    if r["note"]:
        print(f"    note: {r['note']}")
    print()

report = {"results": results, "score": score(results)}
with open("results.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n========== SCORE REPORT ==========")
print(json.dumps(report["score"], indent=2))
print("\nSaved full report to results.json")