'''
    Scrap tutocomputer web site for programming IT books and their details.

    1. Index
        This site has several categories, from Cobol to Autocad. Each cateogry has a lot of books
        in a list, with no pagination at all (easier!). So, frist step, read the categories and their
        direct links:

        element ASIDE with class="sidebar" contents the category list
            LI element
                A element has the HREF info to get the category index list

        Inside any category:

            H2 class="post-title"
                A HREF has a link like
                    ./programming/19-cobol-21-days.html
                                  --
                                  ^
                                  this is the unique ID for each book
            
            the download link has the form:
                https://tuto-computer.com/download-file-19.html
                                                        __
                                                        ^
                                                        so, we must build the link from the unique ID

    Prior to execution you must create a couple of folders in your Home directory:
        scraps/tuto-computer/data
        scraps/tuto-computer/links

    Libraries used:
        Beautifulsoup
        ArgumentParser
        requests
        json


'''


from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import pprint
import pathlib
import random
import json

# ArgumentParser - https://pymotw.com/3/argparse/
from argparse import ArgumentParser


config = {
    "urls": {
        "root": "https://tuto-computer.com/",
        "base": "https://tuto-computer.com/category/programming-it",
        "book": "https://tuto-computer.com/get1/"
        },
    "url_page_suffix": "?page=",
    "json_path_prefix": pathlib.Path.home() / "scraps/tuto-computer/data/",
    "json_prefix": "json_",
    "json_suffix": ".json",
    "json_files": {
        "index": "index_",
        "issues": "issues_",
    },
    "link_path_prefix": pathlib.Path.home() / "scraps/tuto-computer/links/",
    "link_prefix": "link_",
    "link_suffix": ".txt",
    "link_files": {
        "links": "links_"
    }
 }

dict_issues = {}

def check_args():
    global fase
    global thread

    # Args
    parser = ArgumentParser()

    parser.add_argument("-f", "--fase", dest="fase", default=0, help="fase 0: init, fase 1: details / links")

    args = parser.parse_args()
    fase = int(args.fase)
    
    if fase <0 or fase>1:
        print("ERR: fase must be a value between 0 and 1.")
        sys.exit(1)

def check_paths():
    global config

    try:
        os.makedirs(config["json_path_prefix"], exist_ok=True)
    except:
        return False
    
    return True

def create_csv(file):
    global config

    try:
        path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"][file] + config["json_suffix"])
        print(path)
        path.touch()
        return path    
    except:
        print("ERR: Cannot create an instance of file path!", path)
        sys.exit(1)

def create_link(file):
    global config

    try:
        path = config["link_path_prefix"] / (config["link_prefix"] + config["link_files"][file] + config["link_suffix"])
        print(path)
        path.touch()
        return path    
    except:
        print("ERR: Cannot create an instance of file path!", path)
        sys.exit(1)

def read_index_page():
    global config
    global list_links

    category_link = ''
    list_links = []

    url = config["urls"]["root"]
    print(url)

    session = requests.Session()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    r = session.get(url, headers=headers) # verify=False) #get the response

    if r.status_code != 200:
        print("URL NOT FOUND!", r.status_code)
        pprint.pprint(r)
        sys.exit(1)
    else:
        html = r.content
        bsObj = bs(html, "lxml")
        for level1 in bsObj.findAll("aside", {"class": "sidebar"}):
            for level2 in level1.findAll("li"):
                for level3 in level2.findAll("a"):
                    category_link = level3.attrs["href"]
                    list_links.append(category_link)


def get_detail_issue(book_id):
    global config
    global dict_issues

    url = config["urls"]["book"] + str(book_id).strip()
    print("**** PROCESS", url)

    retry = True
    n_tries = 0

    while retry is True:
        try:
            r = requests.get(url)
            retry = False
        except:
            n_tries = n_tries + 1
            print(f"ERROR, retry {n_tries}")
            if n_tries < 10:
                pass
            else:
                print("TOO MANY RETRIES. ABORT.")
                sys.exit(1)

    if r.status_code != 200:
        print(f"ERR: page {url} cannot be read.")
    else:
        print("Processing issue... looking for Download button...")
        html = r.content
        bsObj = bs(html, "lxml")

        book_download_link = ''

        for level1 in bsObj.findAll("a", {"class": re.compile("Download btn*")}):
            tmp_data = level1.attrs["href"]

            if "drive.google.com" in tmp_data:
                book_download_link = tmp_data
            else:
                book_download_link = config["urls"]["book"] + tmp_data[1:]

            print("   ", book_download_link)
            dict_issues[book_id] = {
                "book_download_link": book_download_link
            }


def read_book_detail_page():
    global config
    global records_processed
    global dict_issues
    global list_links
    
    list_books = []
    dict_data = {}

    retry = True
    n_tries = 0

    session = requests.Session()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    out_path = create_link("links")   

    for i in list_links:
        print("URL", i)
        '''
                H2 class="post-title"
                A HREF has a link like
                    ./programming/19-cobol-21-days.html
                                  --
                                  ^
                                  this is the unique ID for each book
        '''
        n_tries = 0
        retry = True
        while retry is True:
            url = config["urls"]["root"] + i[2:]
            print(url, "<<<<<<<")
            try:
                r = session.get(url, headers=headers) # verify=False) #get the response
                retry = False
            except:
                n_tries = n_tries + 1
                print(f"ERROR, retry {n_tries}")
                if n_tries < 10:
                    pass
                else:
                    print("TOO MANY RETRIES. ABORT.")
                    sys.exit(1)

        if r.status_code != 200:
            print(f"ERR: page {url} cannot be read.")
        else:
            print("Processing issue... looking for Download button...")
            html = r.content
            bsObj = bs(html, "lxml")
            for level1 in bsObj.findAll("h2", {"class": "post-title"}):
                for level2 in level1.findAll("a"):
                    # ./programming/19-cobol-21-days.html
                    tmp_data = level2.attrs["href"].split("/")
                    tmp_data2 = tmp_data[2].split("-")
                    url_issue = config["urls"]["root"] + "/download-file-" + str(tmp_data2[0]) + ".html"
                    print(url_issue)
                    list_books.append(url_issue)

    with out_path.open(mode="w") as file:
        for i in list_books:
            file.write(i+"\n")
    
    file.close()


def read_issues_links(letter, path):
    global config

    in_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["issues"] + str(letter).strip() + config["json_suffix"])
     
    pprint.pprint(in_path)

    out_path = path

    pprint.pprint(out_path)

    with in_path.open(mode="r") as file:
        dict_data = json.loads(file.read())
 
    file.close()

    with out_path.open(mode="w") as file:
        for d in dict_data:
            tmp_link = dict_data[d]["image_large"]
            if tmp_link>'':
                file.write(tmp_link+"\n")
    
    file.close()


def main():
    global config
    global fase
    global records_processed
    global list_links

    print("Scrap tuto-computer site")
    check_args()

    if check_paths() is False:
        print("ERR: check config!", config["json_path_prefix"])
        sys.exit(1)

    records_processed = 0

    if fase == 0:
        read_index_page()
        read_book_detail_page()



if __name__ == "__main__":
    main()

