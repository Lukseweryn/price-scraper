import re
import os
import json

from web_scraper import ShopScraper
from file_manager import FileManager
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

if __name__ == '__main__':
    shop_info_file = os.path.join(os.path.dirname(__file__), 'shop_information.json')
    if not os.path.exists(shop_info_file):
        fixer.create_shop_information(__file__)
    price_file = os.path.join(os.path.dirname(__file__), 'results.csv')
    if not os.path.exists(price_file):
        fixer.create_results_file(__file__)

    with open(shop_info_file, 'r', encoding='utf-8') as f:
        shops = json.load(f)

    file_manager = FileManager(price_file)
    data = file_manager.read_csv_data()

    for shop in shops:
        try:
            scraper = ShopScraper(shop['url'], 10)
            scraper.rodo_braker()
            price = scraper.price_extraction()
            if price is not None and isinstance(price, str):
                formatted_price = format_price(price)
            else:
                print(f"Warning: price is invalid for {shop['product_name']} from {shop['shop_name']}: {price}")
                formatted_price = ""
            file_manager.merge_data(data, formatted_price, shop['product_name'], shop['shop_name'])
        except Exception as e:
            print(f"Error processing {shop['product_name']} from {shop['shop_name']}: {e}")

    file_manager.write_csv_data(data)
    price_alert.check_price(price_file)
