from bs4 import BeautifulSoup

with open('src/web/index.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
ids = [tag.get('id') for tag in soup.find_all(id=True)]
from collections import Counter
print('Real BeautifulSoup duplicate IDs:', {k: v for k, v in Counter(ids).items() if v > 1})
