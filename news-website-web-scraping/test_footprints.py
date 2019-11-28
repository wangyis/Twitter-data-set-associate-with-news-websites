# the purpose of this file is to test formatting of different news sites
# (not part of actual project functionality)

import urllib2
import os
import re
import html2text
from bs4 import BeautifulSoup
import articleDateExtractor
import time
import datetime
import requests


# TESTING
site = 'https://thehill.com/regulation/court-battles/441210-judge-rules-in-favor-of-sacha-baron-cohen-in-hearing-on-roy-moore'
site2 = 'https://thehill.com/author/brett-samuels'
page = requests.get(site)
page2 = requests.get(site2)
soup = BeautifulSoup(page.text)
soup2 = BeautifulSoup(page2.text)

print(soup)
print(soup2)
#print(re.search('(?i)((?<=(category":{"title":")).+?(?="))', str(soup))).group(0).lower()
# print(re.findall('(?i)((?<=("fullname":")).+?(?="))', str(soup)))
# print(soup.title.string)

# print(soup.get_text())