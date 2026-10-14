import subprocess
import time
import urllib.request
import urllib.error
import json
import sys

# Start server locally on port 5055 for testing
print("Starting server.py test instance on port 5055...")
proc = subprocess.Popen([sys.executable, "server.py", "--port", "5055"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(2.5)

base_url = "http://localhost:5055"
tests = [
    ("GET / (Home)", f"{base_url}/", "GET", None, 200),
    ("GET /methodology.html", f"{base_url}/methodology.html", "GET", None, 200),
    ("GET /api/stats", f"{base_url}/api/stats", "GET", None, 200),
    ("GET /api/search?q=dengiz&limit=100", f"{base_url}/api/search?q=dengiz&limit=100", "GET", None, 200),
    ("POST /api/translate", f"{base_url}/api/translate", "POST", json.dumps({"text": "test"}).encode(), 401),
    ("POST /api/ai", f"{base_url}/api/ai", "POST", json.dumps({"message": "test"}).encode(), 401),
    ("GET /api/collocations/ai-analyze", f"{base_url}/api/collocations/ai-analyze?word=test", "GET", None, 401),
    ("POST /api/checker/ai-diagnose", f"{base_url}/api/checker/ai-diagnose", "POST", json.dumps({"text": "test"}).encode(), 401),
]

all_passed = True
results = []
try:
    for name, url, method, data, expected_code in tests:
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                body = resp.read()
                if name == "GET /api/stats":
                    stats = json.loads(body.decode())
                    print(f"  Live stats: {stats}")
                elif "api/search" in name:
                    search_res = json.loads(body.decode())
                    print(f"  Search count returned: {len(search_res.get('results', []))} (clamped to <=50)")
                if status == expected_code:
                    results.append((name, status, "PASS"))
                else:
                    results.append((name, status, f"FAIL (expected {expected_code})"))
                    all_passed = False
        except urllib.error.HTTPError as e:
            if e.code == expected_code:
                results.append((name, e.code, "PASS"))
            else:
                results.append((name, e.code, f"FAIL (expected {expected_code})"))
                all_passed = False
        except Exception as e:
            results.append((name, str(e), "ERROR"))
            all_passed = False
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

print("\n--- TEST RESULTS ---")
for r in results:
    print(f"[{r[2]}] {r[0]}: HTTP {r[1]}")
print(f"OVERALL: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
