# Scrapers

**Scrapers** is a repository of several web scraping scripts.

The goal is to get rich content from sites, dump data to JSON files and so on. Media like images, videos or other formats will be not processed by Python.<br>
In this case, is better to save links into files and then process them with a dedicated download tool, like aria or jdownloader.

## Included in this repo:

### scrap_whakoom_home.py
  
Process comic issues from Whakoom site. A huge collection with single issues and series. All of then are processed by this script.<br>
Output files include general index, series details and issues details. All of them for each initial letter to leverage the files weight.

#### args

| option | value | description |    
|--------|-------|-------------|
| -f, --fase | 0, 1 | fase to process, 0 for index pages, 1 for series/issues pages |
| -t, --thread | 0-5 | 0 indicates processing complete list, 1-5 only process a chunk |

*chunk represents a portion of letters string from 1 to z. This way is possible to launch till 5 process alltogether (in separate terminal sessions).

Current chunks are:<br>
["1abc", "defgh", "ijklmn", "opqrst", "uvwxyz"]


##### results

A list of files will be created in the **./whakoom/data** folder in JSON format: indexes, serie indexes and issue details.

