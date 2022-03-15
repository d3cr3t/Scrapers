#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	scrap_grimorio.py

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

# Carpeta para resultados
path = "./_SCRAP_GRIMORIO"
os.makedirs(path, exist_ok=True)

out = open(path+"/"+"links.txt", "w")

html = ''
for line in open("grimorio.html", 'r').readlines():
	print("reading...")
	html = html+line

bsObj = bs(html, "html.parser")

for level1 in bsObj.findAll('a', href=re.compile('.*pdf')):
	print("http://elgrimorio.org/"+level1.attrs['href'])
