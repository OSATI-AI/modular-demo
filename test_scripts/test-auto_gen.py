import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import base64
import os 
from openai import OpenAI
import time 

MODEL = "gpt-4o"

def get_element_by_id_and_classes(url, element_id, class_names):
    # Send a GET request to the specified URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the element with the specified ID
        element = soup.find(id=element_id)
        
        if element:
            # Create a new BeautifulSoup object for the output
            output_soup = BeautifulSoup('<div></div>', 'html.parser')
            output_div = output_soup.div

            # Find all top-level elements with one of the specified classes
            for child in element.find_all(recursive=False):
                if any(cls in child.get('class', []) for cls in class_names):
                    output_div.append(child)
            
            return output_div
        else:
            return f"Element with ID '{element_id}' not found."
    else:
        return f"Failed to retrieve the page. Status code: {response.status_code}"

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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Example usage
url = 'https://www.mathebattle.de/edu_randomtasks/training_show/443'
element_id = 'content'
class_names = ['typ', 'exercise_question', 'exercise_form']
context = ""
api_key = OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
api_base='https://openrouter.ai/api/v1'
client = OpenAI(base_url=api_base, api_key=api_key)


# for i in range(3):
#     context += f"Example{i+1}:\n"
#     filtered_html = get_element_by_id_and_classes(url, element_id, class_names)
#     context += str(filtered_html) + "\n\n"

img_path = "screenshot.png"
print("Take screenshot ...")
take_screenshot(url, img_path)

print("Encode to base64 ...")
base64_image = encode_image(img_path)


print("Wait for LLM response ...")
response = client.chat.completions.create(
    model=MODEL,
    messages=[
            {"role": "user", "content": [
            {"type": "text", "text": "Describe the image."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.0,
)

print(response.choices[0].message.content)
