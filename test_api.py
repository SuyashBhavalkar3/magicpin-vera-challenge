import requests
import json

def test():
    base_url = "http://localhost:8000"
    
    print("Testing /v1/healthz...")
    try:
        r = requests.get(f"{base_url}/v1/healthz")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nTesting /v1/metadata...")
    try:
        r = requests.get(f"{base_url}/v1/metadata")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nTesting /v1/context (Pushing a sample category)...")
    try:
        payload = {
            "scope": "category",
            "context_id": "dentists",
            "version": 1,
            "payload": {"name": "Dentists", "slug": "dentists"},
            "delivered_at": "2026-04-29T12:00:00Z"
        }
        r = requests.post(f"{base_url}/v1/context", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
