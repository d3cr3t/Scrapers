#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_xnxx.py

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

from selenium import webdriver
browser = webdriver.Firefox()



urlBase = "https://multi.xnxx.com/category/erotica/p-"

# Carpeta para resultados
path = "./_SCRAP_XNXX"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

session = requests.Session()

picpages = []

for page in range(1, 2): #76):

	url = urlBase+str(page).strip()+"/"
	print("*** Reading", url)

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers)

	html = r.content
	bsObj = bs(html, "html.parser")

	# Cada página es el índice de un año completo
	# Extraemos los links a las revistas individuales

	for level1 in bsObj.findAll('div', {"class": "tcContainer"}):
		for level2b in level1.findAll('a', {"class": "listing"}):
			pprint.pprint(level2b.attrs['href'])
			picpages.append(level2b.attrs['href'])

	print("I got it!")

	print("Processing each gallery page....")


	for i in picpages:
		#url = "https://multi.xnxx.com/"+i
		#print("*** Reading", url)

		url = "http://multi.xnxx.com/gallery/1168432/b9ad/your_wildest_dreams/8/#lg=1&slide=8"
		print("*** Reading", url)
		try:
			browser.get("url")
		except ValueError:
			print(ValueError)
			pass

		'''		Button=''
		while not Button:
		    try:
		        Button=browser.find_element_by_name('footer')
		    except:continue
		'''
		pprint.pprint(browser)

		html = r.content
		bsObj = bs(html, "html.parser")

		print("---")

		print(html)

		browser.close()
		sys.exit(9)

		for level1 in bsObj.findAll('div', {'class': re.compile('boxImg.*')}):
			print(level1.attrs['data-src'])

'''
		for level1 in bsObj.findAll('div', {'class': 'tcContainer'}):
			for level2 in level1.findAll('img'):
				print(level2.attrs['src'])



out.close()

'''
