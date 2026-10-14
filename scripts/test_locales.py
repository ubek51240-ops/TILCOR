"""
scripts/test_locales.py - Verifies that every key in locales/uz.json
exists in locales/en.json and locales/ru.json without any missing keys.
Fails with non-zero exit code if any key is missing.
"""

import json
import os
import sys

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locales')

with open(os.path.join(LOCALES_DIR, 'uz.json'), 'r', encoding='utf-8') as f:
    uz_data = json.load(f)

with open(os.path.join(LOCALES_DIR, 'en.json'), 'r', encoding='utf-8') as f:
    en_data = json.load(f)

with open(os.path.join(LOCALES_DIR, 'ru.json'), 'r', encoding='utf-8') as f:
    ru_data = json.load(f)

uz_keys = set(uz_data.keys())
en_keys = set(en_data.keys())
ru_keys = set(ru_data.keys())

missing_in_en = uz_keys - en_keys
missing_in_ru = uz_keys - ru_keys

print(f"Total keys in uz.json: {len(uz_keys)}")
print(f"Total keys in en.json: {len(en_keys)}")
print(f"Total keys in ru.json: {len(ru_keys)}")

failed = False
if missing_in_en:
    print(f"ERROR: Missing keys in en.json: {missing_in_en}")
    failed = True
else:
    print("PASS: en.json has all keys.")

if missing_in_ru:
    print(f"ERROR: Missing keys in ru.json: {missing_in_ru}")
    failed = True
else:
    print("PASS: ru.json has all keys.")

if failed:
    sys.exit(1)
print("ALL LOCALE TESTS PASSED SUCCESSFULLY!")
