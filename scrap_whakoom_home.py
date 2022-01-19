'''
    Scrap whakoom web site for comics information: covers and details
    Some titles has only one issue, others has a complete series.
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
        "root": "https://www.whakoom.com",
        "base": "https://www.whakoom.com/explore/whole_catalog/",
        "letters": "https://www.whakoom.com/explore/whole_catalog/start_with_"
        },
    "url_page_suffix": "?page=",
    "url_letters_all": "1abcdefghijklmnopqrstuvwxyz",
    "url_letters": ["1abc", "defgh", "ijklmn", "opqrst", "uvwxyz"],
    "json_path_prefix": pathlib.Path.home() / "whakoom/data/",
    "json_prefix": "json_",
    "json_suffix": ".json",
    "json_files": {
        "index": "index_",
        "issues": "issues_",
        "series": "series_",
    }
 }

dict_issues_by_letter = {}

def check_args():
    global fase
    global thread

    # Args
    parser = ArgumentParser()

    parser.add_argument("-f", "--fase", dest="fase", default=0, help="fase 0: init, fase 1: details")
    parser.add_argument("-t", "--thread", dest="thread", default=0, type=int, help="0: complete, 1-5: sector to process (from 1 to c...)")

    args = parser.parse_args()
    fase = int(args.fase)
    if args.thread <0 or args.thread>5:
        print("ERR", "-t parameter must be 0 to 5.")
        sys.exit(1)
    else:
        thread = args.thread
    

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

def create_csv(file, letter):
    global config

    try:
        path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"][file] + str(letter).strip() + config["json_suffix"])
        print(path)
        path.touch()
        return path    
    except:
        print("ERR: Cannot create an instance of file path!", path)
        sys.exit(1)


def read_index_page(letter, path):
    global config

    if str(letter).strip() == '1':
        url = config["urls"]["base"]
    else:
        url = config["urls"]["letters"]+letter

    end_of_letter = False
    page_counter = 1
    list_links = []
    list_data = []
    dict_data = {}

    while end_of_letter is False:
        url_page = url + "?page=" + str(page_counter).strip()
        print(url_page)
        print("-" * 80)
        
        r = requests.get(url, params={'page':str(page_counter).strip()})
        page_counter = page_counter+1

        if r.status_code != 200:
            end_of_letter = True
        else:
            html = r.content
            bsObj = bs(html, "lxml")

            for level1 in bsObj.findAll("ul", {"class": re.compile("auto-rows")}):
                for level2 in level1.findAll("li"):
                    link_detail = ''
                    img_url = ''
                    id_unique = ''
                    title_issue = ''
                    language_edition = ''
                    user_rate = ''
                    issues_by_serie = ''

                    for level3 in level2.findAll("a"):
                        link_detail = level3.attrs["href"]
                        id_unique = level3.attrs["data-item-id"]
                    for level3 in level2.findAll("span", {"class": "cover"}):
                        for level4 in level3.findAll("img"):
                            img_url = level4.attrs["src"]
                    for level3 in level2.findAll("strong"):
                        title_issue = level3.get_text()
                    for level3 in level2.findAll("span", {"class": "info"}):
                        for level4 in level3.findAll("span", {"class": "lang"}):
                            language_edition = level4.get_text()
                    for level3 in level2.findAll("span", {"class":"stats"}):
                        for level4 in level3.findAll("span", {"class": "rate"}):
                            tmp_user_rate = level4.get_text().split(":")
                            try:
                                user_rate = tmp_user_rate[1]
                            except:
                                user_rate = ''
                                pass
                        for level4 in level3.findAll("span", {"class": "issues"}):
                            tmp_issues_by_serie = level4.get_text().split(":")
                            try:
                                issues_by_serie = tmp_issues_by_serie[1].strip()
                            except:
                                issues_by_serie = ''
                                pass


                    print(title_issue, issues_by_serie)

                    dict_data[id_unique] = {
                        "id": id_unique,
                        "link_detail": link_detail,
                        "img_url": img_url,
                        "title_issue": title_issue,
                        "language_edition": language_edition,
                        "user_rate": user_rate,
                        "issues_by_serie": issues_by_serie,
                        }


 
    print(f"SAVING DATA.. INDEX LETTER {letter}")
    
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_data, file)
    
    file.close()

def read_number_page():
    global config
    global thread

    letters_chunk = config["url_letters_all"] if thread==0 else config["url_letters"][thread-1]

    for letter in letters_chunk:
        path = create_csv("index", letter)
        read_index_page(letter, path)

def get_index_data():

    read_number_page()

def get_detail_issue(url_issue, edition_type='', about_this_edition='', story='', id_serie=''):
    global config
    global dict_issues_by_letter

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
        
        print(f"""
          id_issue: {id_issue}
          id_serie: {id_serie}
     title_in_full: {title_in_full} | {issue_in_serie}
-------------------------------------
                """)

        '''        

        print(f"""
          id_issue: {id_issue}
          id_serie: {id_serie}
     title_in_full: {title_in_full} | {issue_in_serie}
       image_large: {image_large}
    binding_format: {binding_format}
       in_language: {in_language}
         publisher: {publisher}
about_this_edition: {about_this_edition}
             story: {story}
     authors_tasks: {authors_tasks}
    date_published: {date_published}
              isbn: {isbn}
             price: {price}
-------------------------------------
                """)
        '''

        dict_issues_by_letter[id_issue] = {
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

def read_serie_or_unique_page(letter, path):
    global config
    global records_processed
    global dict_issues_by_letter

    dict_data = {}
    dict_series = {}

    in_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["index"] + str(letter).strip() + config["json_suffix"])
     
    pprint.pprint(in_path)

    with in_path.open(mode="r") as file:
        dict_data = json.loads(file.read())
 
    file.close()

    out_path = config["json_path_prefix"] / (config["json_prefix"] + config["json_files"]["issues"] + str(letter).strip() + config["json_suffix"])

    pprint.pprint(out_path)

    dict_issues_by_letter = {}

    for i in dict_data:
        if dict_data[i]["issues_by_serie"]>'':
            print(dict_data[i]["title_issue"], dict_data[i]["issues_by_serie"])
            tmp_data = get_series_issues(dict_data[i])
            if tmp_data["id"] == "ERR":
                print("ERR", "This comic has not issues!")
            else:
                dict_series[tmp_data["id"]] = tmp_data
            print("=" * 80)
            print("RECORDS PROCESSED:", records_processed)
            print("=" * 80)
        else:
            url_issue = dict_data[i]["link_detail"]
            print("ISSUE NOT IN A SERIE ......................")
            get_detail_issue(url_issue)
    
    print(f"SAVING DATA... SERIES LETTER {letter}")
    
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_series, file)
    
    file.close()   
      
    print("SAVING DATA... ISSUES LETTER {letter}")
    
    with out_path.open(mode="w", encoding="utf-8") as file:
        json.dump(dict_issues_by_letter, file)
    
    file.close()   


def read_series_and_orphans_pages():
    global config
    global thread

    letters_chunk = config["url_letters_all"] if thread==0 else config["url_letters"][thread-1]

    for letter in letters_chunk:
        path = create_csv("series", letter)
        i_path = create_csv("issues", letter)
        read_serie_or_unique_page(letter, path)

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
        read_series_and_orphans_pages()


if __name__ == "__main__":
    main()

