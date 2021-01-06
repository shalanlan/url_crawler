# Url Crawler
This is a simple web crawler CLI tool which fetches URLs from webpages and outputs crawl results to stdout as the crawl proceeds.
It repeats this process upon every URL fetched. 
# Prerequisite
Should be run with python 3.8.
# Installation
This CLI uses BeautifulSoup to crawl and parse html content
```
pip3 install beautifulsoup4
```
and Arparse to parse command line args:
```
pip3 install argparse
```
To run locally, clone this repo via:
```
git clone https://github.com/shalanlan/url_crawler.git
```
# Run CLI
Navigate to `url_crawler` directory and run:
```
python3 url_crawler.py <url>
```
For help, include `-h`. 

To run tests:
```
python3 -m unittest test_url_crawler.py
```
NOTE: Tests use mock patches for request and thus can be run offline.


