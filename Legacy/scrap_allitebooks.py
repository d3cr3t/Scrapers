#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_allitebooks.py

'''

# BS se puede instalar con pip install beautifulsoup4
# requests se instala con pip to install requests

from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import pprint
import random

urlBaseIndex = 'http://www.allitebooks.org/page/%PAGE%/'

# Carpeta para resultados
path = "./_SCRAP_ALLITEBOOKS"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

session = requests.Session()

for page in range(1, 862):

	url = urlBaseIndex.replace("%PAGE%", str(page).strip())
	print("Leyendo", page, url)
	print("-" * 80)

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers)

	html = r.content
	bsObj = bs(html, "lxml")	#"html.parser")

	# Extraemos los links a cada página de cada libro

	for level1 in bsObj.findAll('h2', {"class": "entry-title"}):
		for level2 in level1.findAll('a'):
			#pprint.pprint(level2.attrs['href'])
			#out.write(level2.attrs['href']+"\n")

			# Vamos por el libro...
			print("Leyendo...", level2.attrs['href'])
			rbook = session.get(level2.attrs['href'], headers=headers)

			htmlbook = rbook.content
			bsObjbook = bs(htmlbook, "lxml")	#"html.parser")

			for book1 in bsObjbook.findAll('span', {"class": re.compile("download-links")}):
				for book2 in book1.findAll('a'):
					pprint.pprint(book2.attrs['href'])
					out.write(book2.attrs['href']+"\n")

out.close()
