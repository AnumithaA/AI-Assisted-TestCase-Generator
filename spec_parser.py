# spec_parser.py
import json
import yaml
from pathlib import Path

def load_spec(file_path: str) -> dict:
    """Load an OpenAPI/Swagger spec from a .json or .yaml/.yml file."""
    path = Path(file_path)
    with open(path, "r") as f:
        if path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        return json.load(f)


def normalize_endpoints(spec: dict) -> list[dict]:
    """
    Flatten an OpenAPI spec into a list of simple endpoint dicts:
    {method, path, summary, parameters, request_body, responses}
    """
    endpoints = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue  # skip non-HTTP keys like 'parameters' at path level

            endpoint = {
                "method": method.upper(),
                "path": path,
                "summary": details.get("summary", ""),
                "parameters": _extract_parameters(details),
                "request_body": _extract_request_body(details),
                "responses": _extract_responses(details),
            }
            endpoints.append(endpoint)

    return endpoints


def _extract_parameters(details: dict) -> list[dict]:
    params = []
    for p in details.get("parameters", []):
        params.append({
            "name": p.get("name"),
            "in": p.get("in"),          # query, path, header
            "required": p.get("required", False),
            "type": p.get("schema", {}).get("type", "string"),
        })
    return params


def _extract_request_body(details: dict) -> dict | None:
    body = details.get("requestBody")
    if not body:
        return None
    content = body.get("content", {})
    json_schema = content.get("application/json", {}).get("schema", {})
    return json_schema or None


def _extract_responses(details: dict) -> dict:
    responses = {}
    for code, info in details.get("responses", {}).items():
        content = info.get("content", {})
        schema = content.get("application/json", {}).get("schema", {})
        responses[code] = schema
    return responses