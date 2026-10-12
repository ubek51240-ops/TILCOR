import json

with open(r'C:\Users\user\Desktop\tarjimon\data\full_corpus.json', 'r', encoding='utf-8') as f:
    fc = json.load(f)

hem_items = [item for item in fc if item.get('book') == 'hemingway']
cho_items = [item for item in fc if item.get('book') == 'cholpon']

def sample_30(items, name):
    n = len(items)
    print(f"\n=================== {name} (Total: {n} pairs) ===================")
    indices = list(range(10)) + list(range(n//2 - 5, n//2 + 5)) + list(range(n - 10, n))
    for idx in indices:
        item = items[idx]
        pos = "BEGIN" if idx < 10 else ("MID" if idx < n//2 + 5 else "END")
        uz = " ".join(item.get('uz', '').split())[:65]
        en = " ".join(item.get('en', '').split())[:65]
        print(f"[{pos} #{idx+1} | {item['id']}]")
        print(f"  UZ: {uz}...")
        print(f"  EN: {en}...")

sample_30(hem_items, "HEMINGWAY")
sample_30(cho_items, "CHO'LPON")
