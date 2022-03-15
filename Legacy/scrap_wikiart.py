# scrap_wikiart.py 0.2
# (C) 2021 Teko
# Scrap Wikiart.org

'''
    Proceso para la lectura de las imágenes albergadas en Wikiart.org para un autor concreto.

    1. Lectura de la página del autor.
    2. Búsqueda del enlace donde se encuentran las imágenes.
    3. Búsqueda del enlace donse se muestran los enlaces a todas ellas.
    4. Lectura de cada página para leer los enlaces de las imágenes.

    En el caso de estas galerías, cada imagen consta de diversos enlaces según su calidad.
    Estos enlaces se muestran cuando el usuario hace click en la opción TODAS LAS DIMENSIONES
    generando una ventana flotante (simulada) con las opciones disponibles. Los enlaces no están
    en formato HTML, si no en un objeto Javascript, presumiblemente AngularJS.
    El objetivo es descargar la imagen de máxima resolución disponible. En algunos casos hay más
    de una, puesto que las obras pueden estar representadas por distintos grabados o pinturas.
    Para asegurar la descarga de todas ellas, hay dos opciones:

    a) Usar Selenium para interactuar con la página y hacer click en la mencionada opción.
    b) Convertir el código fuente perteneciente al objeto Javascript a una cadena de texto con
    formato JSON válido y luego convertir la misma en un objeto Python.

    En el segundo caso se han observado algunos errores de sintaxis que pueden perjudicar el
    proceso. Por ejemplo, las entidades &quot; (que deben convertirse a comillas), pueden estar
    mal escritas. Tras algunas comprobaciones manuales se detectan cadenas del tipo &ququot; que
    son erróneas. La conversión de cadena a JSON con el modilo json, curiosamente, sabe cómo
    tratar estas incidencias y tras procesar todos los enlaces de un artista no da ningún
    problema aparente.

    Teniendo todo ello en cuenta, al convertir estos datos a variables Python se pueden filtrar
    los enlaces de las imágenes por diversos criterios:

    a) El siguiente fragmento:

    {
	"_t": "ThumbnailSizesModel",
	"ImageThumbnailsModel": [{
		"Thumbnails": [{
			"SizeKB": 6,
			"Width": 210,
			"Height": 126,
			"Url": "https://uploads4.wikiart.org/00231/images/francisco-goya/a-fight-at-the-venta-nueva-2.jpg!PinterestSmall.jpg",
			"Name": "PinterestSmall"
		}, {
        .
        .
        .
		}, {
			"SizeKB": 233,
			"Width": 1920,
			"Height": 1149,
			"Url": "https://uploads1.wikiart.org/00231/images/francisco-goya/a-fight-at-the-venta-nueva-2.jpg!HD.jpg",
			"Name": "HD"
		}, {
			"SizeKB": 1482,
			"Width": 1920,
			"Height": 1149,
			"Url": "https://uploads3.wikiart.org/00231/images/francisco-goya/a-fight-at-the-venta-nueva-2.jpg",
			"Name": "Original"
		}],
        .
        .
        .

        permite observar que las imágenes de alta resolución se identifican con la clave Name igual a Original.

    b) También se cumple el siguiente patrón. Las URL de las imágenes originales nunca contienen un símbolo !

    Cualquiera de ambos métodos nos dará el link a la imagen final. El programa usa el criterio a)

    Como se puede ver, cada imagen está albergada en un servidor distinto, imposibilitanto el "cálculo" de la URL
    a partir de la página donde se alberga la imagen. Una posibilidad comprobada y descartada.

    Una vez conseguidos los enlaces de las imágenes, éstos se almacenarán en un fichero de texto links.txt en una
    carpeta que identifica al autor o artista. La descarga de las imágenes podrá realizarse más tarde con una
    herramienta tal como JDownloader o Aria. Es más eficaz que la descarga de las imágenes desde el propio programa.

    La clase bcolors se utiliza para cuestiones cosméticas. Son secuencias Escape para usar color en el terminal.

    * Una posible mejora del programa es poder indicar la ruta de la página del artista como argumento.

    REVISIONES

    0.1 Versión inicial
    0.2 Petición del artista al usuario, por medio de entrada manual, con búsqueda y selección de resultados.

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
import json

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
PAGE_ROOT = "https://www.wikiart.org"
PAGE_URL = "https://www.wikiart.org/es/"
PATH_PICTURES = "./_SCRAP_WIKIART/"
CATEGORY_NAME = 0
CATEGORY_LINK = 1
CATEGORY_PAGES = 2
NEWLINE = "\n"

ARTIST_LINK = 0
ARTIST_NAME = 1

# Modificar para el artista deseado (*)
#PAGE_ARTIST = "gustave-dore/"
#PAGE_ARTIST = "m-c-escher/"
#PAGE_ARTIST = "rene-magritte/"
#PAGE_ARTIST = "edward-hopper/"
#PAGE_ARTIST = "victor-vasarely/"
#PAGE_ARTIST = "paul-klee/"
#PAGE_ARTIST = "pablo-picasso/"
#PAGE_ARTIST = "frida-kahlo/"
#PAGE_ARTIST = "andy-warhol/"
#PAGE_ARTIST = "roy-lichtenstein/"
#PAGE_ARTIST = "vincent-van-gogh/"
#PAGE_ARTIST = "edvard-munch/"
#PAGE_ARTIST = "salvador-dali/"
#PAGE_ARTIST = "el-bosco/"
PAGE_ARTIST = "keith-haring/"

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
    os.makedirs(PATH_PICTURES, exist_ok=True)

def logo():
    try:
        os.system('clear')
    except:
        for i in range(0,30):
            print()
        pass

    print(f"{bcolors.HEADER}Scrap WikiArt 0.2{bcolors.ENDC}")
    print("-" * 80)

def read_homepage(url, list_pictures):
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
            list_pictures.append([category_name, category_link, 0])

def create_path_pictures():
    # Crea una carpeta para el artista
    print(f"Creating folder for {PAGE_ARTIST} ... ", end="")
    try:
        os.makedirs(PATH_PICTURES + PAGE_ARTIST, exist_ok=True)
        print("OK")
    except:
        print("ERR")
        pass

def search_full_list(list_pictures_pages):
    url = PAGE_URL + PAGE_ARTIST
    session = requests.Session()
    r = session.get(url)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")

    # La página donde se encuentra el enlace para ver todas las páginas
    # se puede construir:
    next_page_url = url + "all-works/text-list"

    r = session.get(next_page_url)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")
    for elements in bsObj.findAll('div', {'class': 'view-all-works'}):
        for each_work in elements.findAll('li', {'class': 'painting-list-text-row'}):
            for each_work_link in each_work.findAll('a'):
                print(PAGE_ROOT + each_work_link.attrs['href'])
                list_pictures_pages.append(PAGE_ROOT + each_work_link.attrs['href'])


def process_each_image_page(list_pictures_pages, list_pictures):
    # Cada pagina contiene un objeto Javascript con todos los posibles links
    # de las imágenes en distinta resolución. Hay que procesarlo para convertirlo
    # en datos utilizables por Python.

    out = open(PATH_PICTURES + PAGE_ARTIST + "/links.txt", "w")

    for picture_page_url in list_pictures_pages:
        picture_name = picture_page_url.split("/")
        print(f"{bcolors.HEADER}Leyendo página {bcolors.OKGREEN}{picture_name[len(picture_name)-1]}{bcolors.ENDC}")
        session = requests.Session()
        r = session.get(picture_page_url)
        html = r.content
        bsObj = BeautifulSoup(html, "html5lib")

        # lectura del objeto AngularJS
        for elements in bsObj.findAll('main', {'ng-controller': 'ArtworkViewCtrl'}):
            # conversión a JSON decodificado (se decarta la parte de la cadena que no interesa)
            json_tmp = elements.attrs['ng-init'][22:]
            json_tmp = json_tmp[:-1]
            pictures_data = json.loads(json_tmp)

            # Para encontrar las posibles imágenes disponibles hay que atravesar
            # el objeto formato por diccionarios y listas:
            npic = 0
            for n in pictures_data['ImageThumbnailsModel']:
                # Si hay más de una imagen, recorremos las miniaturas de cada una
                for i in n['Thumbnails']:
                    if i['Name'] == 'Original':
                        npic += 1
                        print(f"{npic}: {bcolors.OKBLUE}{i['Width']}x{i['Height']}{bcolors.ENDC}")
                        out.write(i['Url'] + NEWLINE)
    out.close()
    print()

def ask_for_search():
    print()
    print("Bienvenido al scraper de Wikiart.\nIntroduce el nombre del artista que buscas e intentaré encontrarlo.")
    artist_search ='*'
    while artist_search > '':
        artist_search = input("Escribe su nombre lo más sencillo y directo posible.\nPor ejemplo, 'dali', 'munchen', 'dore': ")
        search_artist(artist_search)

def search_artist(artist_name):
    list_results = []
    na = 1

    session = requests.Session()
    url = "https://www.wikiart.org/es/Search/" + artist_name.replace(" ", "%20")
    r = session.get(url)
    html = r.content
    bsObj = BeautifulSoup(html, "html5lib")
    for elements in bsObj.findAll('ul', {'class': 'wiki-artistgallery-container.*'}):
        for level2 in elements.findAll('div', {'class': 'artist-name'}):
            for level3 in level2.findAll('a'):
                list_results.append([level3.attrs['href'], level3.attrs['title']])

    if len(list_results) > 0:
        print()
        print("Selecciona el artista:")
        for j in list_results:
            print(f"{na}: {j[ARTIST_NAME]}")
        print()
        select_artist = input("Escribe el número del artista a procesar:")
    else:
        print("No se han encontrado resultados. Inténtalo de nuevo.")



if __name__ == "__main__":
    list_pictures_pages = []
    list_pictures = []

    logo()
    init_app()
    #ask_for_search()
    read_homepage(PAGE_URL + PAGE_ARTIST, list_pictures)
    create_path_pictures()
    search_full_list(list_pictures_pages)
    process_each_image_page(list_pictures_pages, list_pictures)

    print()
    print("OK. Proceso terminado. Utiliza JDownloader o similar para procesar los enlaces guardados.")
