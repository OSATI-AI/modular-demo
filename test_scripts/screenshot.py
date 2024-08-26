from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def take_screenshot(url, output_file):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')

    # Set up the ChromeDriver service
    service = Service('C:\dev\chromedriver-win64\chromedriver.exe')  # Update this to the correct path

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load completely
        time.sleep(3)  # You can adjust this based on your needs

        # Take a screenshot and save it to the specified file
        driver.save_screenshot(output_file)
        print(f'Screenshot saved to {output_file}')
    finally:
        # Quit the driver
        driver.quit()

# Example usage
url = 'https://www.mathebattle.de/edu_randomtasks/training_show/443'
output_file = 'screenshot.png'
take_screenshot(url, output_file)
