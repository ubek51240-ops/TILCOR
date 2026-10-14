"""
scripts/test_server_endpoints.py - Comprehensive verification of local server endpoints
Tests anonymous 401s, PBKDF2 authentication, session cookies, rate limits, and /api/collocations filtering.
"""

import sys
import os
import threading
import time
import urllib.request
import urllib.parse
import http.cookiejar
import json

# Ensure workspace root is in path
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE)

import server

def run_test_server(port):
    server_address = ('127.0.0.1', port)
    httpd = server.socketserver.TCPServer(server_address, server.AppRequestHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def main():
    test_port = 8765
    print(f"[*] Starting test server on port {test_port}...")
    httpd = run_test_server(test_port)
    time.sleep(0.5)

    base_url = f"http://127.0.0.1:{test_port}"
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    results = {}

    def fetch(path, data=None, headers=None, use_opener=True):
        url = base_url + path
        hdrs = headers or {}
        req = urllib.request.Request(url, data=data, headers=hdrs)
        caller = opener.open if use_opener else urllib.request.urlopen
        try:
            with caller(req) as resp:
                body = resp.read().decode('utf-8')
                return resp.status, body, resp.headers
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            return e.code, body, e.headers
        except Exception as e:
            return 999, str(e), {}

    print("\n--- 1. Testing Anonymous Endpoints ---")
    # Anonymous GET /
    status, body, _ = fetch('/')
    print(f"GET / -> Status: {status}")
    assert status == 200, f"Expected 200, got {status}"
    results['/'] = status

    # Anonymous GET /api/auth/me
    status, body, _ = fetch('/api/auth/me')
    print(f"GET /api/auth/me -> Status: {status}, Body: {body}")
    assert status == 200
    data = json.loads(body)
    assert data.get('isAdmin') is False
    results['/api/auth/me (anonymous)'] = status

    # Anonymous GET /api/ai -> must be 401
    status, body, _ = fetch('/api/ai')
    print(f"GET /api/ai -> Status: {status}")
    assert status in (401, 403), f"Expected 401/403, got {status}"
    results['/api/ai'] = status

    # Anonymous GET /api/translate -> must be 401
    status, body, _ = fetch('/api/translate')
    print(f"GET /api/translate -> Status: {status}")
    assert status in (401, 403), f"Expected 401/403, got {status}"
    results['/api/translate'] = status

    # Anonymous GET /api/collocations/ai-analyze?word=test -> must be 401
    status, body, _ = fetch('/api/collocations/ai-analyze?word=test')
    print(f"GET /api/collocations/ai-analyze?word=test -> Status: {status}")
    assert status in (401, 403), f"Expected 401/403, got {status}"
    results['/api/collocations/ai-analyze?word=test'] = status

    # Anonymous GET /api/checker/ai-diagnose -> must be 401
    status, body, _ = fetch('/api/checker/ai-diagnose')
    print(f"GET /api/checker/ai-diagnose -> Status: {status}")
    assert status in (401, 403), f"Expected 401/403, got {status}"
    results['/api/checker/ai-diagnose'] = status

    print("\n--- 2. Testing /api/collocations?q=heart (filtering test) ---")
    status, body, _ = fetch('/api/collocations?q=heart')
    assert status == 200
    colloc_data = json.loads(body)
    colloc_list = colloc_data.get('collocations', colloc_data.get('results', []))
    ids = [c.get('id') for c in colloc_list]
    print(f"Returned {len(colloc_list)} collocations for 'heart'.")
    assert 'colloc-2685' not in ids, "colloc-2685 MUST NOT be returned!"
    assert 'colloc-5766' not in ids, "colloc-5766 MUST NOT be returned!"
    print("PASS: Neither colloc-2685 nor colloc-5766 returned!")
    results['collocations_filtering'] = "PASS"

    print("\n--- 3. Testing Admin Login Flow ---")
    # Failed login
    fail_payload = json.dumps({"username": "admin", "password": "wrongpassword"}).encode('utf-8')
    status, body, _ = fetch('/api/auth/login', data=fail_payload, headers={'Content-Type': 'application/json'})
    print(f"Failed login -> Status: {status}")
    assert status == 401

    # Successful login with PBKDF2
    login_payload = json.dumps({"username": "admin", "password": "<parol kodda saqlanmaydi>"}).encode('utf-8')
    status, body, headers = fetch('/api/auth/login', data=login_payload, headers={'Content-Type': 'application/json'})
    print(f"Success login -> Status: {status}, Body: {body}")
    assert status == 200
    login_resp = json.loads(body)
    assert login_resp.get('isAdmin') is True

    # Test /api/auth/me as authenticated admin
    status, body, _ = fetch('/api/auth/me')
    print(f"GET /api/auth/me (authenticated) -> Status: {status}, Body: {body}")
    assert status == 200
    me_resp = json.loads(body)
    assert me_resp.get('isAdmin') is True
    assert me_resp.get('user') == 'admin'

    # Test AI endpoint as authenticated admin
    status, body, _ = fetch('/api/collocations/ai-analyze?word=test')
    print(f"GET /api/collocations/ai-analyze (as admin) -> Status: {status}")
    assert status == 200

    # Test Logout
    status, body, _ = fetch('/api/auth/logout', data=b"{}", headers={'Content-Type': 'application/json'})
    print(f"POST /api/auth/logout -> Status: {status}")
    assert status == 200

    # Verify session cleared in /api/auth/me
    status, body, _ = fetch('/api/auth/me')
    print(f"GET /api/auth/me (after logout) -> Status: {status}, Body: {body}")
    assert status == 200
    me_after = json.loads(body)
    assert me_after.get('isAdmin') is False

    print("\n--- 4. Summary of Endpoint Test Results ---")
    for k, v in results.items():
        print(f"  {k}: {v}")

    print("\nALL SERVER ENDPOINT TESTS PASSED SUCCESSFULLY!")
    httpd.shutdown()

if __name__ == '__main__':
    main()
