import json
import re, time, random
from bs4 import BeautifulSoup
import DownloadImage as downloader
import ExcelWriter as excel
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


time_intervals = [3, 5, 6, 8, 10, 12, 15]

def write_scraped_products(url):
    f = open("record/scraped_products.txt", "a")
    f.write(url + "\n")
    f.close()


def save_urls_to_file(cat_links):
    f = open("record/cat_urls_list.txt", "a")
    f.write(json.dumps(cat_links) + "\n")
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
        else:
            weight = None
    except Exception as e:
        weight = None
        pass
    return weight


def find_weight_from_description(prod_desc):
    weight = ""
    prod_divs = prod_desc.findAll("div", attrs={"class": "productText"})
    for div in prod_divs:
        try:
            div = div.text.strip()
            if len(div.split()) == 1:
                weight = convert_weight_to_kg(div)
                if weight is not None:
                    break
        except Exception as e:
            weight = None
            pass
    if weight is None:
        weight = ""
    return weight


def find_weight_from_title(title : str):
    weight = ""
    splitted_title = title.split(" ")
    for sp_t in splitted_title:
        sp_t = sp_t.split("x")[-1]
        if "g" in sp_t.lower() or "kg" in sp_t.lower() or "ml" in sp_t.lower() or "l" in sp_t.lower():
            weight = convert_weight_to_kg(sp_t)
            if weight is not None:
                break
    if weight is None:
        weight = ""
    return weight


def scrape_product(link, selenium_webdriver):
    print("Scraping product link...")
    selenium_webdriver.init_driver()
    selenium_webdriver.webdriver.get(link)
    WebDriverWait(selenium_webdriver.webdriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div.app > div.ln-o-page > div.ln-o-page__body > div > div > div > section:nth-child(1) > div > div > div.pd__right > h1')))
    selenium_webdriver.accept_cookies()
    page_src = selenium_webdriver.webdriver.page_source
    page_obj = BeautifulSoup(page_src, "lxml")

    prod_title = page_obj.find("h1", attrs={"class": "pd__header"}).text.strip()
    categories_list, tags = get_categories_tags(page_obj)
    try:
        cost_div = page_obj.find("div", attrs={"class": "pd__cost"})
        price = cost_div.find("div", attrs={"data-test-id": "pd-retail-price"}).text.strip()
        price = increase_price_15_percent(price)
        price_per_unit = cost_div.find("span", attrs={"class": "pd__cost__per-unit"}).text.strip()
        weight = find_weight_from_title(prod_title)
        prod_desc = page_obj.find("div", attrs={"class": "ln-c-card pd-details ln-c-card--soft"})
        if weight == "":
            weight = find_weight_from_description(prod_desc)
        prod_desc = str(prod_desc)
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


def scrape_products_page(main_cat, link, selenium_webdriver, list_scraped_products):
    prod_urls_list = []
    selenium_webdriver.init_driver()
    selenium_webdriver.webdriver.get(link)
    selenium_webdriver.accept_cookies()
    try:
        total_products = int(selenium_webdriver.webdriver.find_element_by_id("resultsHeading").text.split("(")[-1].split(" ")[0].replace(",", ""))
    except:
        total_products = -1
    counter = 0
    while True:
        WebDriverWait(selenium_webdriver.webdriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#productLister > ul')))
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
            time.sleep(random.choice(time_intervals))
            counter = 0
        except Exception as e:
            click_no_thanks(selenium_webdriver)
            if counter == 2:
                break
            counter = counter + 1
    selenium_webdriver.close_webdriver()

    if len(prod_urls_list) >= (total_products - 10):
        cat_links = {main_cat: prod_urls_list}
        save_urls_to_file(cat_links)
    else:
        cat_links = {main_cat: []}
        save_urls_to_file(cat_links)
    prod_urls_list = list(set(prod_urls_list))

    for prod_url in prod_urls_list:
        try:
            if prod_url not in list_scraped_products:
                scrape_product(prod_url, selenium_webdriver)
                write_scraped_products(prod_url)
                list_scraped_products.append(prod_url)
                time.sleep(random.choice(time_intervals))
        except Exception as e:
            pass
