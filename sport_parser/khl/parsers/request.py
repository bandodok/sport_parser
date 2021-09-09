import functools

import requests
from bs4 import BeautifulSoup


@functools.lru_cache(maxsize=5)
def get_request_content(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')
