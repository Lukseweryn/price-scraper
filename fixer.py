import json
import logging
import os

logger = logging.getLogger(__name__)

def create_shop_class(caller_path):
    """Create a JSON file with default shop class information."""
    shop_class_file = os.path.join(os.path.dirname(caller_path), "shop_class.json")
    default_shop_class_dict = {
        'crop': ['priceview__FinalPriceWrapper-sc-1d2v9as-0'],
        'medicine': [
            'ProductCard__priceSaleMinimal__mlyb5',
            'ProductCard__priceRegular__crOK3'
        ],
        'mediaexpert': ['main-price'],
        'x-kom': ['sc-jnqLxu'],
        'empik': ['css-1f0k13e-DesktopPriceStyles'],
    }
    try:
        with open(shop_class_file, "w", encoding="utf-8") as f:
            json.dump(default_shop_class_dict, f, ensure_ascii=False, indent=4)
        logger.info("shop_class.json created successfully.")
    except Exception:
        logger.exception("Error creating shop_class.json.")

def create_shop_information(caller_path):
    """Create a JSON file with default shop information."""
    shop_info_file = os.path.join(os.path.dirname(caller_path), "shop_information.json")
    default_shops_information = [
        {
            'url': 'https://www.cropp.com/pl/pl/bezowe-spodnie-z-lnem-500de-08x?algolia_query_id=df76b8e4a6111ebf47ca401534da8834',
            'shop_name': 'cropp',
            'product_name': 'Spodnie wide leg w paski',
        },
        {
            'url': 'https://www.empik.com/lego-speed-champions-klocki-bolid-f1-ferrari-sf-24-77242-lego,p1576044526,zabawki-p',
            'shop_name': 'empik',
            'product_name': 'Lego Ferrari SF-23',
        },
        {
            'url': 'https://wearmedicine.com/p/pasek-dwustronny-meski-ze-skory-ekologicznej-kolor-brazowy-1038430',
            'shop_name': 'medicine',
            'product_name': 'Pasek męski',
        }
    ]
    try:
        with open(shop_info_file, 'w', encoding='utf-8') as f:
            json.dump(default_shops_information, f, ensure_ascii=False, indent=4)
        logger.info("shop_information.json created successfully.")
    except Exception:
        logger.exception("Error creating shop_information.json.")

def create_results_file(caller_path):
    """Create a CSV file where results will be stored."""
    shop_results_file = os.path.join(os.path.dirname(caller_path), "results.csv")
    try:
        with open(shop_results_file, 'w', encoding='utf-8') as f:
            f.write("SKLEP,PRODUKT,CENA,DATA\n")
        logger.info("results.csv created successfully.")
    except Exception:
        logger.exception("Error creating results.csv.")
