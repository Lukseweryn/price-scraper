import csv
import ctypes
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def check_price(csv_file):
    product_prices = defaultdict(list)
    product_shop = {}

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['PRODUKT']
            try:
                price = float(row['CENA'])
            except (ValueError, TypeError):
                continue
            product_prices[product].append(price)
            product_shop[product] = row.get('SKLEP', 'Unknown shop')

    for product, prices in product_prices.items():
        if len(prices) >= 2:
            last_price = prices[-1]
            prev_price = prices[-2]
            logger.info("%s: last=%.2f, previous=%.2f, change=%.2f",
                        product, last_price, prev_price, last_price - prev_price)
            if last_price != prev_price:
                shop = product_shop.get(product, 'Unknown shop')
                message = f"Product: {product}\nShop: {shop}\nPrice changed from {prev_price} to {last_price}"
                ctypes.windll.user32.MessageBoxW(0, message, "Price Alert", 1)
        else:
            logger.info("%s: not enough data to compare prices yet.", product)
