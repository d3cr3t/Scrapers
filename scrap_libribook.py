'''
    Scrap libribook web site for programming IT books and their details.

    Go to your home root directory and create this folders struct:

    /scraps/
        libribook/
            data
            links

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
        "root": "https://libribook.com",
        "base": "https://libribook.com/category/programming-it",
        "book": "https://libribook.com/get1/"
        },
    "url_page_suffix": "?page=",
    "json_path_prefix": pathlib.Path.home() / "scraps/libribook/data/",
    "json_prefix": "json_",
    "json_suffix": ".json",
    "json_files": {
        "index": "index_",
        "issues": "issues_",
    },
    "link_path_prefix": pathlib.Path.home() / "scraps/libribook/links/",
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

    parser.add_argument("-f", "--fase", dest="fase", default=0, help="fase 0: init, fase 1: details")

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

def read_index_page(path):
    global config

    max_page = 0

    url = config["urls"]["base"]

    r = requests.get(url)

    if r.status_code != 200:
        print("URL NOT FOUND!")
        sys.exit(1)
    else:
        html = r.content
        bsObj = bs(html, "lxml")

        for level1 in bsObj.findAll("li", {"class": "PagedList-skipToLast"}):
            for level2 in level1.findAll("a"):
                tmp_data = level2.attrs["href"].split("=")
                try:
                    max_page = int(tmp_data[1])
                except:
                    print("CANNOT READ MAX PAGE!")
                    sys.exit(1)

    list_links = []
    list_data = []
    dict_data = {}

    for i in range(1, max_page + 1):
        url_page = url + "?page=" + str(i).strip()
        print(url_page)
        print("-" * 80)
        
        retry = True
        n_tries = 0

        while retry is True:
            try:
                r = requests.get(url, params={'page':str(i).strip()})
                retry = False
            except:
                print(f"ERROR GETTING URL. Retry {n_tries}")
                if n_tries < 10:
                    pass
                else:
                    sys.exit(1)

        if r.status_code != 200:
            print("END OF PAGE INDEX LOOP")
        else:
            html = r.content
            bsObj = bs(html, "lxml")

            for level1 in bsObj.findAll("div", {"class": "content"}):
                book_title = ''
                book_link = ''
                book_id = ''
                for level2 in level1.findAll("h4"):
                    for level3 in level2.findAll("a"):
                        book_title = level3.get_text()
                        book_link = level3.attrs["href"]
                        tmp_data = book_link.split("/")
                        book_id = tmp_data[2]

                print(f"Page {i} - {book_id} - {book_title}")

                dict_data[book_id] = {
                    "id": book_id,
                    "book_link": book_link,
                    "book_title": book_title,
                    }


 
    print(f"SAVING DATA...")
    
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_data, file)
    
    file.close()

def read_number_page():
    global config
    global thread

    path = create_csv("index")
    read_index_page(path)

def get_index_data():

    read_number_page()

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

    dict_data = {}

    in_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["index"] + config["json_suffix"])
     
    with in_path.open(mode="r") as file:
        dict_data = json.loads(file.read())
 
    file.close()

    out_path = create_link("links")   

    for i in dict_data:
        url_issue = dict_data[i]["book_link"]
        book_id = dict_data[i]["id"]
        get_detail_issue(book_id)

    with out_path.open(mode="w") as file:
        for d in dict_issues:
            tmp_link = dict_issues[d]["book_download_link"]
            if tmp_link>'':
                file.write(tmp_link+"\n")
    
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

    print("Scrap libribook site")
    check_args()

    if check_paths() is False:
        print("ERR: check config!", config["json_path_prefix"])
        sys.exit(1)

    records_processed = 0

    if fase == 0:
        get_index_data()
    if fase == 1:
        read_book_detail_page()



if __name__ == "__main__":
    main()

