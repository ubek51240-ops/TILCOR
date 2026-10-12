import json

with open(r'C:\Users\user\Desktop\tarjimon\data\collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = json.load(f)

print(f"Total collocation entries: {len(collocs):,}")

# Check repeated token entries: e.g. "nice nice nice"
repeated = []
for c in collocs:
    en_words = c.get('english', '').lower().split()
    if len(en_words) > 1 and len(set(en_words)) == 1:
        repeated.append(c['english'])

print(f"Repeated token entries: {len(repeated)} (Samples: {repeated[:5]})")

# Check identical scores (MI 8.08, T 10.6, freq 137, LL 70.26)
identical_count = sum(1 for c in collocs if c.get('miScore') == 8.08 and c.get('tScore') == 10.6 and c.get('freq') == 137)
print(f"Entries with hardcoded template metrics (MI=8.08, T=10.6, f=137): {identical_count:,} ({identical_count/len(collocs)*100:.1f}%)")

# Sources breakdown
sources_cnt = {}
for c in collocs:
    src = c.get('sourceBook', 'Unknown')
    sources_cnt[src] = sources_cnt.get(src, 0) + 1

print("\nSources breakdown:")
for s, cnt in sorted(sources_cnt.items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f"  {s}: {cnt:,} ta")
