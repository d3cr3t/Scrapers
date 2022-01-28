'''
    Scrap IGDB web site for videogames information: covers and details
    Consider platform index page as the main index.
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
import time

# ArgumentParser - https://pymotw.com/3/argparse/
from argparse import ArgumentParser


config = {
    "urls": {
        "root": "https://www.igdb.com",
        "index": "https://www.igdb.com/platforms/",
        },
    "url_page_suffix": "?page=",
    "json_path_prefix": pathlib.Path.home() / "igdb/data/",
    "json_prefix": "json_",
    "json_suffix": ".json",
    "json_files": {
        "index": "index_",
        "issues": "issues_",
    },
    "link_path_prefix": pathlib.Path.home() / "igdb/links/",
    "link_prefix": "link_",
    "link_suffix": ".txt",
    "link_files": {
        "images": "images_"
    }
 }

dict_issues_by_platform = {}

def check_args():
    global fase
    global thread

    # Args
    parser = ArgumentParser()

    parser.add_argument("-f", "--fase", dest="fase", default=0, help="fase 0: platforms, fase 1: details, fase 2: image links")
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

    print(f"PROCESS INIIT: --fase {fase} --thread {thread}")

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
        print("PATH", path)
        path.touch()
        return path    
    except:
        print("ERR: Cannot create an instance of file path!", file)
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

def normalize(str):
    tmp = str.lower()

    result = ''.join([c if (ord(c) >= 48 and ord(c) <= 57) or (ord(c) >= 97 and ord(c) <= 122) else '_' for c in tmp])

    return result

def read_index_page(sector, path):
    global config

    url = config["urls"]["index"]

    list_links = []
    list_data = []
    dict_data = {}

    print(url)
    print("-" * 80)
    
    r = requests.get(url)

    if r.status_code != 200:
        print("ERR", "url not found!")
        sys.exit(1)
    else:
        html = r.content
        bsObj = bs(html, "lxml")
        n_sector = 0

        n_key = 0

        for level1 in bsObj.findAll("div", {"id": "content-page"}):
            for level2 in level1.findAll("div", {"class": re.compile("row fix-heights")}):
                n_sector = n_sector+1
                print("SECTOR", n_sector)
                for level3 in level2.findAll("div", {"class": "media"}):
                    game_system = ''
                    game_system_link = ''
                    recent_version = ''
                    for level4 in level3.findAll("div", {"class": "media-body"}):
                        for level5 in level4.findAll("a"):
                            game_system = level5.get_text()
                            game_system_link = level5.attrs["href"]
                        for level5 in level4.findAll("p"):
                            recent_version = level5.get_text().split(":")[1]

                    print(n_key, game_system, "|", recent_version)
                    n_key = n_key+1

                    dict_data[n_key] = {
                        "id": n_key,
                        "game_system": game_system,
                        "game_system_normalized": normalize(game_system),
                        "game_system_link": game_system_link,
                        "recent_version": recent_version,
                        "sector": n_sector
                        }

    print(f"SAVING DATA.. INDEX LETTER")
    
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_data, file)
    
    file.close()

def get_index_data():
    global config
    path = create_csv("index")
    read_index_page("index", path)

def _get_detail_issue(url_issue, edition_type='', about_this_edition='', story='', id_serie=''):
    global config
    global dict_issues_by_platform

    url = config["urls"]["root"] + url_issue
    print("**** PROCESS", url)

    r = requests.get(url)

    if r.status_code != 200:
        print(f"ERR: page {url} cannot be read.")
    else:
        print("Processing issue...")
        html = r.content
        bsObj = bs(html, "lxml")

        tmp_id = url.split("/")

        try:
            id_issue = tmp_id[4]
        except:
            id_issue = ''
            pass
        
        binding_format = edition_type
        in_language = ''
        publisher = ''
        #about_this_edition = ''
        #story = ''
        authors_tasks = ''
        date_published = ''
        isbn = ''
        title_in_full = ''
        price = ''
        issue_in_serie = ''
        image_large = ''

        for level1 in bsObj.findAll("p", {"class": "format"}):
            binding_format = level1.get_text()
        
        for level1 in bsObj.findAll("p", {"class": "lang-pub"}):
            for level2 in level1.findAll("span", {"itemprop": "inLanguage"}):
                in_language = level2.get_text()
            for level2 in level1.findAll("span", {"itemprop": "publisher"}):
                publisher = level2.get_text()

        if about_this_edition == '':
            for level1 in bsObj.findAll("div", {"class": "about-this-edition"}):
                for level2 in level1.findAll("p"):
                    about_this_edition = level2.get_text()

        if story =='':
            for level1 in bsObj.findAll("div", {"class": "wiki-text"}):
                for level2 in level1.findAll("p"):
                    story = story + level2.get_text() + "\n"

        for level1 in bsObj.findAll("div", {"class": re.compile("authors")}):
            for level2 in level1.findAll("p"):
                authors_tasks = level2.get_text()

        for level1 in bsObj.findAll("div", {"class": "info"}):
            for level2 in level1.findAll("p", {"itemprop": "datePublished"}):
                date_published = level2.attrs["content"]

        for level1 in bsObj.findAll("div", {"class": "info-item"}):
            for level2 in level1.findAll("ul"):
                for level3 in level2.findAll("li", {"itemprop": "isbn"}):
                    isbn = level3.get_text()

        for level1 in bsObj.findAll("div", {"class": "b-info"}):
            for level2 in level1.findAll("p", {"class": "comic-cover"}):
                for level3 in level2.findAll("a"):
                    image_large = level3.attrs["href"]
            for level2 in level1.findAll("h1", {"itemprop": "name"}):
                for level3 in level2.findAll("span"):
                    title_in_full = level3.get_text()
                for level3 in level2.findAll("strong"):
                    issue_in_serie = level3.get_text()
            for level2 in level1.findAll("button", {"class": "on-sale"}):
                tmp_price = level2.get_text()
                if "€" in tmp_price:
                    price = tmp_price
        

        dict_issues_by_platform[id_issue] = {
            "id_issue": id_issue,
            "id_serie": id_serie,
            "title_in_full": title_in_full,
            "issue_in_serie": issue_in_serie,
            "image_large": image_large,
            "binding_format": binding_format,
            "in_language": in_language,
            "publisher": publisher,
            "about_this_edition": about_this_edition,
            "story": story,
            "authors_tasks": authors_tasks,
            "date_published": date_published,
            "isbn": isbn,
            "price": price,
        }


def _get_series_issues(dict):
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



def read_platforms_index():
    global config
    global thread
    global records_processed
    global dict_issues_by_platform

    dict_data = {}

    in_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["index"] + config["json_suffix"])

    with in_path.open(mode="r") as file:
        dict_data = json.loads(file.read())
 
    file.close()

    dict_issues_by_platform = {}

    for i in dict_data:
        print(dict_data[i]["id"], dict_data[i]["game_system"])
        url = config["urls"]["root"] + dict_data[i]["game_system_link"] + "/games"
        r = requests.get(url, params={'page':"1", "title":"asc"})

        if r.status_code != 200:
            print(f"ERR: page {url} cannot be read.")
            issue_error = True
        else:
            print("Processing platform index", dict_data[i]["game_system"], "max page?")
            html = r.content
            bsObj = bs(html, "lxml")
            max_page = 1
            for level1 in bsObj.findAll("div", {"class": "pagination"}):
                for level2 in level1.findAll("li"):
                    try:
                        tmp_page = int(level2.get_text())
                        if tmp_page > max_page:
                            max_page = tmp_page
                    except:
                        pass
            print("Max page", max_page)
            read_games_lists(dict_data[i], max_page)


def read_games_lists(dict, max_page):
    global config

    dict_data = {}
    n_issue = 1

    out_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["issues"] + str(dict["id"]).strip() + "_" + dict["game_system_normalized"] + config["json_suffix"])

    #pprint.pprint(out_path)

    for p in range(1, max_page+1):
        #print(f"PROCESSING PAGE {p} for {dict["game_system"]}")
        url = config["urls"]["root"] + dict["game_system_link"] + "/games"

        retry = True
        n_tries = 20

        while retry:
            try:
                print(f"page {p} from ({max_page})...")
                r = requests.get(url, params={'page':str(p).strip(), "title":"asc"})
                retry = False
            except:
                n_tries = n_tries -1
                if n_tries >= 0:
                    print("ERR:", "connection failure, will retry")
                    time.sleep(5)
                    pass
                else:
                    print("ERR:", "maximum number of retries reached.... :-(")
                    print("ofending page:")
                    print(url, p)
                    sys.exit(2)
            
        if r.status_code != 200:
            print(f"ERR: page {url} cannot be read.")
            issue_error = True
        else:
            print("process html")
            html = r.content
            bsObj = bs(html, "lxml")
            for level1 in bsObj.findAll("div", {"class": "media-body"}):
                for level2 in level1.findAll("a"):
                    game_link = level2.attrs["href"]
                    dict_data[n_issue] = {"id_issue": n_issue, "issue_link": game_link, "game_system": dict["game_system"]}
                    n_issue = n_issue+1
    
    print("SAVING...", out_path)
    with out_path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_data, file)
    file.close()

def _extract_image_links():
    global config

    letters_chunk = config["url_letters_all"] if thread==0 else config["url_letters"][thread-1]

    for letter in letters_chunk:
        path = create_link("images", letter)
        read_games_lists(letter, path)

def main():
    global config
    global fase
    global records_processed

    print("Scrap igdb site")
    check_args()

    if check_paths() is False:
        print("ERR: check config!", config["json_path_prefix"])
        sys.exit(1)

    records_processed = 0

    if fase == 0:
        get_index_data()
    if fase == 1:
        read_platforms_index()
    if fase == 2:
        read_issues_links()
    if fase == 3:
        extract_image_links()



if __name__ == "__main__":
    main()

