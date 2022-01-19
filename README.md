# Scrapers

Scrapers is a repository of several web scraping scripts.

The goal is to get rich content from sites, dump data to JSON files and so on. Media like images, videos or other formats will be not processed by Python.
In this case, is better to save links into files and then process them with a dedicated download tool, like aria or jdownloader.

Included in this repo:

scrap_whakoom_home.py
  Process comic issues from Whakoom site. A huge collection with single issues and series. All of then are processed by this script.
  Output files include general index, series details and issues details. All of them for each initial letter to leverage the files weight.
