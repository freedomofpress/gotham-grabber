#! /usr/bin/env python3

import argparse
import os
import requests
import subprocess
import urllib
from bs4 import BeautifulSoup

def get_ist_bookmarks(url, index=1):
    res = requests.get(url + "/" + str(index))
    soup = BeautifulSoup(res.text, 'html.parser')
    marks = soup.findAll('a', attrs={'rel':'bookmark'})
    print("Adding {} links to be scraped.".format(len(marks)))
    if len(marks) == 1000:
        marks.extend(get_ist_bookmarks(url, index + 1))        
    return marks
 
def scrape_ist_page(url):
    marks = get_ist_bookmarks(url)
    marklinks = [mark['href'] for mark in marks]
    return marklinks

def scrape_dnainfo_page(url, index=1):
    scrape_url = url + "/page/" + str(index)
    res = requests.get(scrape_url, headers={'User-Agent':'gothamgrabber'})
    soup = BeautifulSoup(res.text, 'html.parser')
    links = ['https:' + link['href'] for link in soup.findAll('a',
             attrs = {'class':'headline'})]
    print("Adding {} links to be scraped.".format(len(links)))
    if len(links) == 8:
        links.extend(scrape_dnainfo_page(url, index + 1))
    return links

def scrape_laweekly_page(law_id, index=1):
    scrape_url = "http://www.laweekly.com/authors/authorAjax/" + law_id + \
                 "?page=" + str(index)
    res = requests.get(scrape_url).json()
    if not res['data']:
        return []
    soup = BeautifulSoup(res['data'], 'html.parser')
    headlines = soup.findAll('div', {'class':'headline'})
    links = ['http://laweekly.com' + headline.find('a')['href'] for headline in headlines]
    print("Adding {} links to be scraped.".format(len(links)))
    links.extend(scrape_laweekly_page(law_id, index + 1))
    return links

def scrape_newsweek_page(url, index=0):
    scrape_url = url + "?page=" + str(index)
    res = requests.get(scrape_url, headers={'User-Agent':'gothamgrabber'})
    if not res.text:
        return []
    soup = BeautifulSoup(res.text, 'html.parser')
    arts = soup.findAll('article')[1:]
    headlines = [art.find('h3') for art in arts]
    links = ['http://newsweek.com' + headline.find('a')['href'] for headline in headlines]
    print("Adding {} links to be scraped.".format(len(links)))
    links.extend(scrape_newsweek_page(url, index + 1))
    return links

def scrape_kinja_page(url, start_time=''):
    scrape_url = url + start_time
    res = requests.get(scrape_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    arts = soup.findAll('h1', {'class':'entry-title'})
    links = [art.find('a')['href'] for art in arts]
    print("Adding {} links to be scraped.".format(len(links)))
    load_more = []
    load_more = soup.findAll('div', {'class':'load-more__button'})
    if load_more:
        links.extend(scrape_kinja_page(url, load_more[0].find('a')['href']))

    return links

def log_errors(url, dirname, error_bytes):
    filename = "errors.log"
    processed_error = error_bytes.decode('utf-8').split('\n')[0]
    with open(os.path.join(dirname, filename), "a") as f:
        f.write(url + '\n')
        f.write(processed_error + '\n')

def main():
    parser = argparse.ArgumentParser(description="A script for scraping and converting to PDF all of the articles by a given author in the DNAinfo/Gothamist network, LA Weekly, or Newsweek. Accepts either a URL to an online author page or a list of links to articles as input.")
    infile = parser.add_mutually_exclusive_group(required=True)
    infile.add_argument("-u","--url", help="The URL of the author page with the links you want to collect", default=None)
    infile.add_argument("-t","--textfile", help="A list of links for the grabber script to convert to PDFs", default=None)

    args = parser.parse_args()

    if args.url:
        url = args.url
        spliturl = urllib.parse.urlparse(url)
        
        slug = spliturl.path.split("/")[-1]

        slug = urllib.parse.unquote(slug)
        
        if 'ist.com' in spliturl.netloc:
            print("Scraping Gothamist network page.")
            links = scrape_ist_page(url)
            names = slug.lower().split()
            lastname = names[-1]

        elif 'dnainfo.com' in spliturl.netloc:
            print("Scraping DNAinfo page. This may take a while.")
            links = scrape_dnainfo_page(url)
            names = slug.lower().split("-")
            lastname = names[-1]

        elif 'laweekly.com' in spliturl.netloc:
            print("Scraping LAWeekly page.")
            names = slug.split('-')[:-1]
            lastname = names[-1]
            law_id = slug.split('-')[-1]
            links = scrape_laweekly_page(law_id)

        elif 'newsweek.com' in spliturl.netloc:
            print("Scraping Newsweek page.")
            names = slug.split('-')
            lastname = names[-1]
            links = scrape_newsweek_page(url)

        elif 'kinja.com' in spliturl.netloc:
            print("Scraping Kinja page.")
            names = [slug, 'kinja']
            lastname = names[0]
            links = scrape_kinja_page(url)

        else:
            print("""Link must be to a page on one of the following sites:
            -- Gothamist network
            -- DNAinfo
            -- LA Weekly
            -- Newsweek
            -- Kinja""")
            return

        filename = "-".join(names) + ".txt"

        dirname = os.path.join("out", lastname)

        os.makedirs(dirname, exist_ok=True)

        with open(os.path.join(dirname, filename), "w") as f:
            f.write('\n'.join(links))

    elif args.textfile:
        filename = args.textfile
        dirname = os.path.dirname(filename)

        with open(filename, "r") as f:
            links = f.read().splitlines()

    errorcount = 0

    for link in links:
        number = links.index(link) + 1
        progress = "(" + str(number) + "/" + str(len(links)) + ")"
        command = ["node", "grabber.js", "--url", link, "--outdir", dirname]
        print("Making PDF of " + link + " " + progress)
        process = subprocess.run(command, stdout=subprocess.PIPE)
        if process.returncode:
            print("Encountered an error with that URL. Logging it now.")
            errorcount += 1
            log_errors(link, dirname, process.stdout)

    completed = len(links) - errorcount
    print("Scrape complete. {completed} files should be available in {dirname}.".format(**locals()))

if __name__ == "__main__":
    main()
