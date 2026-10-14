import glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')

js_files = [
    'js/app.js', 'js/corpus.js', 'js/collocations.js', 'js/checker.js',
    'js/dictionary.js', 'js/translator.js', 'js/phd_hub.js', 'js/researcher_hub.js'
]

for f in js_files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        print(f"=== {f} ===")
        for i, line in enumerate(lines):
            line_str = line.strip()
            if any(w in line_str for w in ['searchTerm', 'filter(', 'toLowerCase', 'search(', 'normalize', 'includes(']):
                if any(c in line_str for c in ["'", '`', '’', '‘', 'ʻ', 'ʼ']) or 'replace' in line_str or 'includes' in line_str:
                    print(f"  L{i+1}: {line_str[:120]}")
    except Exception as e:
        print(f"Error {f}: {e}")
