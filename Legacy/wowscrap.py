'''
	wowscrap.py

	Vamos a leer links de libros en Wow Ebook

	para ello, primero determinaremos lo que hay que capturar y procesar:

	Link inicial: http://www.wowebook.co
'''

# BS se puede instalar con pip install beautifulsoup4
# requests se instala con pip to install requests

from bs4 import BeautifulSoup
import requests
import re
import pprint
import os

# Página inicial, indice en la home page
# En la barra de menús vemnos una opción CATEGORIES
'''
	Este es el elemento HTML que nos interesa:

	El primer nivel sería el elemento li con la clase page_item
	(abreviado a dos categorías para comodidad, el método es el mismo)


<li class="page_item"><a href="#categories" title="Categories">Categories</a>
	<ul class="children">
		<li class="cat-item cat-item-326"><a href="https://www.wowebook.co/category/algorithms-cryptography/" title="Algorithms &amp; Cryptography">Algorithms &amp; Cryptography</a></li>
		<li class="cat-item cat-item-317"><a href="https://www.wowebook.co/category/business-management/" title="Business &amp; Management">Business &amp; Management</a></li>
	</ul>
</li>
'''

listCategories = []
listEbooks = []

urlHome = 'https://www.wowebook.co'

# Carpeta para resultados
path = "./_wowebooks"
os.makedirs(path, exist_ok=True)


session = requests.Session()

# Leemos la página y procesamos la lista de categorías
# Conservamos el link, opcionalmente el título de la categoría


r = session.get(urlHome)
html = r.content
bsObj = BeautifulSoup(html, "html.parser")

print("Home cargada")

for level1 in bsObj.findAll('li', {"class": "page_item"}):
	for level2 in level1.findAll('li', {"class": re.compile("cat-item*")}):
		for level3 in level2.findAll('a'):
			listCategories.append([level3.attrs['href'], level3.get_text()])

#pprint.pprint(listCategories)

# Bucle para leer categoría por categoría, y dentro de cada cual, todas las páginas de libros

for cat in listCategories:
	# Lectura de primera página de categoría
	print("Leyendo", cat[1], ": ", end='')
	r = session.get(cat[0])
	html = r.content
	bsObj = BeautifulSoup(html, "html.parser")
	lastPage = 1
	# Página final? buscamnos el último botón de navegación que corresponde al último elemento a href del div
	for level1 in bsObj.findAll("div", {"class": "wpmn_page_navi"}):
		for level2 in level1.findAll("a"):
			lastPageTmp = level2.attrs['href']
		lastPage = lastPageTmp.split("/")
		lastPage = int(lastPage[6])

	print(lastPage, "páginas")

	# Bucle de categoría, desde la página 1 hasta lastPage
	# La primera página ya la tenemos, se puede aprovechar o no
	# Para no complicarlo, leemos de la página 1 hasta la última obtenida en lastPage
	for i in range(1, lastPage+1):
		url = cat[0]+"page/"+str(i)
		print("Leyendo", url)
		filename = cat[1].replace(" ", "-")+".txt"
		r = session.get(url)
		html = r.content
		bsObj = BeautifulSoup(html, "html.parser")
		for level1 in bsObj.findAll('a', {'rel':'bookmark'}):
			urlEbook = level1.attrs['href']
			# Leemos detalle del libro, buscamos el botón DOWNLOAD
			# Es posible que algún libro no lo tenga
			# El elemento a encontrar es:
			# <a class="maxbutton-1 maxbutton" target="_blank" rel="noopener" href="http://ul.to/lifqlfct"><span class="mb-text">DOWNLOAD</span></a>
			print(cat[1], "buscando link en", urlEbook)
			r2 = session.get(urlEbook)
			html2 = r2.content
			bsObj2 = BeautifulSoup(html2, "html.parser")
			for sublevel in bsObj2.findAll('a', {"rel":"noopener"}):
				urlDownload = sublevel.attrs['href']
				print("-- encontrado", urlDownload)
				with open(path+"/"+filename, 'a') as handler:
					handler.write(urlDownload+"\n")

# Terminado el proceso, tenemos una serie de ficheros de texto en
# la carpeta _wowebooks que podemos usar con cualquier gestor de descargas
# como JDownloader, etc.
# En este caso, recomiendo crear una cuenta en Alldebrid.com y activarla
# en JDownloader para saltarse las limitaciones de las cuentas gratis y los
# captcha.
