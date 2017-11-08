#! /usr/bin/env python3

import argparse
import os
import requests
import subprocess
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
    marklinks = [mark['href'] for mark in marks]
    return marklinks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The -ist network URL for the author page with the links you want to collect")

    args = parser.parse_args()

    name = input("What is the name of the author? ")

    filename = name.lower().replace(" ","-") + ".txt"

    dirname = os.path.join("out", name.lower().split()[-1])

    if not(os.path.exists(dirname)):
        os.makedirs(dirname)

    links = scrape_ist_page(args.url, name)

    with open(os.path.join(dirname, filename), "w") as f:
        f.write('\n'.join(links))

    for link in links:
        command = ["node", "grabber.js", "--url", link, "--outdir", dirname]
        print("Making a pdf of " + link)
        subprocess.run(command)

if __name__ == "__main__":
    main()
