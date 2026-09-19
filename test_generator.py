import json
import os
from groq import Groq
from dotenv import load_dotenv
import time

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

TEST_CASE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "test_case_batch",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {
                                "type": "string",
                                "enum": ["success", "edge", "failure"],
                            },
                            "request": {
                                "type": "object",
                                "properties": {
                                    "path_params": {"type": "string"},
                                    "query_params": {"type": "string"},
                                    "body": {"type": "string"},
                                },
                                "required": ["path_params", "query_params", "body"],
                                "additionalProperties": False,
                            },
                            "expected_status": {"type": "integer"},
                        },
                        "required": ["name", "category", "request", "expected_status"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["test_cases"],
            "additionalProperties": False,
        },
    },
}

def _strip_noise(schema):
    if isinstance(schema, dict):
        return {k: _strip_noise(v) for k, v in schema.items() if k not in ("xml", "example")}
    if isinstance(schema, list):
        return [_strip_noise(item) for item in schema]
    return schema


def build_prompt(endpoint: dict) -> str:
    clean = {
        "method": endpoint["method"],
        "path": endpoint["path"],
        "summary": endpoint["summary"],
        "parameters": endpoint["parameters"],
        "request_body": _strip_noise(endpoint["request_body"]),
        "responses": _strip_noise(endpoint["responses"]),
    }
    return f"""You are generating API test cases for this endpoint:

{json.dumps(clean, indent=2)}

Generate 4-6 test cases covering:
- success: valid inputs that should succeed
- edge: boundary values, empty strings, minimum/maximum lengths or numbers, unusual-BUT-valid inputs. Each edge case must differ from every success case in at least one concrete value — do not repeat a success case under a different name.
- failure: invalid types, malformed input, or values that violate documented constraints (e.g. wrong type, value outside an enum).

IMPORTANT: path parameters (marked "in": "path") are part of the URL itself and
cannot be omitted - a request without one simply doesn't match this route, so
never generate a "missing path param" failure case. Instead, test path params
by substituting an INVALID VALUE (wrong type, e.g. a string where an integer
is expected, or a negative number where positive is expected).
Only body fields and query parameters can be tested as "missing" when optional
or required-but-absent.

For path_params, query_params, and body: output each as a JSON-encoded STRING
(e.g. "{{\\"petId\\": 5}}"), not a raw object. Use "{{}}" if there are no params,
and "" (empty string) for body if the endpoint takes no request body.
Give expected_status based on the endpoint's documented responses. Return ONLY a valie JSON arrayof test cases. DON'T include explanations, markdowns or code fences."""

def generate_tests_for_endpoint(endpoint: dict, max_retries: int = 3) -> list[dict]:
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": build_prompt(endpoint)}],
                response_format=TEST_CASE_SCHEMA,
                max_completion_tokens=2000,
            )
            parsed = json.loads(response.choices[0].message.content)
            test_cases = parsed["test_cases"]

            for tc in test_cases:
                tc["method"] = endpoint["method"]
                tc["path"] = endpoint["path"]
                req = tc["request"]
                req["path_params"] = json.loads(req["path_params"]) if req["path_params"] else {}
                req["query_params"] = json.loads(req["query_params"]) if req["query_params"] else {}
                req["body"] = json.loads(req["body"]) if req["body"] else None

            return test_cases

        except Exception as e:
            last_error = e
            print(f"  retry {attempt + 1}/{max_retries} for {endpoint['method']} {endpoint['path']}: {e}")
            time.sleep(1)

    # after exhausting retries, don't crash the whole batch - log and move on
    print(f"  GAVE UP on {endpoint['method']} {endpoint['path']}: {last_error}")
    return []

def generate_all_tests(endpoints: list[dict]) -> list[dict]:
    all_tests = []
    for ep in endpoints:
        tests = generate_tests_for_endpoint(ep)
        if not tests:
            print(f"  WARNING: 0 tests generated for {ep['method']} {ep['path']}")
        all_tests.extend(tests)
    return all_tests