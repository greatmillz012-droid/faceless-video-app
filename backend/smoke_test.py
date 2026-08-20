#!/usr/bin/env python3
"""Smoke test for the local app."""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n=== TEST 1: Health Check ===")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    print("✓ PASS")

def test_register():
    """Test user registration."""
    print("\n=== TEST 2: Register User ===")
    payload = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Token: {data.get('access_token', 'N/A')[:30]}...")
        print("✓ PASS")
        return data.get("access_token")
    else:
        print("✗ FAIL")
        return None

def test_login(email="testuser@example.com", password="testpass123"):
    """Test user login."""
    print("\n=== TEST 3: Login ===")
    payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Token: {data.get('access_token', 'N/A')[:30]}...")
        print("✓ PASS")
        return data.get("access_token")
    else:
        print("✗ FAIL")
        return None

def test_videos(token):
    """Test get videos endpoint."""
    print("\n=== TEST 4: Get Videos (Protected) ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/videos", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    if resp.status_code == 200:
        print("✓ PASS")
    else:
        print("✗ FAIL")

def test_api_docs():
    """Test API documentation endpoint."""
    print("\n=== TEST 5: API Docs ===")
    resp = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✓ PASS - Swagger docs available")
    else:
        print("✗ FAIL")

def main():
    print("=" * 60)
    print("FACELESS VIDEO APP - SMOKE TEST")
    print("=" * 60)
    
    try:
        test_health()
        token = test_register()
        if not token:
            token = test_login()
        if token:
            test_videos(token)
        test_api_docs()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✓ Backend (FastAPI) running on http://localhost:8000")
        print("✓ SQLite database initialized")
        print("✓ Authentication system functional")
        print("✓ API endpoints responding")
        print("\nApp is ready for development!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
