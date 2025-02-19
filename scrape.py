from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import requests

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to ChromeDriver
CHROMEDRIVER_PATH = '/opt/homebrew/bin/chromedriver'

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigate to the URL
    URL = 'https://maps.app.goo.gl/r5XSrc9fMcfkmbdf8'
    URL2 = 'https://maps.app.goo.gl/T2NW7ruCPQbLXCEQ8'
    URL1 = 'https://maps.app.goo.gl/sK2EFDvi2uVsve6p9'
    driver.get(URL)
    logging.debug(f"Page loaded: {driver.current_url}")

    # Wait for the main image container
    main_image_container = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]"))
    )
    
    # Hover over the main image container
    actions = ActionChains(driver)
    actions.move_to_element(main_image_container).perform()
    logging.debug("Hovered over main image container")

    # Wait for the "See Photos" button to become clickable
    see_photos_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[3]/button/div"))
    )
    see_photos_button.click()
    logging.debug("Clicked 'See Photos' button")

    # Wait for the menu tab to be available and click it
    menu_tab = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Menu')]"))
    )
    menu_tab.click()
    logging.debug("Clicked 'Menu' tab")

    # Wait for all menu images to be present using a pattern
    menu_images = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[1]/div[position()>0]/div/a/div[1]"))
    )
    
    logging.debug(f"Found {len(menu_images)} menu images")

    # Download images
    for i, img in enumerate(menu_images, 1):
        # Try to get the image URL
        img_url = img.get_attribute('src') or img.get_attribute('data-src')  # Check for lazy loading
        if not img_url:
            # If not an img tag, look for background image in style
            style = img.get_attribute('style')
            if style and 'background-image' in style:
                import re
                match = re.search(r'background-image: url\((.*?)\)', style)
                if match:
                    img_url = match.group(1).strip('"')
        
        if img_url and img_url.startswith('http'):
            response = requests.get(img_url)
            if response.status_code == 200:
                with open(f'menu_image_{i}.jpg', 'wb') as file:
                    file.write(response.content)
                logging.info(f"Image {i} downloaded from {img_url}")
            else:
                logging.warning(f"Failed to download image from {img_url}")
        else:
            logging.warning(f"Could not find valid URL for image {i}")

    # If there's more content to load, scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for new images to load

    # Check for newly loaded images
    new_images = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[1]/div[position()>0]/div/a/div[1]"))
    )
    new_images_found = [img for img in new_images if img not in menu_images]
    if new_images_found:
        logging.debug(f"Found {len(new_images_found)} new menu images after scrolling")
        for i, img in enumerate(new_images_found, len(menu_images) + 1):
            # ... (same image download logic as above)
            pass

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    driver.quit()