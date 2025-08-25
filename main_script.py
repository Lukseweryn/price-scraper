import re
import os
import json

from web_scraper import ShopScraper  # Assuming web_scraper.py is in the same directory
from file_manager import FileManager  # Assuming file_manager.py is in the same directory
import fixer
import price_alert

def format_price(price_str):
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[^\d,\.]', '', price_str)
    # Replace comma with dot if comma is used as decimal separator
    if ',' in cleaned and '.' not in cleaned:
        cleaned = cleaned.replace(',', '.')
    # Remove any thousands separator (assuming . or ,)
    cleaned = re.sub(r'(?<=\d)[.,](?=\d{3}\D)', '', cleaned)
    return cleaned

shop_info_file = os.path.join(os.path.dirname(__file__), 'shop_information.json')
if not os.path.exists(shop_info_file):
    fixer.create_shop_information(__file__)
price_file = os.path.join(os.path.dirname(__file__), 'results.csv')
if not os.path.exists(price_file):
    fixer.create_results_file(__file__)

# Load the shops with url & product from the JSON file
with open(shop_info_file, 'r', encoding='utf-8') as f:
    shops = json.load(f)
for shop in shops:
    # Use the ShopScraper class
    scraper = ShopScraper(shop['url'], 2)
    scraper.rodo_braker()
    price = scraper.price_extraction()
    if price is not None and isinstance(price, str):
        formatted_price = format_price(price)
    else:
        print(f"Warning: price is invalid for {shop['product_name']} from {shop['shop_name']}: {price}")
        formatted_price = ""
    price = formatted_price
    file_manager = FileManager(price_file)
    loaded_data = file_manager.read_csv_data()
    new_data = file_manager.merge_data(loaded_data, price, shop['product_name'], shop['shop_name'])
    file_manager.write_csv_data(new_data)

# Call the price alert function
price_alert.check_price(price_file)
