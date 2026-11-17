with open('src/web/index.html', encoding='utf-8') as f:
    text = f.read()

import re
from collections import Counter
all_ids = re.findall(r'\bid="([^"]+)"', text)
dups = {k: v for k, v in Counter(all_ids).items() if v > 1}
print('Real duplicate IDs in index.html:', dups)
