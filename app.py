from bs4 import BeautifulSoup
import requests
import re


'''
Generate a url
returns a soup object
'''
def get_soup(url):
    req = requests.get(url)
    return BeautifulSoup(req.text, 'html.parser')
'''
returns genre name
'''
def get_genre(soup):
    page_header = soup.find(class_='page-header')
    return page_header.h1.string


'''
Get book links from a page
'''
def genre_book_links(soup):
    book_links = []

    product_pods = soup.find_all(class_='product_pod')

    for product_pod in product_pods:
        book_link = product_pod.find('a')['href']
        book_link = re.split('..\/..\/..\/', book_link)[1]
        book_link = "https://books.toscrape.com/catalogue/" + book_link
        book_links.append(book_link)
    
    return book_links
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
# Get book genre
genre = get_genre(soup)
# Get genre links
genre_book_links = genre_book_links(soup)

