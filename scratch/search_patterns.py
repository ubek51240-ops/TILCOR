import os, re

patterns = ['dissertationData', 'researchStats', 'literaryCorporaMeta', 'Fair Use', 'Open Access', 'erkin ochiq', 'Sarguzasht parchasi']
files_to_check = ['index.html'] + [os.path.join('js', f) for f in os.listdir('js') if f.endswith('.js')]

for path in files_to_check:
    if not os.path.exists(path):
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            for pat in patterns:
                matches = list(re.finditer(re.escape(pat), content, re.IGNORECASE))
                if matches:
                    print(f'{path}: found {len(matches)} occurrences of "{pat}"')
    except Exception as e:
        print(f'Error reading {path}: {e}')
