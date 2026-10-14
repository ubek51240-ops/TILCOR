import re, sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import server

APOSTROPHE_CHARS = "'’‘`ʻʼ´ʹ՚′‵ˈ"
# Regex that treats all apostrophe variants within words as part of the word:
FIXED_TOKEN_PATTERN = re.compile(rf"[a-zA-Z\u0400-\u04FF]+(?:[{APOSTROPHE_CHARS}-][a-zA-Z\u0400-\u04FF]+)*")

active_c = server.get_active_corpus()[:500]

found_oz = 0
found_koz = 0
for seg in active_c:
    uz_text = seg.get('uz', '')
    tokens = FIXED_TOKEN_PATTERN.findall(uz_text)
    # Check if any token has o'z or ko'z variants
    for t in tokens:
        clean = re.sub(rf"[{APOSTROPHE_CHARS}]", "'", t).lower()
        if clean in ['o\'z', 'o\'zini', 'o\'zining', 'o\'ziga']:
            found_oz += 1
            break
    for t in tokens:
        clean = re.sub(rf"[{APOSTROPHE_CHARS}]", "'", t).lower()
        if 'ko\'z' in clean:
            found_koz += 1
            break

print(f"With fixed token pattern: found o'z in {found_oz} sentences, ko'z in {found_koz} sentences!")
