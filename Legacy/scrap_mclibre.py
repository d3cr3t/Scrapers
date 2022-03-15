#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_mclibre.py

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

urlBaseYear = 'https://www.mclibre.org/consultar/documentacion/revistas-years/revistas-%YEAR%.html'

# Carpeta para resultados
path = "./_SCRAP_MCLIBRE"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

session = requests.Session()

for page in range(2003, 2021):

	url = urlBaseYear.replace("%YEAR%", str(page).strip())
	print("Leyendo", url)

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers)

	html = r.content
	bsObj = bs(html, "lxml")	#"html.parser")

	# Cada página es el índice de un año completo
	# Extraemos los links a las revistas individuales

	for level1 in bsObj.findAll('div', {"class": "miniaturas"}):
		for level2 in level1.findAll('a'):
			pprint.pprint(level2.attrs['href'])
			out.write(level2.attrs['href']+"\n")


out.close()
