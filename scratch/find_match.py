with open('src/web/index.html', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'<[^>]*\bid="bollinger_close_in"[^>]*>', text)
print('bollinger_close_in matches:', matches)
