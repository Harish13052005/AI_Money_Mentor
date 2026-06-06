"""
Production Readiness Audit Tests for AI Money Mentor
Tests all critical endpoints and functionality
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://192.168.0.39:8501"
RESULTS = []

def log_test(name, status, details=""):
    result = {
        "test": name,
        "status": "PASS" if status else "FAIL",
        "details": details
    }
    RESULTS.append(result)
    status_str = "[PASS]" if status else "[FAIL]"
    print(f"{status_str} {name}")
    if details:
        print(f"      {details}")

# ==================== TESTS ====================

# Test 1: Health Check
print("\n=== BACKEND STARTUP ===")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    if resp.status_code == 200:
        log_test("Health Check", True, f"Status: {resp.status_code}")
    else:
        log_test("Health Check", False, f"Status: {resp.status_code}")
except Exception as e:
    log_test("Health Check", False, str(e))

# Test 2: Register User
print("\n=== AUTHENTICATION ===")
test_user_register = {
    "username": f"testuser_{datetime.now().timestamp()}",
    "email": f"test_{datetime.now().timestamp()}@example.com",
    "password": "securepass123"
}
try:
    resp = requests.post(f"{BASE_URL}/register", json=test_user_register, timeout=5)
    if resp.status_code == 200:
        user_data = resp.json()
        log_test("Register User", True, f"Username: {user_data.get('username')}")
        test_user = test_user_register
    else:
        log_test("Register User", False, f"Status: {resp.status_code}, Response: {resp.text[:100]}")
        test_user = None
except Exception as e:
    log_test("Register User", False, str(e))
    test_user = None

# Test 3: Login
token = None
if test_user:
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        resp = requests.post(f"{BASE_URL}/token", data=login_data, timeout=5)
        if resp.status_code == 200:
            token_data = resp.json()
            token = token_data.get("access_token")
            log_test("Login (Token Generation)", True, f"Token received: {len(token) if token else 0} chars")
        else:
            log_test("Login (Token Generation)", False, f"Status: {resp.status_code}, Response: {resp.text[:100]}")
    except Exception as e:
        log_test("Login (Token Generation)", False, str(e))

# Test 4: Get Current User
if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/users/me/", headers=headers, timeout=5)
        if resp.status_code == 200:
            user = resp.json()
            log_test("Get Current User (JWT Auth)", True, f"User: {user.get('username')}")
        else:
            log_test("Get Current User (JWT Auth)", False, f"Status: {resp.status_code}")
    except Exception as e:
        log_test("Get Current User (JWT Auth)", False, str(e))

# Test 5: Analyze Financial Data (requires auth)
print("\n=== FINANCIAL ANALYSIS ===")
if token:
    analyze_data = {
        "income": 5000.0,
        "expenses": 3000.0,
        "savings": 1000.0,
        "investments": [{"type": "stocks", "amount": 500}],
        "goals": ["retirement", "emergency fund"]
    }
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/analyze", json=analyze_data, headers=headers, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            log_test("Analyze Financial Data", True, f"Savings Rate: {result.get('summary', 'N/A')[:50]}")
            record_id = None  # Will need to fetch from history
        else:
            log_test("Analyze Financial Data", False, f"Status: {resp.status_code}, Response: {resp.text[:150]}")
    except Exception as e:
        log_test("Analyze Financial Data", False, str(e))

# Test 6: Get History
print("\n=== HISTORY & RECORDS ===")
if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/history", headers=headers, timeout=5)
        if resp.status_code == 200:
            records = resp.json()
            if len(records) > 0:
                record_id = records[0].get("id")
                log_test("Get Financial History", True, f"Records found: {len(records)}")
            else:
                log_test("Get Financial History", True, f"No records yet (expected for new user)")
                record_id = None
        else:
            log_test("Get Financial History", False, f"Status: {resp.status_code}")
            record_id = None
    except Exception as e:
        log_test("Get Financial History", False, str(e))
        record_id = None

# Test 7: Get Record Detail
if token and record_id:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/records/{record_id}", headers=headers, timeout=5)
        if resp.status_code == 200:
            record = resp.json()
            log_test("Get Record Detail", True, f"Record ID: {record.get('id')}")
        else:
            log_test("Get Record Detail", False, f"Status: {resp.status_code}")
    except Exception as e:
        log_test("Get Record Detail", False, str(e))

# Test 8: Explain Endpoint
print("\n=== AI EXPLANATIONS ===")
if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"question": "How can I increase my savings rate?", "context": ""}
        resp = requests.post(f"{BASE_URL}/explain", params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            log_test("Explain Endpoint", True, f"Response length: {len(result.get('explanation', ''))} chars")
        else:
            log_test("Explain Endpoint", False, f"Status: {resp.status_code}")
    except Exception as e:
        log_test("Explain Endpoint", False, str(e))

# Test 9: Duplicate Email Check
print("\n=== INPUT VALIDATION ===")
try:
    resp = requests.post(f"{BASE_URL}/register", json=test_user_register, timeout=5)
    if resp.status_code == 400:
        log_test("Duplicate Email Rejection", True, "Correctly rejected duplicate")
    else:
        log_test("Duplicate Email Rejection", False, f"Status: {resp.status_code} (expected 400)")
except Exception as e:
    log_test("Duplicate Email Rejection", False, str(e))

# Test 10: Invalid Token
print("\n=== ERROR HANDLING ===")
try:
    headers = {"Authorization": "Bearer invalid_token"}
    resp = requests.get(f"{BASE_URL}/users/me/", headers=headers, timeout=5)
    if resp.status_code == 401:
        log_test("Invalid Token Rejection", True, "401 Unauthorized")
    else:
        log_test("Invalid Token Rejection", False, f"Status: {resp.status_code} (expected 401)")
except Exception as e:
    log_test("Invalid Token Rejection", False, str(e))

# Test 11: Missing Token
try:
    resp = requests.get(f"{BASE_URL}/users/me/", timeout=5)
    if resp.status_code == 403:
        log_test("Missing Token Rejection", True, "403 Forbidden")
    else:
        log_test("Missing Token Rejection", False, f"Status: {resp.status_code} (expected 403)")
except Exception as e:
    log_test("Missing Token Rejection", False, str(e))

# ==================== REPORT ====================
print("\n\n=== AUDIT REPORT ===")
print(f"Total Tests: {len(RESULTS)}")
pass_count = sum(1 for r in RESULTS if "PASS" in r["status"])
fail_count = sum(1 for r in RESULTS if "FAIL" in r["status"])
print(f"PASSED: {pass_count}")
print(f"FAILED: {fail_count}")

print("\n=== DETAILED RESULTS ===")
for result in RESULTS:
    status_fmt = result['status'].ljust(10)
    print(f"{status_fmt} | {result['test']:35} | {result['details']}")

sys.exit(0 if fail_count == 0 else 1)
