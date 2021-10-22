import functools
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


@functools.lru_cache(maxsize=5)
def get_request_content(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')


@functools.lru_cache(maxsize=5)
def get_selenium_content(url):
    loc = os.getenv('CHROMEDRIVER')
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_argument('ignore-certificate-errors')
    capabilities = webdriver.DesiredCapabilities().CHROME
    capabilities['acceptSslCerts'] = True
    driver = webdriver.Chrome(loc, options=op)
    driver.get(url)
    r = driver.page_source
    driver.close()
    return BeautifulSoup(r, 'html.parser')
