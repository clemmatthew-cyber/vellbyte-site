"""Check public company and support routes with normal HTTPS validation."""
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import sys

URLS = [
    'https://vellbyte.com/',
    'https://vellbyte.com/apps/',
    'https://vellbyte.com/apps/trip-split/',
    'https://vellbyte.com/apps/pack-planner/',
    'https://vellbyte.com/services/',
    'https://vellbyte.com/about/',
    'https://vellbyte.com/contact/',
    'https://vellbyte.com/testing/',
    'https://vellbyte.com/privacy/',
    'https://support.vellbyte.com/',
    'https://support.vellbyte.com/trip-split-support.html',
    'https://support.vellbyte.com/trip-split-privacy.html',
    'https://support.vellbyte.com/pack-planner-support.html',
    'https://support.vellbyte.com/pack-planner-privacy.html',
    'https://www.vellbyte.com/',
]

errors = []
for url in URLS:
    try:
        with urlopen(Request(url, headers={'User-Agent': 'VellbyteSiteCheck/1.0'}), timeout=12) as response:
            destination = urlsplit(response.geturl())
            if response.status != 200 or destination.scheme != 'https' or destination.hostname not in {'vellbyte.com', 'www.vellbyte.com', 'support.vellbyte.com'}:
                raise ValueError(f'unexpected response {response.status} at {response.geturl()}')
        print(f'OK {url}')
    except Exception as exc:
        errors.append(f'FAIL {url}: {exc}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(URLS)} public URLs returned trusted HTTPS responses.')
