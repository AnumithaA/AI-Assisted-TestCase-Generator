from spec_parser import load_spec, normalize_endpoints
from test_generator import generate_tests_for_endpoint
import json

spec = load_spec("data/petstore_swagger.json")
endpoints = normalize_endpoints(spec)

TARGET = {
    ("POST", "/pet"),
    ("GET", "/pet/{petId}"),
    ("PUT", "/pet"),
    ("DELETE", "/pet/{petId}")
}

target_endpoints = [
    e for e in endpoints
    if (e["method"], e["path"]) in TARGET
]

all_tests = []

for ep in target_endpoints:
    tests = generate_tests_for_endpoint(ep)
    all_tests.extend(tests)
    print(f"  {ep['method']} {ep['path']}: {len(tests)} tests generated")


# ADD THE BACKSTOP TESTS HERE
MANUAL_BACKSTOP_TESTS = [
    {
        "name": "Manual: nonexistent petId should 404",
        "category": "failure",
        "method": "GET",
        "path": "/pet/{petId}",
        "request": {
            "path_params": {"petId": 999999},
            "query_params": {},
            "body": None
        },
        "expected_status": 404,
    },
    {
        "name": "Manual: missing required fields should 400",
        "category": "failure",
        "method": "POST",
        "path": "/pet",
        "request": {
            "path_params": {},
            "query_params": {},
            "body": {}
        },
        "expected_status": 400,
    },
    {
        "name": "Manual: non-integer id should 400",
        "category": "failure",
        "method": "PUT",
        "path": "/pet",
        "request": {
            "path_params": {},
            "query_params": {},
            "body": {
                "id": "abc",
                "name": "Test",
                "photoUrls": []
            }
        },
        "expected_status": 400,
    },
    {
        "name": "Manual: delete existing pet should 200",
        "category": "success",
        "method": "DELETE",
        "path": "/pet/{petId}",
        "request": {
            "path_params": {"petId": 1},
            "query_params": {},
            "body": None
        },
        "expected_status": 200,
    },
]

all_tests.extend(MANUAL_BACKSTOP_TESTS)

print(
    f"Added {len(MANUAL_BACKSTOP_TESTS)} hand-authored "
    f"backstop tests (guarantee bug-registry coverage)"
)


with open("generated_tests.json", "w") as f:
    json.dump(all_tests, f, indent=2)

print(f"\nSaved {len(all_tests)} total test cases to generated_tests.json")