import logging
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import fixer

logger = logging.getLogger(__name__)

class ShopScraper:
    """A class to scrape product prices from a given URL using Selenium."""
    def __init__(self, url, wait_time=2):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")

        shop_class_file = os.path.join(os.path.dirname(__file__), "shop_class.json")
        if not os.path.exists(shop_class_file):
            fixer.create_shop_class(__file__)

        with open(shop_class_file, "r", encoding="utf-8") as f:
            shop_class_dict = json.load(f)

        log_path = 'NUL' if os.name == 'nt' else '/dev/null'
        service = Service(log_path=log_path)
        self.driver = webdriver.Chrome(options=chrome_options, service=service)
        self.driver.implicitly_wait(6)
        self.wait_time = wait_time
        self.driver.get(url)

        self.shop_classes = []
        for shop, classes in shop_class_dict.items():
            if shop in url:
                self.shop_classes = classes
                break
        if not self.shop_classes:
            raise ValueError("No matching shop classes found for the provided URL.")

    def rodo_braker(self):
        """Accept cookies on the website."""
        cookie_button_texts = ['zaakceptuj', 'akceptuje', 'w porządku',
                               'zgadzam się', 'akceptuję', 'zgoda']
        accept_cookies_button = None
        action_chains = ActionChains(self.driver, self.wait_time)

        try:
            buttons = self.driver.find_elements(By.XPATH, '//button')
            for button in buttons:
                button_text = button.text.strip()
                if any(text.lower() in button_text.lower()
                       for text in cookie_button_texts):
                    accept_cookies_button = button
                    break
        except Exception:
            pass

        if accept_cookies_button:
            action_chains.move_to_element(accept_cookies_button)
            action_chains.click()
            action_chains.perform()
            logger.info("Cookie consent button clicked.")
            return True
        else:
            logger.info("No cookie consent button found.")
            return False

    def price_extraction(self):
        """Extract the price from the webpage."""
        wait = WebDriverWait(self.driver, self.wait_time)
        price = None
        for class_name in self.shop_classes:
            try:
                price_element = wait.until(lambda d: d.find_element(By.CLASS_NAME, class_name))
                price = price_element.text
                logger.info("Price found with class '%s': %s", class_name, price)
                self.driver.quit()
                break
            except TimeoutException:
                continue
            except Exception:
                logger.warning("Error while searching for price with class '%s'", class_name, exc_info=True)
                continue
        if price is None:
            logger.warning("Price element not found with any of the specified class names.")
            self.driver.quit()
        return price
