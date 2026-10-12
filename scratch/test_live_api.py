import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Test /api/occurrences
req = urllib.request.urlopen('http://localhost:5050/api/occurrences?limit=5')
data = json.loads(req.read().decode('utf-8'))
print('API /api/occurrences total:', data.get('total'))
print('First occurrence item:', data['results'][0]['surface_form_en'], '<->', data['results'][0]['surface_form_uz'])
print('First occurrence page:', data['results'][0]['pdf_page_num'], '| Strategy:', data['results'][0]['translation_strategy'])

# 2. Test /api/kwic
req2 = urllib.request.urlopen('http://localhost:5050/api/kwic?q=wrinkles&limit=3')
data2 = json.loads(req2.read().decode('utf-8'))
print('\nAPI /api/kwic count for wrinkles:', len(data2.get('results', [])))
for k in data2['results']:
    print(f"   {k['left']} [{k['keyword']}] {k['right']} (p.{k['page']})")

# 3. Test /api/export
req3 = urllib.request.urlopen('http://localhost:5050/api/export?type=occurrences')
content = req3.read().decode('utf-8')
print('\nAPI /api/export CSV lines:', len(content.splitlines()))
print('API /api/export Header:', content.splitlines()[0][:80])

# 4. Test /api/annotate (POST)
payload = json.dumps({
    'occurrence_id': 'occ-00007',
    'grammatical_pattern': 'Sifat + Ot (Adj + Noun)',
    'semantic_group': 'Tana a’zolari va tashqi koʻrinish',
    'equivalence_type': 'Toʻliq ekvivalent',
    'translation_strategy': 'direct_adequate',
    'is_lingvocultural': 0,
    'scientific_note': 'Ensani chuqur ajinlar qoplashi obrazli tarzda toʻliq ekvivalent bilan berilgan.',
    'annotator_name': 'PhD Izlanuvchi'
}).encode('utf-8')

req4 = urllib.request.Request('http://localhost:5050/api/annotate', data=payload, headers={'Content-Type': 'application/json'})
res4 = json.loads(urllib.request.urlopen(req4).read().decode('utf-8'))
print('\nAPI /api/annotate result:', res4)
