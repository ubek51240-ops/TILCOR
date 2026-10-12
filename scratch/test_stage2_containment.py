import subprocess, time, urllib.request, urllib.error, json, base64, sys

print("=== STARTING STAGE 2 ACCEPTANCE TESTS ===")

# Start server on test port 5099
port = 5099
cmd = [sys.executable, "server.py", "--port", str(port), "--env", "test"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    # Wait for server to start
    time.sleep(2)
    base_url = f"http://localhost:{port}"

    # Helper for basic auth header
    def make_auth_header(u, p):
        tok = base64.b64encode(f"{u}:{p}".encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {tok}"}

    # TEST 1: Anonymous request to /
    print("[TEST 1] Anonymous GET / ...")
    try:
        req = urllib.request.Request(f"{base_url}/")
        urllib.request.urlopen(req)
        assert False, "Anonymous GET / should have returned 401!"
    except urllib.error.HTTPError as e:
        assert e.code == 401, f"Expected 401, got {e.code}"
        assert 'noindex' in e.headers.get('X-Robots-Tag', '').lower()
        print("  -> PASSED: 401 Unauthorized, noindex present")

    # TEST 2: Anonymous request to /api/search
    print("[TEST 2] Anonymous GET /api/search?q=dengiz ...")
    try:
        req = urllib.request.Request(f"{base_url}/api/search?q=dengiz")
        urllib.request.urlopen(req)
        assert False, "Anonymous GET /api/search should have returned 401!"
    except urllib.error.HTTPError as e:
        assert e.code == 401, f"Expected 401, got {e.code}"
        print("  -> PASSED: 401 Unauthorized (corpus text cannot be read anonymously)")

    # TEST 3: Anonymous request to /api/ai
    print("[TEST 3] Anonymous POST /api/ai ...")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/ai",
            data=json.dumps({"word": "dengiz"}).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        assert False, "Anonymous POST /api/ai should have returned 401!"
    except urllib.error.HTTPError as e:
        assert e.code == 401, f"Expected 401, got {e.code}"
        print("  -> PASSED: 401 Unauthorized (AI endpoints not reachable anonymously)")

    # TEST 4: Reviewer authenticated GET /api/search
    print("[TEST 4] Reviewer GET /api/search?q=dengiz ...")
    headers_rev = make_auth_header("reviewer", "tilcor_supervisor_2026")
    req = urllib.request.Request(f"{base_url}/api/search?q=dengiz", headers=headers_rev)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['totalCorpus'] == 3811, f"Expected active totalCorpus 3811, got {data['totalCorpus']}"
        print(f"  -> PASSED: 200 OK, totalCorpus={data['totalCorpus']}, found={data['totalFound']}")

    # TEST 5: Reviewer attempting admin endpoint /api/ai
    print("[TEST 5] Reviewer POST /api/ai (must be 403 Forbidden) ...")
    try:
        req = urllib.request.Request(
            f"{base_url}/api/ai",
            data=json.dumps({"word": "dengiz"}).encode('utf-8'),
            headers={**headers_rev, "Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        assert False, "Reviewer should not have access to AI endpoint (should be 403)!"
    except urllib.error.HTTPError as e:
        assert e.code == 403, f"Expected 403 Forbidden, got {e.code}"
        print("  -> PASSED: 403 Forbidden for reviewer on admin endpoint")

    # TEST 6: Admin GET /api/stats
    print("[TEST 6] Admin GET /api/stats ...")
    headers_adm = make_auth_header("admin", "tilcor_phd_admin_2026")
    req = urllib.request.Request(f"{base_url}/api/stats", headers=headers_adm)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        stats = json.loads(resp.read().decode('utf-8'))
        assert stats['totalSegments'] == 3811
        assert stats['totalCollocations'] == 6544
        assert stats['quarantinedSegments'] == 1346
        assert stats['quarantinedCollocations'] == 2
        print(f"  -> PASSED: Live stats computed directly from DB/data: {stats}")

    # TEST 7: Search for quarantined Stevenson items
    print("[TEST 7] Search for Stevenson placeholder in /api/search ...")
    req = urllib.request.Request(f"{base_url}/api/search?q=Sarguzasht+parchasi", headers=headers_adm)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        assert res['totalFound'] == 0, f"Quarantined Stevenson items should not be found! Found: {res['totalFound']}"
        print("  -> PASSED: 0 quarantined Stevenson items returned in search")

    # TEST 8: Search for synthetic collocations
    print("[TEST 8] Search for synthetic collocations (nice nice nice) ...")
    req = urllib.request.Request(f"{base_url}/api/collocations?q=nice+nice+nice", headers=headers_adm)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        found_ids = [item.get('id') for item in res.get('results', [])]
        assert 'colloc-6411' not in found_ids, "colloc-6411 (nice nice nice) should be quarantined and excluded!"
        assert 'colloc-6412' not in found_ids, "colloc-6412 (good good good) should be quarantined and excluded!"
        print("  -> PASSED: Quarantined synthetic collocations (colloc-6411, colloc-6412) are completely excluded from search results")

    print("\nALL 8 AUTOMATED SECURITY & CONTAINMENT TESTS PASSED PERFECTLY!")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
