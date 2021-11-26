import openpyxl


def create_heading():

    headers = ["General Category", "Main Category", "Sub Category", "Sub Sub Category", "Sub Sub Sub Category", "Tags", "SKU", "Title", "Price", "Price/unit", "Weight", "Product Details", "Image 1", "Image 2", "Image 3"]
    workbook_name = "Data/sainsburys_products.xlsx"

    wb_obj = openpyxl.Workbook()
    sheet = wb_obj.active
    sheet.append(headers)
    wb_obj.save(filename=workbook_name)


def write_excel_file(categories_list, tags, sku, title, price, price_per_unit, weight, prod_details, img):
    workbook_name = "Data/sainsburys_products.xlsx"
    wb = openpyxl.load_workbook(workbook_name)
    page = wb.active

    data = ["Groceries", categories_list[0], categories_list[1], categories_list[2], categories_list[3], tags, sku, title, price, price_per_unit, weight, prod_details, img]

    page.append(data)
    wb.save(filename=workbook_name)