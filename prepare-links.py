#! /usr/bin/env python3

import argparse
import os
import requests
from bs4 import BeautifulSoup

def get_ist_bookmarks(url, index=1):
    res = requests.get(url + "/" + str(index))
    soup = BeautifulSoup(res.text, "html.parser")
    marks = soup.findAll('a', attrs={'rel':'bookmark'})
    if len(marks) == 1000:
        marks.extend(get_ist_bookmarks(url, index + 1))        
    return marks
 
def scrape_ist_page(url, name):
    marks = get_ist_bookmarks(url)
    marklinks = [mark['href'] + '\n' for mark in marks]
    filename = name.lower().replace(' ','-') + '-links.txt'
    with open(filename, 'w') as f:
        f.writelines(marklinks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The -ist network URL for the author page with the links you want to collect")

    name = input("What is the name of the author? ")
    lastname = name.lower().split()[-1]

    if not(os.path.exist(lastname)
        os.mkdir(lastname)

    args = parser.parse_args()

    scrape_ist_page(args.url, name)

if __name__ == "__main__":
    main()
