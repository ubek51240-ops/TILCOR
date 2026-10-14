with open('index.html', encoding='utf-8') as f:
    for i, l in enumerate(f, 1):
        if 'id="view-' in l:
            print(f"{i}: {l.strip()}")
