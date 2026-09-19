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

def resolve_refs(node, components: dict, _seen: set | None = None):
    """
    Recursively resolve $ref pointers against spec['components']['schemas'].
    _seen tracks refs currently being resolved in this branch, to avoid
    infinite recursion on circular schemas (replaced with a placeholder instead).
    """
    if _seen is None:
        _seen = set()

    if isinstance(node, dict):
        if "$ref" in node:
            ref_path = node["$ref"]  # e.g. "#/components/schemas/Pet"
            schema_name = ref_path.split("/")[-1]

            if schema_name in _seen:
                return {"type": "object", "note": f"circular ref to {schema_name}"}

            schema = components.get(schema_name)
            if schema is None:
                return {"type": "object", "note": f"unresolved ref {schema_name}"}

            return resolve_refs(schema, components, _seen | {schema_name})

        return {k: resolve_refs(v, components, _seen) for k, v in node.items()}

    if isinstance(node, list):
        return [resolve_refs(item, components, _seen) for item in node]

    return node

def normalize_endpoints(spec: dict) -> list[dict]:
    components = spec.get("components", {}).get("schemas", {})
    endpoints = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue

            endpoint = {
                "method": method.upper(),
                "path": path,
                "summary": details.get("summary", ""),
                "parameters": _extract_parameters(details),
                "request_body": resolve_refs(_extract_request_body(details), components),
                "responses": resolve_refs(_extract_responses(details), components),
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