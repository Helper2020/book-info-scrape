from bs4 import BeautifulSoup
import json
import requests
import re


def get_soup(url):
    '''
    This function takes an url and returns a soup object

    Args:
        url (str): string representing an url link
    returns:
        BeautifulSoup:
    '''
    req = requests.get(url)
    return BeautifulSoup(req.text, 'html.parser')


def get_genre(soup):
    '''
    This function takes a BeautifulSoup object
    and find the genre name from the booktoscrape page

    Args:
        soup (BeaufifulSoup): BeautifulSoup object
    returns:
        str: genre title
    '''
    page_header = soup.find(class_='page-header')
    return page_header.h1.string


'''
Get book links from a page
'''
def genre_page_links(soup):
    '''
    This function takes a BeautifulSoup object that's
    a parsed document of the book-to-scrape homepage

    Args:
        soup (BeaufifulSoup): BeautifulSoup object
    returns:
        List: A List of strings that consists the genre urls
    '''
    book_links = []

    product_pods = soup.find_all(class_='product_pod')

    for product_pod in product_pods:
        book_link = product_pod.find('a')['href']
        book_link = re.split('..\/..\/..\/', book_link)[1]
        book_link = "https://books.toscrape.com/catalogue/" + book_link
        book_links.append(book_link)
    
    return book_links

def multiple_page_links(link, soup):
    '''
    This function tkaes a BeautifulSoup object that's
    a parsed document of a genre book link then finds 
    all the genre subpages.

    Args:
        link (str): genre link
        soup (BeaufifulSoup): BeautifulSoup object
    returns:
        List: A List of strings that holds the url genre subpages
    '''
    genre_link = link
    next_urls = []
    next_tag = soup.find(class_='next')

    
    while next_tag:
        next_url = next_tag.a['href']
        url = genre_link.replace('index.html', next_url)
        next_urls.append(url)

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        next_tag = soup.find(class_='next')
    
    return next_urls

urls = ['https://books.toscrape.com/index.html']

req = requests.get(urls.pop())
soup = BeautifulSoup(req.text, 'html.parser')

# Gather a list of urls from the sidebar
sidebar = soup.find(class_='nav-list')

for link in sidebar.find_all('a'):
    url = link.get('href')
    if url.find('books_1') > -1:
        continue
    urls.append(url)

    
# Need to prepend(https://books.toscrape.com/catalogue/category) to the rest of the urls
for idx in range(len(urls)):
    url = urls[idx]
    new_url = 'https://books.toscrape.com/' + url
    urls[idx] = new_url



# Lets get the book data now
soup = get_soup(urls[0])
# get multiple links in genre if any
genre_links = multiple_page_links(urls[0], soup)
print(genre_links)
# Get book genre
genre = get_genre(soup)
# Get genre links
genre_page_links = genre_page_links(soup)



