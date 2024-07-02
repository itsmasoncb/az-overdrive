##########################
# Import Setup
##########################
import logging
import coloredlogs
import requests
from bs4 import BeautifulSoup
from time import sleep
from validator_collection import checkers
from selenium import webdriver

##########################
# Variable Setup
##########################
logger = logging.getLogger('MasonWishList')
logging.basicConfig(level=logging.INFO)

wishlist_url = 'https://www.amazon.com/hz/wishlist/ls/36B9FRG2AYASB'
overdrive_url = 'https://www.overdrive.com/search?q='
libbyapp_url = 'https://share.libbyapp.com/title/'


def asin_to_isbn(asin: str):
    """

    :param asin:
    :return:
    """
    logger.info('Converting ASIN to ISBN..')
    checkers.is_integer(asin)

    try:
        if len(str(asin)) == 10:
            isbn_10 = asin
            logger.info('ISBN10 calculated: {}'.format(isbn_10))
        else:
            isbn_10 = None
        checkers.has_length(asin, minimum=10, maximum=13)
        # 978 Prefix, minus last digit for check digit calculation
        isbn_13_no_check_digit = '978' + asin[:-1]
        logger.info('Intermediate 12 digit code created')
        total = 0
        for index, digit in enumerate(isbn_13_no_check_digit):
            if index % 2 == 0:
                total += int(digit) * 1
            else:
                total += int(digit) * 3
        remainder = total % 10
        check_digit = (10 - remainder) % 10
        isbn_13 = isbn_13_no_check_digit + str(check_digit)
        logger.info('ISBN-13 calculated: {}'.format(isbn_13))

        return isbn_10, isbn_13

    except BaseException as e:
        logger.error('asin_to_isbn has encountered an error. The error reads: {}'.format(e))


def wishlist_to_urls():
    """

    :return:
    """
    # TODO: Use Selenium to lazy load wishlist
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(wishlist_url, headers=headers)

    if response.status_code != 200:
        print("Failed to retrieve the wishlist page")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    item_urls = []
    for item in soup.select("a.a-link-normal"):
        href = item.get('href')
        # Look for URLS with /dp/
        if href and '/dp/' in href:
            item_url = "https://www.amazon.com" + href.split('?')[0]
            item_urls.append(item_url)

    return item_urls




# asin = '0063347539'
# isbn = asin_to_isbn(asin)
# if isbn:
#     print(f"The ISBN for ASIN {asin} is {isbn}.")
# else:
#     print("Invalid ASIN. It must be a numeric string.")