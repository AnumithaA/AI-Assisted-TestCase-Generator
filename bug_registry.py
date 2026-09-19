# bug_registry.py
BUGS = [
    {
        "id": "BUG-1",
        "endpoint": "POST /pet",
        "description": "Missing required-field validation (name, photoUrls)",
        "correct_behavior": "Request missing 'name' or 'photoUrls' should return 400",
        "actual_behavior": "Silently accepts and returns 200",
        "matches": lambda r: (
            r["method"] == "POST" and r["path"] == "/pet"
            and r["category"] == "failure"
            and (not isinstance(r["request"]["body"], dict)
                 or not r["request"]["body"].get("name")
                 or not r["request"]["body"].get("photoUrls"))
            and r["expected_status"] == 400
            and r["actual_status"] == 200
        ),
    },
    {
        "id": "BUG-2",
        "endpoint": "GET /pet/{petId}",
        "description": "Wrong status code for nonexistent pet",
        "correct_behavior": "Nonexistent petId should return 404",
        "actual_behavior": "Returns 200 with a null body",
        "matches": lambda r: (
            r["method"] == "GET" and r["path"] == "/pet/{petId}"
            and r["expected_status"] == 404
            and r["actual_status"] == 200
        ),
    },
    {
        "id": "BUG-3",
        "endpoint": "PUT /pet",
        "description": "No type validation on 'id' field",
        "correct_behavior": "Non-integer id should return 400",
        "actual_behavior": "Returns 200 with no actual update performed",
        "matches": lambda r: (
            r["method"] == "PUT" and r["path"] == "/pet"
            and isinstance(r["request"]["body"], dict)
            and "id" in r["request"]["body"]
            and not isinstance(r["request"]["body"]["id"], int)
            and r["expected_status"] in (400, 422)
            and r["actual_status"] == 200
        ),
    },
    {
        "id": "BUG-4",
        "endpoint": "DELETE /pet/{petId}",
        "description": "Type mismatch \u2014 path param compared as string vs int keys",
        "correct_behavior": "Deleting an existing petId should return 200",
        "actual_behavior": "Returns 404 even for pets that exist",
        "matches": lambda r: (
            r["method"] == "DELETE" and r["path"] == "/pet/{petId}"
            and r["expected_status"] == 200
            and r["actual_status"] == 404
        ),
    },
]