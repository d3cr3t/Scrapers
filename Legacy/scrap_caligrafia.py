#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_caligrafia.py
	(c) 2021 Teko

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

urlBase = 'https://fichasdecaligrafia.com/'

session = requests.Session()

# Carpeta para resultados
path = "./_SCRAP_CALIGRAFIA"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

listpages = []
listpdfs = []

print("Scrap Caligrafia 0.1 - (c) Teko")
print("-" * 80)

# Bucle 1: pasa por todas las páginas índice

for i in range(1,22):
	url = urlBase+"page/"+str(i).strip()+"/"
	html = ''

	print(f"Leyendo página {i} {url}")

	# Creamos una cabecera on un elemento aleatorio para que el sitio Web nos vea como un cliente diferente a cada llamada
	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers)

	html = r.content
	bsObj = bs(html, "lxml")

	for level1 in bsObj.findAll('div', {"class": re.compile("post-image")}):
		for level2 in level1.findAll('a'):
			# print(level2.attrs['href'])
			listpages.append(level2.attrs['href'])

# Bucle 2: pasa por cada página individual extraída anteriormente

for i in listpages:
	url = i
	html = ''

	print(f"Leyendo ficha: {url}")

	# Las páginas de descarga son del formato:
	# https://fichasdecaligrafia.com/?smd_process_download=1&download_id=2370

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers)

	html = r.content
	bsObj = bs(html, "lxml")

	for level1 in bsObj.findAll('a', {"href": re.compile(".*download.*")}):
		# print(level1.attrs['href'])
		listpdfs.append(level1.attrs['href'])
		out.write(level1.attrs['href']+"\n")

out.close()

print("-" * 80)
print(f"Proceso terminado. Encontrarás los links en el fichero {path}/links.txt")
print("Puedes descargar los archivos con la utilidad aria:")
print("    aria2c -i links.txt")
print()
