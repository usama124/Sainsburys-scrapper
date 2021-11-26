import json
import re, time
from bs4 import BeautifulSoup
import DownloadImage as downloader
import ExcelWriter as excel


def write_scraped_products(url):
    f = open("record/scraped_products.txt", "a")
    f.write(url + "\n")
    f.close()


def increase_price_15_percent(price):
    if "£" in price:
        price = price.replace("£", "").strip()
        price = float(price)
        price = price + (price * 0.15)
    elif "p" in price:
        price = price.replace("p", "").strip()
        price = float(float(price)/100)
        price = price + (price * 0.15)
    return "£" + str(price)


def get_categories_tags(page_obj):
    tags_list = []
    tags_ul = page_obj.find("ol", attrs={"class": "ln-c-breadcrumbs ln-o-inline-list"}).findAll("li")
    for tag in tags_ul:
        tag_text = tag.find("a").text.replace("\n", "").replace(",", "").strip()
        tags_list.append(tag_text)
    tags = "|".join(tags_list)
    while len(tags_list) < 4:
        tags_list.append("")

    return (tags_list, tags)


def get_alphabets_unit(value):
    only_alpha = ""
    for char in value:
        if char.isalpha():
            only_alpha += char
    return only_alpha

def convert_weight_to_kg(weight : str):
    non_decimal = re.compile(r'[^\d.-]+')
    unit = get_alphabets_unit(weight).strip()
    try:
        if unit.lower() == "kg":
            return weight
        elif unit.lower() == "l":
            return weight
        elif unit.lower() == "g":
            weight = non_decimal.sub('', weight).strip()
            if "." in weight:
                weight = str(float(weight) / 1000) + "Kg"
            else:
                weight = str(int(weight) / 1000) + "Kg"
        elif unit.lower() == "ml":
            weight = non_decimal.sub('', weight).strip()
            if "." in weight:
                weight = str(float(weight) / 1000) + "L"
            else:
                weight = str(int(weight) / 1000) + "L"
    except Exception as e:
        pass
    return weight


def find_weight_from_title(title : str):
    weight = ""
    splitted_title = title.split(" ")
    for sp_t in splitted_title:
        sp_t = sp_t.split("x")[-1]
        if "g" in sp_t.lower() or "kg" in sp_t.lower() or "ml" in sp_t.lower() or "l" in sp_t.lower():
            weight = convert_weight_to_kg(sp_t)
            break
    return weight


def scrape_product(link, selenium_webdriver):
    print("Scraping product link...")
    selenium_webdriver.init_driver()
    selenium_webdriver.webdriver.get(link)
    time.sleep(4)
    selenium_webdriver.accept_cookies()
    try:
        page_src = selenium_webdriver.webdriver.page_source
        page_obj = BeautifulSoup(page_src, "lxml")

        prod_title = page_obj.find("h1", attrs={"class": "pd__header"}).text.strip()
        categories_list, tags = get_categories_tags(page_obj)
        cost_div = page_obj.find("div", attrs={"class": "pd__cost"})
        price = cost_div.find("div", attrs={"data-test-id": "pd-retail-price"}).text.strip()
        price = increase_price_15_percent(price)
        price_per_unit = cost_div.find("span", attrs={"class": "pd__cost__per-unit"}).text.strip()
        weight = find_weight_from_title(prod_title)
        prod_desc = str(page_obj.find("div", attrs={"class": "ln-c-card pd-details ln-c-card--soft"}))
        prod_sku = page_obj.find("span", attrs={"id": "productSKU"}).text.strip()
        img = page_obj.find("img", attrs={"class": "pd__image"}).attrs["src"]
        image_name = downloader.download_image(img, prod_sku)
        excel.write_excel_file(categories_list, tags, prod_sku, prod_title, price, price_per_unit, weight, prod_desc, image_name)
    except Exception as e:
        pass
    selenium_webdriver.close_webdriver()


def click_no_thanks(selenium_driver):
    try:
        selenium_driver.webdriver.find_element_by_id("smg-etr-invitation-no").click()
    except:
        pass

def scrape_products_page(link, selenium_webdriver, list_scraped_products):
    prod_urls_list = []
    selenium_webdriver.init_driver()
    selenium_webdriver.webdriver.get(link)
    selenium_webdriver.accept_cookies()

    counter = 0
    while True:
        page_obj = BeautifulSoup(selenium_webdriver.webdriver.page_source, "lxml")
        products_grid = page_obj.find("ul", attrs={"class": "productLister gridView"}).findAll("li", attrs={
            "class": "gridItem"})
        for product_div in products_grid:
            try:
                prod_info = product_div.find("div", attrs={"class": "productInfo"}).find("a")
                prod_link = prod_info.attrs["href"]
                prod_urls_list.append(prod_link)
            except:
                pass

        try:
            selenium_webdriver.webdriver.find_element_by_css_selector('#productLister > div:nth-child(2) > ul.pages > li.next > a').click()
            time.sleep(2)
            counter = 0
        except Exception as e:
            print(e)
            click_no_thanks(selenium_webdriver)
            if counter == 2:
                break
            counter = counter + 1
    selenium_webdriver.close_webdriver()

    prod_urls_list = list(set(prod_urls_list))
    try:
        for prod_url in prod_urls_list:
            if prod_url not in list_scraped_products:
                scrape_product(prod_url, selenium_webdriver)
                write_scraped_products(prod_url)
                list_scraped_products.append(prod_url)
    except Exception as e:
        pass
