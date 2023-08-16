# Imports
import requests
from bs4 import BeautifulSoup

# Wishlist URL (print formatted page is easier)
print_url = 'https://www.amazon.com/hz/wishlist/printview/36B9FRG2AYASB?target=_blank&filter=unpurchased&sort=default'

# Get wishlist content
wishlist = requests.get(print_url)

# Parse wishlist for HTML
soup = BeautifulSoup(wishlist.content, 'html.parser')

# Find <span> tags in HTML, filter by class.
span_elements = soup.find_all('span', class_='a-text-bold')

# For each <span> tag it finds, print them.
for span in span_elements:
    print(span.text)

# TODO : Search Overdrive for title, filter by popularity.
# https://www.overdrive.com/search?q=dune&sort=popularity&sd=desc

# TODO : Parse ID number of book.
# https://www.overdrive.com/media/2308988/dune

# TODO : Filter Libby for id search or just use their search.
# https://share.libbyapp.com/title/2308988#library-wakegov
# https://libbyapp.com/search/wakegov

exit()

