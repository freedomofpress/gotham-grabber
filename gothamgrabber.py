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

def scrape_kinja_page(url, start_index=0):
    scrape_url = url + '?startIndex=' + str(start_index)
    res = requests.get(scrape_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    arts = soup.findAll('article')
    links = [art.find('h2').parent['href'] for art in arts if art.find('h2')]
    links.extend([art.find('figure').find('a')['href'] for art in arts if art.find('figure') and not art.find('h2')])
    print("Adding {} links to be scraped.".format(len(links)))
    load_more = []
    load_more = soup.findAll('button')
    if len(load_more) > 1:
        start_index += 20
        links.extend(scrape_kinja_page(url, start_index))

    return links

def scrape_villagevoice_page(url):
    headers={'User-Agent':'gothamgrabber'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    arts = soup.findAll('div', {'class':'c-postList__post__title'})
    links = [art.find('a')['href'] for art in arts]
    print("Adding {} links to be scraped.".format(len(links)))
    next_button = soup.findAll('a', {'class':'next'})
    if next_button:
        next_url = next_button[0]['href']
        links.extend(scrape_villagevoice_page(next_url))

    return links


def scrape_grantland_page(url, index=1):
    scraped_url = url + '/page/' + str(index)
    print(f'scraping {scraped_url}')
    res = requests.get(scraped_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    headlines = soup.findAll('h3', class_='headline beta')
    links = [h.find('a')['href'] for h in headlines]
    if len(links) > 0:
        print("Adding {} links to be scraped.".format(len(links)))
        links.extend(scrape_grantland_page(url, index + 1))
    return links


def scrape_the_ringer(url, index=1):
    scrape_url = url + '/archives/' + str(index)
    print(f'scraping {scrape_url}')
    res = requests.get(scrape_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    if not res.text:
        return []
    headlines = soup.findAll('h2')
    links = [h.find('a')['href'] for h in headlines if h.find('a')]
    if len(links) > 0:
        print("Adding {} links to be scraped.".format(len(links)))
        links.extend(scrape_the_ringer(url, index + 1))
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

    parser.add_argument("-k","--kinja", action='store_true', help="Specifies that the pages to be grabbed are hosted on a Kinja site")

    args = parser.parse_args()

    kinja_command = args.kinja

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
            kinja_command = True

        elif 'villagevoice.com' in spliturl.netloc:
            print("Scraping Village Voice page.")
            names = [slug, 'vv']
            lastname = names[0]
            links = scrape_villagevoice_page(url)

        elif 'theringer.com' in spliturl.netloc:
            print("Scraping the Ringer page.")
            names = slug.lower().split("-")
            lastname = names[-1]
            links = scrape_the_ringer(url)

        elif 'grantland.com' in spliturl.netloc:
            print(spliturl.netloc)
            print("Scraping Grantland page.")
            names = slug.lower().split("-")
            lastname = names[-1]
            links = scrape_grantland_page(url)

        else:
            print("""Link must be to a page on one of the following sites:
            -- Gothamist network
            -- DNAinfo
            -- LA Weekly
            -- Newsweek
            -- Kinja
            -- Village Voice
            -- The Ringer
            -- Grantland""")
            return

        filename = "-".join(names) + ".txt"

        dirname = os.path.join("out", lastname, spliturl.netloc)

        os.makedirs(dirname, exist_ok=True)

        with open(os.path.join(dirname, filename), "w") as f:
            f.write('\n'.join(links))

    elif args.textfile:
        filename = args.textfile
        dirname = os.path.dirname(filename)

        with open(filename, "r") as f:
            links = [line for line in f.read().splitlines() if line.startswith('http')]

    errorcount = 0

    for link in links:
        parsed_url = urllib.parse.urlparse(link)
        file = '-'.join(parsed_url.path.strip('/').split('/'))
        path = f'./{dirname}/{file}.pdf'
        if not os.path.isfile(path):
            number = links.index(link) + 1
            progress = "(" + str(number) + "/" + str(len(links)) + ")"
            command = ["node", "grabber.js", "--url", link, "--outdir", dirname]
            if kinja_command:
                command.insert(2, '-k')
            print("Making PDF of " + link + " " + progress)
            process = subprocess.run(command, stdout=subprocess.PIPE)
            if process.returncode:
                print("Encountered an error with that URL. Logging it now.")
                errorcount += 1
                log_errors(link, dirname, process.stdout)
        else:
            print(f'{path} already exists')

    completed = len(links) - errorcount
    print("Scrape complete. {completed} files should be available in {dirname}.".format(**locals()))

if __name__ == "__main__":
    main()
