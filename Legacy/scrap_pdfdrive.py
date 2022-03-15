# scrap_pdfdrive.py 0.1
# (C) 2021 Teko
# Scrap PDFDrive.com

'''
    Proceso para la lectura de los libros albergados en PDFDrive.com

    1. Lectura de las diferentes categorías.
    2. Creación de la carpeta para descargar los ficheros de cada una.
    3. Lectura del número de páginas de cada categoría y su link.
    4. Lectura de cada categoría completa y generación de lista de links para cada una.

    Una vez tenemos la lista de links de cada categoría, el paso siguiente sería
    leer el mismo y descargar el documento PDF, EPUB, etc. En el caso de PDFDrive,
    no es tan sencillo, ya que el botón de Descarga se genera de forma dinámica al
    cabo de unos segundos, después de cargar el código principal de la página, es decir,
    el HTML inicial. Esto imposibilita el uso de requests junto con BeautifulSoup. Sería
    necesiario usar Selenium. Como el uso de esa librería ralentiza todo el proceso
    la mejor opción es seguir el scrap fuera de este programa:

    - Utilizar JDownloader para cargar las listas de enlaces de una categoría.
    - JDownloader no detectará nada en la primera lectura de los links, y preguntará
    si queremos un análisis profundo. La respuesta debe ser que sí.
    - JDownloader encontrará enlaces a los libros en PDF, etc. pero con la salvedad de
    que encontrará no sólo el enlace del libro al que pertenece el link en cuestión, si no
    también a los que PDFDrive sugiere como "similares".
    - El resultado es que, por ejemplo, en la category Technology, que en teoría hay 200
    enlaces a libros, dada la lista de enlaces a JDownloader, éste produce más de 1.000
    resultados. Esto es porque las sugerencias de PDFDrive están cruzadas entre categorías.

    Si se quieren resultados más ajustados a la "realidad" de cada categoría, hay que usar
    Selenium, tratar el botón de Descarga y procesar el fichero único (puede que exista más
    de uno) y descargarlo, o guardar su enlace para descarga posterior.

'''

# Módulos básicos para web scraping
# Se pueden instalar con pip:
#   pip install bs4
#   pip install requests
#   pip install requests_html

from bs4 import BeautifulSoup
from requests_html import HTMLSession

# Modulos para uso del sistema, regEx, etc
import time
import pprint
import re
import requests
import sys
import os

from pathlib import Path
from os.path import expanduser

# Módulos para certificados de seguridad, no siempre necesarios
# Se pueden instalar con pip:
#   pip install certifi
#   pip install urllib3

import certifi
import urllib3

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

urllib3.disable_warnings()

# Constantes
PAGE_URL = "https://www.pdfdrive.com/"
PATH_BOOKS = "./_SCRAP_PDFDRIVE/"
CATEGORY_NAME = 0
CATEGORY_LINK = 1
CATEGORY_PAGES = 2
NEWLINE = "\n"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def waiter(timetowait, message):
    print(f"{bcolors.OKGREEN} {message} WAIT({timetowait}){bcolors.ENDC}")
    time.sleep(timetowait)

def init_app():
    os.makedirs(PATH_BOOKS, exist_ok=True)

def logo():
    try:
        os.system('clear')
    except:
        for i in range(0,30):
            print()
        pass

    print(f"{bcolors.HEADER}Scrap PDFDrive 0.1{bcolors.ENDC}")
    print("-" * 80)

def read_homepage(url, list_categories):
    print("HOMEPAGE...")
    session = requests.Session()
    r = session.get(url)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")

    # El elemento DIV con la clase categories-list contiene los enlaces a cada
    # categoría principal.
    for categories_block in bsObj.findAll('div', {'class': 'categories-list'}):
        for each_category in categories_block.findAll('a', {'href': re.compile('^/category/.*')}):
            category_link = each_category.attrs['href']
            for category_title in each_category.findAll('p'):
                category_name = category_title.get_text()
            list_categories.append([category_name, category_link, 0])

def create_path_categories(list_categories):
    # Crea una carpeta para cada categoría, para albergar la lista de links
    # de cada categoría. Más tarde puede usarse esta carpeta para descargar
    # los contenidos.
    PATH_BOOKS = "./_SCRAP_PDFDRIVE/"
    for i in list_categories:
        print(f"Creating folder for {PATH_BOOKS}/{i[CATEGORY_NAME]} category... ", end="")
        try:
            os.makedirs(PATH_BOOKS + i[CATEGORY_NAME], exist_ok=True)
            print("OK")
        except:
            print("ERR")
            pass

def read_category_pages(category):
    url = PAGE_URL + category[CATEGORY_LINK]
    session = requests.Session()
    r = session.get(url)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")
    last_page = 1

    # El elemeto DIV con la clase Zebra_Pagination contiene la botonera inferior
    # de la página para navegar entre las páginas de cada categoría. Se lee la
    # página más alta para saber cuántas páginas tiene cada categoría.
    for elements in bsObj.findAll('div', {'class': 'Zebra_Pagination'}):
        for page_numbers in elements.findAll('a'):
            test_integer = page_numbers.get_text()
            try:
                convert_integer = int(test_integer)
                if convert_integer > last_page:
                    last_page = convert_integer
            except:
                pass
    print(f"Category {category[CATEGORY_NAME]} has {last_page} pages.")
    return last_page

def read_category_pages_counter(list_categories):
    # Se añade el contador de páginas a la lista de categorías ya leída.

    for index_category, category in enumerate(list_categories):
        page_counter = read_category_pages(category)
        list_categories[index_category][CATEGORY_PAGES] = page_counter

def read_pages_by_category(list_categories):
    # Los links resultantes para cada categoría se almacenan en la
    # carpeta correspondiente, en un fichero llamado links.txt

    for category in list_categories:
        out = open(PATH_BOOKS + category[CATEGORY_NAME] + "/links.txt", "w")
        last_page = category[CATEGORY_PAGES]
        for k in range(1, last_page):
            url = PAGE_URL + category[CATEGORY_LINK] + "/p" + str(k).strip() + "/"
            print(f"Leyendo página {url}")
            session = requests.Session()
            r = session.get(url)
            html = r.content
            bsObj = BeautifulSoup(html, "html5lib")

            # El elemento DIV con la clase files-new y dentro del mismo
            # el elemento DIV con la clase file-right contiene el enlace
            # previo de cada libro. Desde aquí, si se quiere, se puede usar
            # Selenium para usar el botón Descargar, esperar a los links de los
            # libros en formato PDF, EPUB, etc. y descargarlos directamente.
            # En este caso, se guarda el link en un fichero de texto para ser
            # procesado posteriormente con JDownloader o cualquier otro gestor
            # de descargas que soporte el examen en profundidad de cada link.

            for elements in bsObj.findAll('div', {'class': 'files-new'}):
                for book_rows in elements.findAll('div', {'class': 'file-right'}):
                    for book_link in book_rows.findAll('a'):
                        print(book_link.attrs['href'])
                        out.write(PAGE_URL + book_link.attrs['href'] + NEWLINE)

        out.close()
        print()



if __name__ == "__main__":
    list_categories = []

    logo()

    init_app()

    read_homepage(PAGE_URL, list_categories)

    create_path_categories(list_categories)

    read_category_pages_counter(list_categories)

    read_pages_by_category(list_categories)

    print()
    print("OK. Proceso terminado. Utiliza JDownloader o similar para procesar los enlaces guardados.")
