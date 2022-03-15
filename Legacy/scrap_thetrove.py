'''
	scrap_thetrove.py

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

urlBase = 'https://thetrove.net/Books/'

# Carpeta para resultados
path = "./_SCRAP_THETROVE"
os.makedirs(path, exist_ok=True)

session = requests.Session()


lookfor = "FLOW+MY+TEARS"

# Lectura de búsqueda

filename = "scrap_thetrove.txt"

level = 0
contentlevel = False
endlevel1 = False
nextlevel = ''

pdflist = []
pageslist = []

pageslist.append([0, ''])

for i in pageslist[level]:
	pprint.pprint(i)
	url = urlBase + i[1]
	print("Leyendo", url)

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers) # verify=False) #get the response

	html = r.content
	bsObj = bs(html, "lxml")

	# First step in each page: PDF content present? if not, get links and proceed

	countpdf = 0

	for level1 in bsObj.findAll('td', {"class": re.compile("litem_name")}):
		for level2 in level1.findAll('a', {"href": re.compile(".*pdf")}):
			countpdf = countpdf + 1
			pdflist.append([level, level2.attrs['href']])
			pprint.pprint(pdflist)
			level = level - 1

	if countpdf < 1:
		# process links
		for level1 in bsObj.findAll('td', {"class": re.compile("litem_name")}):
			for level2 in level1.findAll('a'):
				pageslist.append([level, level2.attrs['href']])
		level = level + 1
		pprint.pprint(pageslist)


	endlevel1 = True

print("OK")
