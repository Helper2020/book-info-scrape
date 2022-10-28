from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image
from urllib.request import urlopen
import random
import requests
import re


HOME_PAGE = 'https://books.toscrape.com/index.html'
img_num = 0
'''
Generate a url
returns a soup object
'''
def get_soup(url):
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

def multiple_page_links(link, soup):
    '''
    This function takes a BeautifulSoup object that's
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

def scrape_book_info(url):
    soup = get_soup(url)

    # Get title name
    title = str(soup.h1.string)
    
    # Get product info
    ptag_set = soup.find_all('p')
    synopsis = ptag_set[3]
    
    # get price
    symbol_price = soup.find(class_='price_color').string
    price = re.search('([0-9]+\.[0-9]+)', symbol_price).group()
    
    # Randomly generate stock quanity
    stock = random.randrange(1,100)
    
    # get UPC
    table = soup.find(class_="table-striped")
    upc = table.find('td').string
    
    # get img path
    img_file = get_image(url, soup)
    print(img_file)

    author_id = random.randrange(1000,1001)
    book_id = random.randrange(1000, 1001)
    # Testing
    book_info = {'author_id': author_id, 'book_id': book_id,
                 'title': title, 'synopsis': synopsis,
                 'price': price, 'stock': stock,
                 'upc': upc, 'img_file': img_file}

    return book_info

def get_image(url, soup):
    domain = urlparse(url).netloc
    div_tag = soup.find(class_='item active')

    img_rel_link =  div_tag.img['src'][6:]

    img_link = "https://" + domain +'/' + img_rel_link
   
    downloaded_image = requests.get(img_link)
    img = Image.open(urlopen(img_link))
    
    file_path = file_path = 'images/' + str(img_num+1) + '.jpg'
    img.save(file_path)

    return file_path

def save_book(title, synopsis, price, stock, upc, img_file):
    pass


urls = genre_book_links()


'''

# get soup for travel page
soup = get_soup(urls[0])
# Get genre
genre = get_genre(soup)
print(genre)
# Get multiple page links
subpages = multiple_page_links(urls[0], soup)
# Get page book links
book_links = genre_page_links(soup)
'''
#scrape_book_info('https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html')








