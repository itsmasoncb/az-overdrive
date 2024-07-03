##########################
# Import Setup
##########################
import logging
import os
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from validator_collection import checkers

##########################
# Variable Setup
##########################
logger = logging.getLogger('MasonWishList')
logging.basicConfig(level=logging.INFO)
os.environ['SE_AVOID_STATS'] = 'true'

wishlist_url = 'https://www.amazon.com/hz/wishlist/ls/36B9FRG2AYASB'

# Overdrive doesn't seem to search ISBNs anymore
unused_base_urls = {'overdrive_url': 'https://www.overdrive.com/search?q={}'}

isbn_10_base_urls = {'libby_base_url': 'https://libbyapp.com/search/wakegov/search/query-{}/page-1/',
                     'goodreads_base_url': 'https://www.goodreads.com/search?q={}&search_type=books',
                     'libgen_base_url': 'https://libgen.is/search.php?req={}',
                     'open_libray': 'https://openlibrary.org/search?isbn={}'}

# Google works best with ISBN13 searches.
isbn_13_base_urls = {'google_books_base_url': 'https://www.google.com/search?tbo=p&tbm=bks&q=isbn%{}'}

# Consider comparing price on these?
paid_base_urls = {'amazon_shopping': 'https://www.amazon.com/dp/{}'}

# find_libby_library = 'https://libbysearch.com/'


def setup_driver():
    """
    """
    # Setup Selenium WebDriver
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    logger.info('Returning driver settings, zoom zoom.')
    return driver


def lazy_load_wishlist(driver):
    """
    """
    try:
        logger.info('Lazy Loading the webpage, this may take a moment...')

        while True:
            # Scroll to the bottom of the page
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            sleep(5)  # Wait for content to load

            # Parse the page content with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Check if "End of list" is in the page
            end_of_list = soup.find('h5', {'aria-level': '5'}, string='End of list')
            if end_of_list:
                logging.info("Found the end of the wishlist. Good job.")
                return soup

    except BaseException as e:
        logger.error('lazy_load_wishlist has encountered an error. The error reads: {}'.format(e))
        exit(1)


def extract_wishlist_urls(soup):
    """
    """
    item_urls = []
    logger.info('Extracting URLs from HTML wishlist data...')
    try:
        # Extract item URLs
        for item in soup.select("a.a-link-normal"):
            href = item.get('href')
            if href and '/dp/' in href:
                item_url = "https://www.amazon.com" + href.split('?')[0]
                if item_url not in item_urls:
                    item_urls.append(item_url)

        return item_urls

    except BaseException as e:
        logger.error('extract_wishlist_urls has encountered an error. The error reads: {}'.format(e))
        exit(1)


def clean_urls(urls):
    """
    """
    cleaned_urls = []
    invalid_urls = []
    for url in urls:
        try:
            # Extract the part of the URL between the first and second slashes after the domain
            amazon_product_code = url.split('/')[4]
            # Remove last character as valid ISBN10 can contain X as the last digit.
            amazon_product_code_int = amazon_product_code[:-1]
            if checkers.is_integer(amazon_product_code_int):
                cleaned_urls.append(amazon_product_code)
            else:
                logging.info('Invalid ISBN, this may be an audiobook: {}'.format(amazon_product_code))
                invalid_urls.append(amazon_product_code)

        except BaseException as e:
            logger.error('clean_urls has encountered an error. The error reads: {}'.format(e))
            exit(1)

    return cleaned_urls, invalid_urls


def asin_to_isbn(asin_list: list):
    """
    """
    logger.info('Converting ASIN to ISBN..')
    isbn_10_list = []
    isbn_13_list = []
    try:
        for asin in asin_list:
            if checkers.has_length(asin, minimum=10, maximum=10):
                isbn_10 = asin
                logger.info('ISBN10 validated and returned: {}'.format(isbn_10))
                isbn_10_list.append(isbn_10)

        for isbn_13 in isbn_10_list:
            # 978 Prefix, minus last digit for check digit calculation
            isbn_13_no_check_digit = '978' + isbn_13[:-1]
            total = 0

            # This math is confusing but end results find the book with both numbers correctly
            for index, digit in enumerate(isbn_13_no_check_digit):
                if index % 2 == 0:
                    total += int(digit) * 1
                else:
                    total += int(digit) * 3
            remainder = total % 10
            check_digit = (10 - remainder) % 10
            isbn_13_final = isbn_13_no_check_digit + str(check_digit)

            checkers.has_length(isbn_13_final, minimum=13, maximum=13)
            logger.info('ISBN-13 validated and converted: {}'.format(isbn_13_final))
            isbn_13_list.append(isbn_13_final)

        logger.info('ISBN10 and ISBN13 lists created.')
        return isbn_10_list, isbn_13_list

    except BaseException as e:
        logger.error('asin_to_isbn has encountered an error. The error reads: {}'.format(e))
        exit(1)


def isbn_free_search_builder(isbn_10_list, isbn_13_list):
    """
    """
    isbn_10_search_urls = []
    isbn_13_search_urls = []
    try:
        logger.info('Parsing list of free options...')
        for isbn_10 in isbn_10_list:
            for website, template in isbn_10_base_urls.items():
                url = template.format(isbn_10)
                isbn_10_search_urls.append(url)

        # TODO: Google URL doesn't work quite right
        for isbn_13 in isbn_13_list:
            for website, template in isbn_13_base_urls.items():
                url = template.format(isbn_13)
                isbn_13_search_urls.append(url)

        logger.info('Returning list of free ISBN urls...')
        return isbn_10_search_urls, isbn_13_search_urls

    except BaseException as e:
        logger.error('isbn_free_search_builder has encountered an error. The error reads: {}'.format(e))
        exit(1)

# TODO: Code paid builder as last resort for when free options are not found, consider amazon smile links.
# def isbn_paid_search_buidler():
#     logger.info('Parsing list for discounted options...')
#     logger.info('Parsing list for dang near full priced options...')
#     pass


def get_amazon_wishlist_urls():
    """
    """
    try:
        driver = setup_driver()
        driver.get(wishlist_url)

        soup = lazy_load_wishlist(driver)
        driver.quit()

        item_urls = extract_wishlist_urls(soup)
        # TODO: item_urls are clean links back to URLS for Amazon, for use in some sort of "paid_parser" later.
        clean_isbn_list, _ = clean_urls(item_urls)
        final_isbn_10_list, final_isbn_13_list = asin_to_isbn(clean_isbn_list)
        isbn_10_search_urls, isbn_13_search_urls = isbn_free_search_builder(final_isbn_10_list, final_isbn_13_list)

        return isbn_10_search_urls, isbn_13_search_urls

    except BaseException as e:
        logger.error('extract_wishlist_urls has encountered an error. The error reads: {}'.format(e))
        exit(1)


def main():
    isbn_10_search_urls, isbn_13_search_urls = get_amazon_wishlist_urls()
    # TODO: Add url checks to confirm if book is found or not, different for each website.
    # TODO: Start to consider breaking this out into other .py files.
    try:
        logger.info(isbn_10_search_urls)
        logger.info(isbn_13_search_urls)

    except BaseException as e:
        logger.error('main has encountered an error. The error reads: {}'.format(e))
        exit(1)


if __name__ == "__main__":
    main()
