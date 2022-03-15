#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_kupdf.py

'''

# BS se puede instalar con pip install beautifulsoup4
# requests se instala con pip install requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import pprint
import random

urlBase = 'https://kupdf.net/categories'

session = requests.Session()

# Carpeta para resultados
path = "./_SCRAP_KUPDF"
os.makedirs(path, exist_ok=True)

listcategories = []
listpages = []
listpdfs = []
listurlfiles = []

url = urlBase
html = ''

print("Leyendo Categories", url)
print("---")

ran = str(int(random.randint(0, 9)))

headers = {
        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }

r = session.get(url, headers=headers) # verify=False) #get the response

html = r.content
bsObj = bs(html, "lxml")

# 1

for level1 in bsObj.findAll('h4', {"class": re.compile("card-title")}):
	for level2 in level1.findAll('a'):
		#print(level2.attrs['href'])
		listcategories.append(level2.attrs['href'])


# 2
print("FASE 2", "-" *80)
kk = 0
for i in listcategories:
	kk = kk + 1
	if kk<2:
		url = i
		html = ''

		category = i[27:]
		print(i, category)
		print("Leyendo", url)

		ran = str(int(random.randint(0, 9)))

		headers = {
		        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
		    }

		r = session.get(url, headers=headers) # verify=False) #get the response

		html = r.content
		bsObj = bs(html, "lxml")

		for level1 in bsObj.findAll('div', {"class": re.compile("card-image")}):
			for level2 in level1.findAll('a'):
				print(level2.attrs['href'])
				listpdfs.append([category, level2.attrs['href']])

# 3
print("FASE 3", "-" *80)

for i in listpdfs:
	url = i[1]
	actualcat = i[0]

	html = ''

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers) # verify=False) #get the response

	html = r.content
	bsObj = bs(html, "lxml")

	for level1 in bsObj.findAll('form', {"id": re.compile("form-queue")}):
		print(level1.attrs['action'])
		listurlfiles.append([actualcat, level1.attrs['action']])


# 4
print("FASE 4", "-" *80)

previouscat = "*"
for i in listurlfiles:
	url = i[1]
	actualcat = i[0]

	if actualcat != previouscat:
		try:
			out.close()
		except:
			pass

		out = open(path+"/"+actualcat+".txt", "w")
		previouscat = actualcat

	html = ''

	ran = str(int(random.randint(0, 9)))

	headers = {
	        'User-Agent': 'Mozilla/5.'+ran+' (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	    }

	r = session.get(url, headers=headers) # verify=False) #get the response

	html = r.content

	pprint.pprint(html)

	bsObj = bs(html, "lxml")

	for level1 in bsObj.findAll('a', {"href": re.compile("downloadFile")}):
		print(level1.attrs['href'])
		out.write(level1.attrs['href']+"\n")


out.close()
