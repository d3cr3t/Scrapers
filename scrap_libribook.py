'''
    Scrap libribook web site for programming IT books and their details.
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
        "images": "images_"
    }
 }

dict_issues = {}

def check_args():
    global fase
    global thread

    # Args
    parser = ArgumentParser()

    parser.add_argument("-f", "--fase", dest="fase", default=0, help="fase 0: init, fase 1: details, fase 2: image links")
    parser.add_argument("-t", "--thread", dest="thread", default=0, type=int, help="0: complete, 1-5: sector to process (from 1 to c...)")

    args = parser.parse_args()
    fase = int(args.fase)
    if args.thread <0 or args.thread>5:
        print("ERR", "-t parameter must be 0 to 5.")
        sys.exit(1)
    else:
        thread = args.thread
    

    if fase <0 or fase>2:
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

def create_link(file, letter):
    global config

    try:
        path = config["link_path_prefix"] / (config["link_prefix"] + config["link_files"][file] + str(letter).strip() + config["link_suffix"])
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
        
        r = requests.get(url, params={'page':str(i).strip()})

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

    r = requests.get(url)

    if r.status_code != 200:
        print(f"ERR: page {url} cannot be read.")
    else:
        print("Processing issue... looking for Download button...")
        html = r.content
        bsObj = bs(html, "lxml")

        book_download_link = ''

        for level1 in bsObj.findAll("a", {"class": re.compile("Download btn*")}):
            tmp_data = level1.attrs["href"]
            book_download_link = config["urls"]["book"] + tmp_data
            print("   ", book_download_link)
            dict_issues[book_id] = {
                "book_download_link": book_download_link
            }

def get_series_issues(dict):
    global config
    global records_processed

    edition_type = ''
    about_this_edition = ''
    story = ''

    issue_error = False
    id_serie = dict["id"]

    url = config["urls"]["root"] + dict["link_detail"]   # not detail of issue, instead, of complete serie
    r = requests.get(url)

    if r.status_code != 200:
        print(f"ERR: page {url} cannot be read.")
        issue_error = True
    else:
        print("Processing serie (about)", dict["title_issue"], "for", dict["issues_by_serie"], "issues")
        story = ''
        about_this_edition = ''
        html = r.content
        bsObj = bs(html, "lxml")
        for level1 in bsObj.findAll("h2", {"class": "about-edition"}):
            level2 = level1.findNext("p")
            if level2:
                about_this_edition = level2.get_text()

        for level1 in bsObj.findAll("div", {"class": "wiki-text"}):
            for level2 in level1.findAll("p"):
                story = story + level2.get_text() + "\n"

    url = config["urls"]["root"] + dict["link_detail"] + "/todos"   # not detail of issue, instead, of complete serie
    r = requests.get(url)

    if r.status_code != 200:
        print(f"ERR: page {url} cannot be read.")
        issue_error = True
    else:
        print("Processing serie", dict["title_issue"], "for", dict["issues_by_serie"], "issues")
        edition_type = ''
        html = r.content
        bsObj = bs(html, "lxml")
        for level1 in bsObj.findAll("p", {"class": "edition-type"}):
            edition_type = level1.get_text()
        for level1 in bsObj.findAll("ul", {"class": re.compile("auto-rows")}):
            for level2 in level1.findAll("a"):
                print("***", level2.attrs["href"])
                get_detail_issue(level2.attrs["href"], edition_type, about_this_edition, story, id_serie)
                records_processed = records_processed+1

    if issue_error is True:
        return {"id": "ERR"}
    else:
        return {"id": dict["id"],
                "title_serie": dict["title_issue"], 
                "issues_by_serie": dict["issues_by_serie"], 
                "edition_type": edition_type,
                "about_this_edition": about_this_edition,
                "story": story,
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

    for i in dict_data:
        url_issue = dict_data[i]["book_link"]
        book_id = dict_data[i]["id"]
        get_detail_issue(book_id)
    

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

def extract_image_links():
    global config

    letters_chunk = config["url_letters_all"] if thread==0 else config["url_letters"][thread-1]

    for letter in letters_chunk:
        path = create_link("images", letter)
        read_issues_links(letter, path)

def main():
    global config
    global fase
    global records_processed

    print("Scrap whakoom site")
    check_args()

    if check_paths() is False:
        print("ERR: check config!", config["json_path_prefix"])
        sys.exit(1)

    records_processed = 0

    if fase == 0:
        get_index_data()
    if fase == 1:
        read_book_detail_page()
    if fase == 2:
        extract_image_links()



if __name__ == "__main__":
    main()

