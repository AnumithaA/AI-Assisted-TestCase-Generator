import requests

BASE = "http://127.0.0.1:5000"

print("BUG-1: POST /pet missing required fields (expect 400, bug returns 200)")
r = requests.post(f"{BASE}/pet", json={})
print(f"  -> got {r.status_code}: {r.json()}\n")

print("BUG-2: GET /pet/999 nonexistent (expect 404, bug returns 200)")
r = requests.get(f"{BASE}/pet/999")
print(f"  -> got {r.status_code}: {r.json()}\n")

print("BUG-3: PUT /pet with non-integer id (expect 400, bug returns 200)")
r = requests.put(f"{BASE}/pet", json={"id": "abc", "name": "Test"})
print(f"  -> got {r.status_code}: {r.json()}\n")

print("BUG-4: DELETE /pet/1 (existing pet) (expect 200, bug returns 404)")
r = requests.delete(f"{BASE}/pet/1")
print(f"  -> got {r.status_code}\n")