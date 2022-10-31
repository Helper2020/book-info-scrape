import os
import random
import requests
import re
import json
import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image
from urllib.request import urlopen



HOME_PAGE = 'https://books.toscrape.com/index.html'


def get_soup(url):
    '''
    Generate a url
    returns a soup object
    '''
    req = requests.get(url)
    return BeautifulSoup(req.text, 'html.parser')


def genre_book_links():
    '''
    This function takes a BeautifulSoup object that's
    a parsed document of the book-to-scrape homepage
    Args:
        soup (BeaufifulSoup): BeautifulSoup object
    returns:
        List: A List of strings that consists the genre urls
    '''
    soup = get_soup(HOME_PAGE)
    # Gather a list of urls from the sidebar
    sidebar = soup.find(class_='nav-list')

    urls = []

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

    return urls
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


def genre_page_links(soup):
    '''
    Get book links from a page

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

def multiple_page_links(url, soup):
    '''
    This function takes a BeautifulSoup object that's
    a parsed document of a genre book link then finds 
    all the genre subpages.

    Args:
        url (str): genre link
        soup (BeaufifulSoup): BeautifulSoup object
    returns:
        List: A List of strings that holds the url genre subpages
    '''
    genre_link = url
    next_urls = []
    next_urls.append(url)
    next_tag = soup.find(class_='next')

    
    while next_tag:
        next_url = next_tag.a['href']
        url = genre_link.replace('index.html', next_url)
        next_urls.append(url)

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        next_tag = soup.find(class_='next')
    
    return next_urls

'''
[
    {
        'title': title_name,
        'upc': upc,
        'price': price,
        'stock': amount,
        'Description': 'description'
    }
]
'''

def scrape_book_info(url, genre):
    soup = get_soup(url)

    # Get title name
    title = str(soup.h1.string)
    
    # Get product info
    ptag_set = soup.find_all('p')
    synopsis = ptag_set[3].string
    
    # get price
    symbol_price = soup.find(class_='price_color').string
    price = re.search('([0-9]+\.[0-9]+)', symbol_price).group()
    
    # Randomly generate stock quanity
    stock = random.randrange(1,100)
    
    # get UPC
    table = soup.find(class_="table-striped")
    upc = table.find('td').string
    
    # get img path
    img_path = get_image(url, soup)

    author_id = random.randrange(1000,1001)
    book_id = random.randrange(1000, 1001)
    # Fill info except name. Will be done later
    book_info = {'author_id': author_id, 'first_name': None, 'last_name': None, 'book_id': book_id,
                 'title': title, 'synopsis': synopsis, 'genre': genre,
                 'price': price, 'stock': stock,
                 'upc': upc, 'img_file_path': img_path}

    return book_info

def get_image(url, soup):

    # check if image folder exist if not create
    if not os.path.exists("images"):
        os.makedirs('images')

    domain = urlparse(url).netloc
    div_tag = soup.find(class_='item active')

    # extract relative link
    img_rel_link =  div_tag.img['src'][6:]
    # assemble the link
    img_link = "https://" + domain +'/' + img_rel_link
    img = Image.open(urlopen(img_link))

    # extract file name from image relative link
    last_slash_idx = img_rel_link.rindex('/')
    img_name = img_rel_link[last_slash_idx+1:]
   
    # put the img in a folder
    rel_path = os.path.join('images', img_name)

    img.save(rel_path)

    return rel_path

# Lets scrape now

genre_urls = genre_book_links()
books_info = []

for genre_url in genre_urls:
   
    # Get soup for genre page
    soup = get_soup(genre_url)
    # get genre name
    genre = get_genre(soup)
    # Get multiple page links
    subpages = multiple_page_links(genre_url, soup)

    for subpage in subpages:
        subpage_soup = get_soup(subpage)
        book_links = genre_page_links(subpage_soup)

        for book_page in book_links:
            books_info.append(scrape_book_info(book_page, genre))
       

# 900 author names
books_info900 = books_info[:900]

with open('full_names900.csv', 'r') as file:
    reader = csv.reader(file)
    # Skip header row
    next(reader, None)
    # idx 
    idx = 0
    for row in reader:
        book = books_info900[idx]
        book['first_name'] = row[1]
        book['last_name'] = row[2]

print(len(books_info900))
with open('books_json.txt', 'w') as file:
    json.dump(books_info, file)







