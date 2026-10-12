import json
import os

data_path = 'data/collocations_full.json'
out_path = 'js/collocations_list.js'

with open(data_path, 'r', encoding='utf-8') as f:
    collocs = json.load(f)

print(f"Jami yuklangan birikmalar: {len(collocs)} ta")

# Create JavaScript file
js_content = "/**\n"
js_content += " * KORPUS.LINGVO — 4 ta kitob va asosiy badiiy parallel korpusdan to'liq kollokatsiyalar ro'yxati\n"
js_content += " * Manbalar:\n"
js_content += " * 1. Cambridge Collocations in Use (Intermediate) (4,323 ta)\n"
js_content += " * 2. IELTS Academic Collocations List (2,466 ta)\n"
js_content += " * 3. 1000 English Collocations Ebook (778 ta)\n"
js_content += " * 4. Cambridge Collocations in Use (Advanced) (173 ta)\n"
js_content += f" * Jami noyob saralangan birikmalar: {len(collocs)} ta to'liq o'zbekcha tarjimasi bilan\n"
js_content += " */\n\n"
js_content += "const collocationsList = " + json.dumps(collocs, ensure_ascii=False) + ";\n\n"
js_content += "if (typeof window !== 'undefined') {\n"
js_content += "    window.collocationsList = collocationsList;\n"
js_content += "    window.collocationsDatabase = collocationsList;\n"
js_content += "}\n"

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

size_mb = os.path.getsize(out_path) / (1024 * 1024)
print(f"Muvaffaqiyatli saqlandi: {out_path} ({size_mb:.2f} MB)")
