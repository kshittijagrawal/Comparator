from bs4 import BeautifulSoup as bs
from requests.exceptions import Timeout
from requests.sessions import TooManyRedirects
import requests
import time
import sys
from prettytable import PrettyTable


def amz_details(bsoup, product, header):
    """ Function used to visit amazon's website, render all the relevant tags, scrapes required information, and returns it to the main block. """

    container = bsoup.find("div", class_="s-main-slot s-result-list s-search-results sg-row")
    prod_links = []
    base_url = "https://www.amazon.in"
    items = container.find_all("div")
    for i in items:
        try:
            link = i.find("a")["href"]
        except Exception as e:
            continue
        if link.find("qid") == -1:
            continue
        prod_links.append(base_url+link)
    
    total_results = len(prod_links)
    req = requests.get(prod_links[0], headers=header).text
    soup = bs(req, "lxml")
    try:
        name = soup.find("span", id="productTitle")
        product_name = name.text.strip()
    except:
        product_name = " ".join(product).title()
    try: 
        rating = soup.find("span", class_="a-icon-alt")
        product_rating = rating.text
    except Exception as e:
        product_rating = "Not Available"
    try:
        price = soup.find("span", id="priceblock_ourprice")
        product_price = price.text
    except Exception as e:
        product_price = "Sold by Third Party. Please visit the website for more info."

    return [["Product Name", product_name],
            ["Product Price", product_price],
            ["Product Rating", product_rating],
            ["Total Fetched Results", total_results]]


def flip_details(bsoup, product, header):
    """ Function used to visit flipkart's website, render all the relevant tags, scrapes required information, and returns it to the main block. """

    container = bsoup.find_all("div", class_="_1AtVbE col-12-12")
    prod_links = []
    base_url = "https://www.flipkart.com"
    for i in container[1:]:
        try:
            link = i.find("a")["href"]
        except Exception as e:
            continue
        if link.find("pid") == -1:
            continue
        prod_links.append(base_url+link)

    total_results = len(prod_links)*10
    req = requests.get(prod_links[0], headers=header).text
    soup = bs(req, "lxml")
    try:
        name = soup.find("div", class_="aMaAEs")
        product_name = name.div.h1.span.text
    except:
        product_name = " ".join(product).title()
    try:
        rating = name.find("div", class_="_3LWZlK")
        product_rating = rating.text + " out of 5 stars"
    except Exception as e:
        product_rating = "Not Available"
    try:
        price = name.find("div", class_="_30jeq3 _16Jk6d")
        product_price = price.text + ".00"
    except Exception as e:
        product_price = "Sold by Third Party. Please visit the website for more info."

    return [["Product Name", product_name],
            ["Product Price", product_price],
            ["Product Rating", product_rating],
            ["Total Fetched Results", total_results]]


def error_handler(source, prod, HEADERS):
    """ Function that sends GET request to the URL and retrieves information; prints the particular error message if an error occured and exits with an exit code 1
        else returns the request object received. """

    try:
        req = requests.get(source, params=prod, headers=HEADERS)
    except Timeout as e:
        print("\nThe website took too long to respond. Please try after sometime.\n")
        sys.exit(1)
    except ConnectionError as e:
        print("\nYou do not have a descent internet connection. Please check your Internet Connection and try again later.\n")
        sys.exit(1)
    except TooManyRedirects as e:
        print("\nYour request exceeded the configured number of maximum redirections. Please try after sometime.\n")
        sys.exit(1)
    except Exception as e:
        print("\nRequest souldn't be completed. Please try after sometime.\n")
        sys.exit(1)

    return req


def flip_main():
    """ Function that extracts product information from the command line, calls 'error_handler()' to check for errors and passes the information to 'flip_details()' 
        to gather required product details. """

    product = sys.argv[1:]
    prod_key = "+".join(product)

    source = "https://flipkart.com/search"
    prod = {"q" : prod_key.lower()}
    HEADERS = ({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"})
    
    req = error_handler(source, prod, HEADERS)

    soup = bs(req.text, "lxml")
    flip_res = flip_details(soup, product, HEADERS)
    return flip_res


def amz_main():
    """ Function that extracts product information from the command line, calls 'error_handler()' to check for errors and passes the information to 'amz_details()' 
        to gather required product details. """

    product = sys.argv[1:]
    product_key = "+".join(product)

    source = "https://amazon.in/s"
    prod = {"k" : product_key.lower()}
    HEADERS = ({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"})

    req = error_handler(source, prod, HEADERS)
    
    soup = bs(req.text, "lxml")
    amz_res = amz_details(soup, product, HEADERS)
    return amz_res


if __name__ == "__main__":
    """ Main block where the gathered result is then printed in the form of tables. """

    flip_res = flip_main()
    time.sleep(2)
    amz_res = amz_main()
    time.sleep(1)

    flipkart = PrettyTable()
    amazon = PrettyTable()
    flipkart.field_names = ["Property", "Data"]
    amazon.field_names = ["Property", "Data"]

    print("\n\n\t\tData from Flipkart")
    print("-"*70)

    flipkart.add_rows(flip_res)
    flipkart.align = "c"
    print(flipkart)
    
    print("\n\n\t\tData from Amazon")
    print("-"*70)

    amazon.add_rows(amz_res)
    amazon.align = "c"
    print(amazon)
