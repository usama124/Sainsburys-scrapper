import configparser
import Scrape_categories as scrapper
from SeleniumDriver import WebDriver
import ExcelWriter as excel

parser = configparser.ConfigParser()
parser.read("Conf/config.ini")


def confParser(section):
    if not parser.has_section(section):
        print("No section info  rmation are available in config file for", section)
        return
    # Build dict
    tmp_dict = {}
    for option, value in parser.items(section):
        option = str(option)
        value = value
        tmp_dict[option] = value
    return tmp_dict


def read_scraped_products():
    list_prod = []
    f = open("record/scraped_products.txt", "r")
    line = f.readline().split("\n")[0]
    while line != "" and line != None:
        list_prod.append(line)
        line = f.readline().split("\n")[0]
    f.close()
    return list_prod


def write_scraped_products(url):
    f = open("record/scraped_products.txt", "a")
    f.write(url + "\n")
    f.close()


general_conf = confParser("general_conf")
CHROME_PATH = general_conf["chrome_path"]
base_url = general_conf["base_url"]
start_url = general_conf["start_url"]

categories_list = confParser("categories")

list_scraped_products = read_scraped_products()

selenium_webdriver = WebDriver(CHROME_PATH)

products_urls_list = []

if __name__ == '__main__':
    excel.create_heading()

    print("\n\nScraping groceries...\n\n")

    for cat in categories_list:
        print(cat.replace("_", "") + "...\n")
        cat_link = categories_list[cat]
        scrapper.scrape_products_page(cat_link, selenium_webdriver, list_scraped_products)

    print("Finish...")

