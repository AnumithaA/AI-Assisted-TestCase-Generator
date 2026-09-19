# scorer.py
import json
from difflib import SequenceMatcher
from bug_registry import BUGS


def compute_correctness_rate(results: list[dict]) -> dict:
    executed = [r for r in results if r["executed"]]
    if not executed:
        return {"total": 0, "passed": 0, "rate": None}
    passed = sum(1 for r in executed if r["passed"])
    return {"total": len(executed), "passed": passed, "rate": round(passed / len(executed), 3)}


def compute_bug_catch_rate(results: list[dict]) -> dict:
    caught, missed = [], []
    for bug in BUGS:
        matching = [r for r in results if r["executed"] and bug["matches"](r)]
        clean_bug = {k: v for k, v in bug.items() if k != "matches"}
        if matching:
            caught.append({**clean_bug, "caught_by": [r["name"] for r in matching]})
        else:
            missed.append(clean_bug)
    return {
        "total_bugs": len(BUGS),
        "caught": len(caught),
        "rate": round(len(caught) / len(BUGS), 3),
        "caught_details": caught,
        "missed": missed,
    }


def _similarity(a: dict, b: dict) -> float:
    a_str = json.dumps(a["request"], sort_keys=True)
    b_str = json.dumps(b["request"], sort_keys=True)
    return SequenceMatcher(None, a_str, b_str).ratio()


def compute_redundancy(test_cases: list[dict], threshold: float = 0.85) -> list[dict]:
    flagged = []
    by_group = {}
    for tc in test_cases:
        key = (tc["method"], tc["path"], tc["category"])
        by_group.setdefault(key, []).append(tc)
    for key, group in by_group.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sim = _similarity(group[i], group[j])
                if sim >= threshold:
                    flagged.append({
                        "endpoint": f"{key[0]} {key[1]}", "category": key[2],
                        "test_a": group[i]["name"], "test_b": group[j]["name"],
                        "similarity": round(sim, 3),
                    })
    return flagged


def score(results: list[dict]) -> dict:
    return {
        "correctness": compute_correctness_rate(results),
        "bug_catch": compute_bug_catch_rate(results),
        "redundancy": compute_redundancy(results),
    }