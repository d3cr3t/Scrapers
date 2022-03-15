# Scrap lunatic site

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome
from seleniumrequests import Firefox
from bs4 import BeautifulSoup

from requests_html import HTMLSession

import time
import pprint
import re
import requests
import sys
import os
import subprocess
from pathlib import Path
from os.path import expanduser
from http.cookiejar import MozillaCookieJar

import certifi
import urllib3

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

urllib3.disable_warnings()

PATH_BOOKS = "./_SCRAP_LUNATIC/"
os.makedirs(PATH_BOOKS, exist_ok=True)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

from collections import defaultdict
cookiesdc = defaultdict(lambda : None)

if sys.version_info < (3,):
    from cookielib import Cookie, MozillaCookieJar
else:
    from http.cookiejar import Cookie, MozillaCookieJar

def load_cookies():
    home = expanduser('~')
    cookies = home+'/Sites/wicked/cookies.txt'
    jar = MozillaCookieJar(cookies)
    jar.load()
    return jar


def waiter(timetowait, message):
    print(bcolors.OKGREEN + message + bcolors.ENDC, "("+str(timetowait).strip()+")")
    time.sleep(timetowait)

def parse_a_page(html, np):
    global listGalleries
    global gallery_prefix

    print("SOUP... PAGE #", np)
    bsObj = BeautifulSoup(html, "html.parser")

    nn = 0
    print("ANALIZYNG SOUP...")

    for level1 in bsObj.findAll('div', {'class': 'featimage--info'}):
        nn = nn+1
        #print(nn, "LEVEL 1")
        for level2 in level1.findAll('div', {"class": "profile--name fs--14"}):
            #print("LEVEL 2.1")
            for level3 in level2.findAll('a'):
                chickGallery = level3.get_text()
        for level2 in level1.findAll('div', {"class": re.compile("profile--title text-gray")}):
            #print("LEVEL 2.2")
            for level3 in level2.findAll('a'):
                #print("LEVEL 3")
                titleGallery = level3.get_text()
                linkGallery = level3.attrs['href']

        listGalleries.append([normalizeName(chickGallery).upper(), linkGallery, titleGallery.strip().upper()])
        #print(nn, [normalizeName(chickGallery).upper(), linkGallery, titleGallery.strip().upper()])

def normalizeName(entry_name):
    """Update name to avoid symbols."""
    # Cut sufixes with usernames

    try:
        tmpExt = entry_name.split('.')[-1]
        tmpMain = entry_name[0:-len(tmpExt)-1]

        if tmpMain == '':
            tmpMain = tmpExt
            tmpExt = ''

        tmpMain2 = tmpMain.split("@")
        newName = tmpMain2[0].replace(".","")

        newName = newName.replace('&', 'and')
        newName = newName.replace('❤️', 'a')


        newName = newName.replace('(', '')
        newName = newName.replace(')', '')
        newName = newName.replace('[', '')
        newName = newName.replace(']', '')
        newName = newName.replace("#", '')
        newName = newName.replace("~", '')
        newName = newName.replace('?', '')
        newName = newName.replace('¿', '')
        newName = newName.replace('!', '')
        newName = newName.replace('¡', '')
        newName = newName.replace("*", '')
        newName = newName.replace("{", '')
        newName = newName.replace("}", '')
        newName = newName.replace("+", '_')

        try:
            newName = unidecode(newName)
        except:
            pass

        newName = newName.replace(',', '')
        newName = newName.replace(';', '')
        newName = newName.replace("\\", '')
        newName = newName.replace("'", '-')
        newName = newName.replace("_", '-')
        newName = newName.replace(' ', '-')
        newName = newName.replace('---', '-')
        newName = newName.replace('--', '-')

        while newName.startswith(" "):
            newName = newName[1:]

        while newName.endswith(" "):
            tnewName = newName[:-1]

        while newName.startswith("_"):
            newName = newName[1:]

        while newName.endswith("_"):
            newName = newName[:-1]

        while newName.startswith("-"):
            newName = newName[1:]
        while newName.endswith("-"):
            newName = newName[:-1]

    #    if len(newName)> MAX_FILENAME:
    #        newName = newName[0:MAX_FILENAME-5]

        if len(tmpExt)>0:
            newName = newName+"."+tmpExt

        newName = newName.lower()
    except:
        newName = entry_name
        pass

    return newName

listLinks = []

print("SCRAP LUNATIC SITE")
print("=" * 80)

print("OPEN SESSION...")
driver = Chrome()
#driver = Firefox()

print("HOMEPAGE...")
driver.implicitly_wait(30)
driver.get("https://www.lunaticai.com/")
#driver.get("https://www.lunaticai.com/search?q=python")

endofpage = False

numelements = 0
previousnum = 0
n = 0
while endofpage is False:
    try:
        elem = driver.find_element_by_xpath("//a[@class='loadMore__btn btn']").click()
        waiter(12, "CLICKED")
    except:
        endofpage = True
        #pass

html = driver.page_source
waiter(10, "END OF CLICKS")
bsObj = BeautifulSoup(html, "html.parser")

for level1 in bsObj.findAll("a", {"class": "aPost__thumb"}):
    n = n +1
    print(level1.attrs['href'])
    listLinks.append(level1.attrs['href'])

print("BOOKS COUNTER", len(level1), n)

print("SECOND LEVEL PAGES....")

session = requests.Session()

listDown = []

nn = 1
for i in listLinks:
    r = session.get(i)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")
    for child in bsObj.findAll('a', {'href': re.compile('https://www.lunaticai.com/p/download.*')}):
        print(nn, child.attrs['href'])
        listDown.append(child.attrs['href'])
    '''
    for daughter in bsObj.findAll("div", {'class': 'post-body'}):
        desc = daughter.get_text()
        print(desc)
    '''
    nn=nn+1

print("THIRD LEVEL AND LAST")

with open(PATH_BOOKS+"/tmp_links", 'w') as handler:
    handler.write('')

nn = 1
for i in listDown:
    try:
        r = session.get(i)
        html = r.content
        bsObj = BeautifulSoup(html, "html5lib")
        for child in bsObj.findAll('a', {'href': re.compile('https://drive.google.com/file.*')}):
            tmplink = child.attrs['href'].replace("/view?usp=sharing", "&export=download")
            print(nn, tmplink)
            with open(PATH_BOOKS+"/tmp_links", 'a') as handler:
                handler.write(tmplink+"\n")
            nn=nn+1
    except:
        pass

'''
actual_dir = os.getcwd()

os.chdir(PATH_BOOKS+"/")
staria = subprocess.call(["/usr/local/bin/aria2c", "-i tmp_links", "-c", "--allow-overwrite=false", "--auto-file-renaming=false"])
os.chdir(actual_dir)
'''
print("CLOSING SESSION...")
driver.close()

print("OK")


'''

https://drive.google.com/file/d/1zsgsxJB1fpp4O1AM1y6spN8DStBEhcT1

https://drive.google.com/u/0/uc?id=1zsgsxJB1fpp4O1AM1y6spN8DStBEhcT1&export=download

https://drive.google.com/u/0/uc?export=download&confirm=21rF&id=1z-7wC6DMSssYka9V4_zMA9cumIsdz7Xr


https://drive.google.com/u/0/uc?export=download&confirm=1zsgsxJB1fpp4O1AM1y6spN8DStBEhcT1

'''
