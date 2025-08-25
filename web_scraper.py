from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import os
import fixer

class ShopScraper:
    """A class to scrape product prices from a given URL using Selenium."""
    def __init__(self, url, wait_time=2):
        #set up the Chrome driver with headless mode, disable GPU for compatibility and shm for docker
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")  # Suppress DevTools message
        # Path to the JSON file
        shop_class_file = os.path.join(os.path.dirname(__file__), "shop_class.json")

        # If the JSON file does not exist, create it with default values
        if not os.path.exists(shop_class_file):
            fixer.create_shop_class(__file__)

        # Load the shops with html classes that corespond to price object from the JSON file
        with open(shop_class_file, "r", encoding="utf-8") as f:
            shop_class_dict = json.load(f)

        #activare webdriver
        # Use correct log_path for Windows and Linux/Mac
        log_path = 'NUL' if os.name == 'nt' else '/dev/null'
        service = Service(log_path=log_path)
        self.driver = webdriver.Chrome(options=chrome_options, service=service)
        self.driver.implicitly_wait(6)  # seconds
        self.wait_time = wait_time
        self.driver.get(url)   
        #Get shop classes
        self.shop_classes = []
        for shop, classes in shop_class_dict.items():
            if shop in url:
                self.shop_classes = classes
                break
        if not self.shop_classes:
            raise ValueError("No matching shop classes found for the provided URL.")

    def rodo_braker(self):
        """Accept cookies on the website."""
        # Define the button texts that indicate acceptance of cookies can be extended
        # to include other languages or variations
        cookie_button_texts = ['zaakceptuj', 'akceptuje', 'w porządku'
                               , 'zgadzam się', 'akceptuję', 'zgoda']
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
        except:
            pass

        if accept_cookies_button:
            action_chains.move_to_element(accept_cookies_button)
            action_chains.click()  
            action_chains.perform()  # Perform the action
            print('Cookie button clicked.')
            return True
        else:
            print('No cookie button found.')
            return False


    def price_extraction(self):
        """Extract the price from the webpage."""
        wait = WebDriverWait(self.driver, self.wait_time)
        price_class_names = self.shop_classes 
        price = None
        for class_name in price_class_names:
            try:
                price_element = wait.until(lambda d: d.find_element(By.CLASS_NAME, class_name))
                price = price_element.text
                print(f'Price found with class "{class_name}": {price}')
                self.driver.quit()
                break
            except TimeoutException:
                continue
            except Exception as e:
                print(f'Error while searching for price: {e}')
                continue
        if price is None:
            print('Price element not found with any of the specified class names.')
        return price