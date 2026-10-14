"""Clean the reference collocation base (data/collocations_full.json).

Run once on the server:  python3 scripts/clean_reference_base_v3.py
A copy of the previous file is kept as data/collocations_full.before_v3.json.

What it does (nothing is invented, only removed or relabelled):
1. "miScore", "tScore", "freq", "logLikelihood" were not computed from any corpus
   (the same values repeat across hundreds of unrelated entries). They are set to null
   and "stats_status" explains that statistics will come from the reference corpus (step 09).
2. Template example sentences ("He noticed that X was crucial.") are removed.
3. Boilerplate notes repeated in thousands of entries ("So'zma-so'z kalka qilinmaydi: ...")
   are removed. Entry-specific notes are kept.
"""
import json, os, re, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, '..', 'data', 'collocations_full.json')
TEMPLATE = re.compile(r"^(He|She|They) (noticed|said|thought) that .+ (was|were) (crucial|important)\.?$", re.I)

with open(PATH, encoding='utf-8') as f:
    data = json.load(f)

backup = PATH.replace('.json', '.before_v3.json')
if not os.path.exists(backup):
    shutil.copyfile(PATH, backup)

trap_counts = collections.Counter((d.get('literalTrap') or '').strip() for d in data)
note_counts = collections.Counter((d.get('culturalNote') or '').strip() for d in data)
boiler_traps = {t for t, c in trap_counts.items() if t and c >= 20}
boiler_notes = {t for t, c in note_counts.items() if t and c >= 20}

n_stats = n_ex = n_trap = n_note = 0
for d in data:
    for k in ('miScore', 'tScore', 'freq', 'logLikelihood',
              'miScore_display', 'tScore_display', 'freq_display', 'logLikelihood_display'):
        if d.get(k) not in (None, ''):
            d[k] = None
            n_stats += 1
    d['stats_status'] = "hisoblanmagan — tayanch korpus statistikasi keyingi bosqichda"
    ex = d.get('example')
    if isinstance(ex, dict):
        src = (ex.get('source_sentence') or ex.get('en') or '').strip()
        if src and TEMPLATE.match(src):
            d['example'] = None
            n_ex += 1
    if (d.get('literalTrap') or '').strip() in boiler_traps:
        d['literalTrap'] = ''
        n_trap += 1
    if (d.get('culturalNote') or '').strip() in boiler_notes:
        d['culturalNote'] = ''
        n_note += 1

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"entries: {len(data)}")
print(f"statistic fields set to null: {n_stats}")
print(f"template examples removed: {n_ex}")
print(f"boilerplate literalTrap removed: {n_trap} (texts: {len(boiler_traps)})")
print(f"boilerplate culturalNote removed: {n_note} (texts: {len(boiler_notes)})")
