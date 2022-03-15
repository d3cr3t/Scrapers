'''
	scrap_fifa.py

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

urlBase = 'https://www.fifaindex.com/es/team/240/atl%C3%A9tico-madrid/'

urlitem = "https://www.amazon.es/Flow-My-Tears-Policeman-Said/dp/1780220413/"

# Carpeta para resultados
path = "./_SCRAP_FIFA"
os.makedirs(path, exist_ok=True)

session = requests.Session()


for page in range(1, 2):
	url = urlBase
	print("Leyendo", url)


	ran = str(int(random.randint(0, 9)))

	headers = {
    	'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }

	r = session.get(url, headers=headers) # verify=False) #get the response

	html = r.content
	bsObj = bs(html.decode("utf-8", "replace"), "html.parser")	#"html.parser")

	#pprint.pprint(html.decode("utf-8", "replace"))

	for level1 in bsObj.findAll('div', {"class": "pl-3"}):
		#pprint.pprint(level1)
		for level2 in level1.findAll('h1'):
			pprint.pprint(level2)

	fh = open("caca.txt", "a")
	fh.write(str(level2))
	fh.close()

	sys.exit(1)
	print("TITLE")
	for level1 in bsObj.findAll('h1', {"id": "title"}):
		for level2 in level1.findAll('span', {'id': "productTitle"}):
			print(level2.get_text())

	print("Página OK")

	out = open("_scrap_amazon_debug.html", "wb")
	out.write(html)
	out.close()


sys.exit(1)

# Bucle para encontrar los enlaces directos a libros

for url in listEbooks:
	print("Leyendo ebooks...", url)
	r = session.get(url)
	html = r.content
	bsObj = BeautifulSoup(html, "html.parser")
	for level1 in bsObj.findAll('a', {'class': re.compile("download-link")}):
		ebooklink = level1.attrs['href']
		if ebooklink not in listEpubs:
			print("ebook:", ebooklink)
			listEpubs.append(ebooklink)

print("Ultima lectura, links directos")

for ebookurl in listEpubs:
	r = session.get(ebookurl)
	html = r.content
	bsObj = BeautifulSoup(html, "html.parser")
	for level1 in bsObj.findAll('a', {'class': re.compile("download-link")}):
		ebooklink = level1.attrs['href']
		print(ebooklink)
		with open(path+"/"+filename, 'a') as handler:
			handler.write(ebooklink+"\n")

print("Links capturados en: ", path+"/"+filename)
print ("OK")
