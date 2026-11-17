with open('src/web/index.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'bollinger_close_in' in l or 'keltner_squeeze' in l:
        print(f'{i+1}: {l.strip()}')
