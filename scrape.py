from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from selenium.webdriver.remote.remote_connection import LOGGER
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER.setLevel(logging.DEBUG)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# Replace with the actual URL of the restaurant on Google Maps
URL = "https://maps.app.goo.gl/sK2EFDvi2uVsve6p9"

# Path to your chromedriver executable
CHROMEDRIVER_PATH = '/opt/homebrew/bin/chromedriver'

# Initialize the browser
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Headless mode if you don't need to see the browser
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(URL)
    
    # Wait for the menu tab to be clickable
    menu_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Menu')]"))
    )
    
    # Click on the menu tab
    menu_tab.click()
    
    # Wait for images to load - this might need adjustment based on network speed
    time.sleep(5)  # Adjust this delay as needed
    
    # Find all images in the menu section
    images = driver.find_elements(By.CSS_SELECTOR, "img[role='presentation']")
    
    for i, img in enumerate(images):
        img_url = img.get_attribute('src')
        if img_url and img_url.startswith('http'):  # Ensure it's a valid URL
            # Download the image
            response = requests.get(img_url)
            if response.status_code == 200:
                with open(f'menu_image_{i}.jpg', 'wb') as file:
                    file.write(response.content)
            print(f"Image {i} downloaded from {img_url}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

