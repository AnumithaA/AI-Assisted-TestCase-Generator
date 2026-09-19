import requests

DEMO_BASE = "http://127.0.0.1:5000"

# only these method+path combos exist on the demo API
RUNNABLE_ENDPOINTS = {
    ("POST", "/pet"),
    ("GET", "/pet/{petId}"),
    ("PUT", "/pet"),
    ("DELETE", "/pet/{petId}"),
}


def _build_url(path: str, path_params: dict) -> str:
    """Substitute {paramName} placeholders in the path with actual values."""
    url = path
    for key, value in path_params.items():
        url = url.replace(f"{{{key}}}", str(value))
    return DEMO_BASE + url


def run_test(test_case: dict) -> dict:
    method = test_case["method"]
    path = test_case["path"]

    if (method, path) not in RUNNABLE_ENDPOINTS:
        return {
            **test_case,
            "executed": False,
            "actual_status": None,
            "passed": None,
            "note": "skipped: no matching demo endpoint",
        }

    req = test_case["request"]
    url = _build_url(path, req["path_params"])

    try:
        response = requests.request(
            method=method,
            url=url,
            params=req["query_params"] or None,
            json=req["body"] if req["body"] else None,
            timeout=5,
        )
        actual_status = response.status_code
        passed = actual_status == test_case["expected_status"]

        return {
            **test_case,
            "executed": True,
            "actual_status": actual_status,
            "passed": passed,
            "note": None,
        }

    except requests.RequestException as e:
        return {
            **test_case,
            "executed": True,
            "actual_status": None,
            "passed": False,
            "note": f"request error: {e}",
        }


def run_all_tests(test_cases: list[dict]) -> list[dict]:
    return [run_test(tc) for tc in test_cases]