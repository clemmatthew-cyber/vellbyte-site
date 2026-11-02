"""Check generated page structure and local internal destinations."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
import sys

ROOT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8765'
PAGES = ['/', '/apps/', '/apps/trip-split/', '/apps/pack-planner/', '/about/', '/contact/', '/testing/', '/privacy/']

class Check(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.errors=[]; self.h1=0; self.titles=0; self.main=0; self.meta=set(); self.html_lang=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html' and a.get('lang')=='en': self.html_lang=True
        if tag=='h1': self.h1+=1
        if tag=='title': self.titles+=1
        if tag=='main': self.main+=1
        if tag=='meta': self.meta.add(a.get('name') or a.get('property'))
        if tag=='img' and 'alt' not in a: self.errors.append('image missing alt')
        for attr in ('href','src'):
            val=a.get(attr,'')
            if val and not val.startswith(('#','mailto:','tel:','https:','http:','//','data:')): self.links.append(val)

errors=[]
for route in PAGES:
    with urlopen(BASE+route,timeout=5) as response:
        html=response.read().decode('utf-8'); status=response.status
    p=Check(); p.feed(html)
    if status!=200 or p.h1!=1 or p.titles!=1 or p.main!=1 or not p.html_lang: errors.append(f'{route}: document structure failed')
    for meta in ['description','viewport','og:title','og:description','og:url','og:image']:
        if meta not in p.meta: errors.append(f'{route}: missing {meta}')
    errors.extend(f'{route}: {e}' for e in p.errors)
    for link in p.links:
        path=urlsplit(urljoin(route,link)).path
        if not path: continue
        target=ROOT/path.lstrip('/')
        if path.endswith('/'): target=target/'index.html'
        if not target.is_file(): errors.append(f'{route}: missing {link}')

support_files=sorted((ROOT/'support').glob('*.html'))
if len(support_files)!=21:
    errors.append(f'Expected 21 mirrored support pages, found {len(support_files)}')
for f in support_files:
    route='/support/'+f.name
    with urlopen(BASE+route,timeout=5) as response:
        html=response.read().decode('utf-8')
        if response.status!=200: errors.append(f'{route}: HTTP {response.status}')
    p=Check(); p.feed(html)
    if 'draft' not in html.lower() or 'noindex' not in html.lower(): errors.append(f'{route}: missing draft/noindex labeling')
    for link in p.links:
        path=urlsplit(urljoin(route,link)).path
        if not path: continue
        target=ROOT/path.lstrip('/')
        if path.endswith('/'): target=target/'index.html'
        if not target.is_file(): errors.append(f'{route}: missing {link}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(PAGES)} company routes and {len(support_files)} mirrored support pages served; internal destinations, draft labels and company metadata checked.')
