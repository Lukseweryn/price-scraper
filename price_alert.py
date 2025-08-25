import csv
from collections import defaultdict
import ctypes
import os

# Dictionary to store prices for each product
def check_price(csv_file):
    product_prices = defaultdict(list)

# Read the CSV file
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['PRODUKT']  # Adjust column name if needed
            price = float(row['CENA'])  # Adjust column name if needed
            product_prices[product].append(price)

# Compare last 2 prices for each product
    for product, prices in product_prices.items():
        if len(prices) >= 2:
            last_price = prices[-1]
            prev_price = prices[-2]
            print(f"{product}: Last price = {last_price}, Previous price = {prev_price}, Change = {last_price - prev_price}")
            if last_price != prev_price:
                shop = row['SKLEP'] if 'SKLEP' in row else 'Unknown shop'
                message = f"Product: {product}\nShop: {shop}\nPrice changed from {prev_price} to {last_price}"
                ctypes.windll.user32.MessageBoxW(0, message, "Price Alert", 1)
        else:
            print(f"{product}: Not enough data to compare prices.")
