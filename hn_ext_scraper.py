import json
import random
import time
from collections import Counter
import requests
import re
import itertools
import html

CHROME_EXT = 'chrome.google.com/webstore/detail'
CHROME_EXT_RGX = r'https?://chrome.google.com/webstore/detail/[A-Za-z\-/]+/?'


def scrape_algolia(query, page=1):
    # Scrape search results (Algolia API)
    r = requests.get(
        'https://hn.algolia.com/api/v1/search',
        params={
            'query': query,
            'hitsPerPage': '100',
            'page': str(page),
        }
    )
    obj = r.json()
    return obj.get('hits')


def normalize_url(url):
    return f"https://{url.split('//', 1)[-1]}".strip('/')


if __name__ == '__main__':
    output = Counter()

    for i in itertools.count(1):
        print(f'Page {i} - {len(output)} extensions scraped.')
        hits = scrape_algolia(CHROME_EXT, page=i)
        if not hits:
            break

        for hit in hits:
            extensions = set()

            text = '\n'.join([str(hit.get('url')), str(hit.get('story_text'))])
            extensions.update(
                re.findall(CHROME_EXT_RGX, text)
            )
            if not extensions:
                r = requests.get(
                    f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    headers={
                        'User-Agent': 'HN Scraper <dario@mory.dev>',
                    },
                    timeout=5,
                )
                extensions.update(
                    re.findall(CHROME_EXT_RGX, html.unescape(r.text))
                )
                # Random sleep (reduce server load)
                time.sleep(random.uniform(2, 10))

            output.update([normalize_url(i) for i in extensions])
            print(extensions if extensions else '')

    with open('extensions.json', 'w') as f:
        f.write(json.dumps(dict(output)))
