import sys
sys.path.insert(0, '.')
from server import get_phd_kwic

res = get_phd_kwic({'q': ['yurak']})
print("KWIC results for 'yurak':", res.get('total'), "rows")
assert res.get('total') > 30, f"Expected >30 results for yurak, got {res.get('total')}"

res_csv = get_phd_kwic({'q': ['yurak'], 'format': ['csv']})
assert res_csv.get('is_csv'), "CSV export failed!"
print("KWIC CSV export length:", len(res_csv.get('csv_content')))
print("KWIC tests PASSED!")
