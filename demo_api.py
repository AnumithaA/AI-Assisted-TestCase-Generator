from flask import Flask, request, jsonify

app = Flask(__name__)

# in-memory store: {petId: {name, photoUrls, ...}}
pets = {
    1: {"id": 1, "name": "Buddy", "photoUrls": ["http://example.com/buddy.jpg"]},
    2: {"id": 2, "name": "Milo", "photoUrls": ["http://example.com/milo.jpg"]},
}
next_id = 3


@app.route("/pet", methods=["POST"])
def create_pet():
    """
    BUG #1: doesn't validate required fields (name, photoUrls).
    Spec says both are required — a request missing either should 400.
    This implementation silently accepts and creates the pet anyway.
    """
    global next_id
    data = request.get_json() or {}

    # --- BUG: no validation here, should check "name" and "photoUrls" exist ---
    pet = {
        "id": next_id,
        "name": data.get("name"),
        "photoUrls": data.get("photoUrls"),
    }
    pets[next_id] = pet
    next_id += 1
    return jsonify(pet), 200


@app.route("/pet/<pet_id>", methods=["GET"])
def get_pet(pet_id):
    """
    BUG #2: returns 200 with a null body for a nonexistent pet,
    instead of the documented 404.
    """
    pet = pets.get(int(pet_id)) if pet_id.isdigit() else None

    # --- BUG: should be `if pet is None: return jsonify({}), 404` ---
    return jsonify(pet), 200


@app.route("/pet", methods=["PUT"])
def update_pet():
    """
    BUG #3: doesn't validate that 'id' is an integer — accepts a string id
    silently, does a no-op "update" (since it never matches a real key),
    but still returns 200 as if it succeeded.
    """
    data = request.get_json() or {}
    pet_id = data.get("id")

    # --- BUG: no type check on pet_id; e.g. "abc" just silently fails to match ---
    if pet_id in pets:
        pets[pet_id].update(data)
        return jsonify(pets[pet_id]), 200

    # silently "succeeds" even though nothing was updated
    return jsonify(data), 200


@app.route("/pet/<pet_id>", methods=["DELETE"])
def delete_pet(pet_id):
    """
    BUG #4: compares the path param as a string against integer dict keys,
    so deleting a real, existing pet incorrectly returns 404.
    """
    # --- BUG: pet_id is a string here (Flask default converter), never matches int keys ---
    if pet_id in pets:
        del pets[pet_id]
        return "", 200

    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(port=5000, debug=True)