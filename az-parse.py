# Imports
import requests
from bs4 import BeautifulSoup
from time import sleep

# Wishlist URL (print formatted page is easier)
print_url = 'https://www.amazon.com/hz/wishlist/printview/36B9FRG2AYASB?target=_blank&filter=unpurchased&sort=default'
# Get wishlist content
wishlist = requests.get(print_url)
# Parse wishlist for HTML
soup = BeautifulSoup(wishlist.content, 'html.parser')
# Find <span> tags in HTML, filter by class.
span_elements = soup.find_all('span', class_='a-text-bold')

# Create empty list for use in next step.
output_list = []
# For each <span> tag it finds, print them.
for span in span_elements[5:]:
    output_list.append(span.text.replace(' ', '+'))

# Characters to filter by
bad_chars = ['[',
             ']',
             '(',
             ')',
             '#',
             '-',
             '.',
             ':']

# Crete empty list for use in next step.
cleaned_list = []
# For each book, remove unwanted characters.
for item in output_list:
    for char in bad_chars:
        item = item.replace(char, '')
    cleaned_list.append(item)
# Print all books in the list
print(cleaned_list)

# Overdrive search URL
base_url = 'https://www.overdrive.com/search?q='
div_elements = []
data_ids = []
# Use list to search Overdrive, find ISBN.
for book in cleaned_list:
    # Create search URL with filters
    search_url = base_url + book + '&sort=popularity&sd=desc'
    # Get Search Content and sleep for 2 seconds.
    search_results = requests.get(search_url)
    # Parse wishlist for HTML
    soup = BeautifulSoup(search_results.content, 'html.parser')
    # Find <a> tags in HTML, filter by data-id attribute.
    div_elements = soup.find('a', attrs={'data-id': True})
    # If it has an id list it, if not it is None.
    data_id_value = div_elements['data-id'] if div_elements else ""
    data_ids.append(data_id_value)
    print(data_id_value)

print(data_ids)

base_url = 'https://share.libbyapp.com/title/'
libby_status = []
for data_id in data_ids:
    # Create search URL with filters
    search_url = base_url + data_id + '#library-wakegov'
    # Get Search Content and sleep for 2 seconds.
    search_results = requests.get(search_url)
    sleep(.1)
    # Parse wishlist for HTML
    soup = BeautifulSoup(search_results.content, 'html.parser')
    # Find <a> tags in HTML, filter by data-id attribute.
    div_elements = soup.find('div', class_='availability-library-summary')
    status = div_elements['availability-library-summary'] if div_elements else None
    libby_status.append(status)

print(libby_status)

# TODO : Filter Libby for id search or just use their search, maybe ISBN-13.
# https://share.libbyapp.com/title/2308988#library-wakegov

exit()


