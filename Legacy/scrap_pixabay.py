#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_pixabay.py

'''

# BS se puede instalar con pip install beautifulsoup4
# requests se instala con pip install requests

from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import pprint
import random

from collections import defaultdict
cookiesdc = defaultdict(lambda : None)

if sys.version_info < (3,):
    from cookielib import Cookie, MozillaCookieJar
else:
    from http.cookiejar import Cookie, MozillaCookieJar

def load_cookies_from_mozilla(filename):
    ns_cookiejar = MozillaCookieJar()
    ns_cookiejar.load(filename, ignore_discard=True)
    return ns_cookiejar

urlBase = 'https://pixabay.com/es/images/search/erotic/?pagi='
urlRoot = "https://pixabay.com"

# Carpeta para resultados
path = "./_SCRAP_PIXABAY"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

# Cookies must be generated with a valid login process, saving them and putting values here
cookiesdc['__cfduid'] = 'db61541c0a1b62589ff609628fb6dd3751585521494'
cookiesdc['lang'] = 'es'
cookiesdc['anonymous_user_id'] = '22a1649b-35b4-4e22-9da5-cdb37be79c4f'
cookiesdc['client_width'] = '1769'
cookiesdc['is_human'] = '1'
cookiesdc['csrftoken'] = 'llCvH7qKuGxRkH4CA4lrUUZgxHIUpnF4Vx4Q30mqUdQWij0HrdTbXjPhT0GdOVK6'
cookiesdc['user_id'] = '2540863'
cookiesdc['sessionid'] = '.eJxVjEsOwiAQQO_C2jTSoQhehkxhGpBSDJ-4MN7d2oVJ1-_zZo1qsznHQOzOXrlEcuzCDPbmTa9UTHA7GCdxVRLOZEYbafvhZ8kPsm3oLax1sL22nA5xCIe6YSKTi6GEYf13p5nH6veT4honOQICB7QChNKz5FqgWvAmueOCrAO5sM8XIKI_gQ:1jIgZa:WGhE58Rsf7ZW_QJSIseCmrLvAzY'

session = requests.Session()

for page in range(1, 2):	#30):

	url = urlBase+str(page).strip()
	print("Leyendo", url)

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, cookies=cookiesdc, verify=False)

	html = r.content
	bsObj = bs(html, "html.parser")

	print(html)

	# Cada página es el índice de una imagen

	for level1 in bsObj.findAll('div', {"class": re.compile("flex_grid")}):
		for level2 in level1.findAll('a'):
			pprint.pprint(level2.attrs['href'])
			#out.write(level2.attrs['href']+"\n")


out.close()
