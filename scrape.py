from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Load ChromeDriver path from environment variable or use default
CHROME_DRIVER_PATH = os.getenv("SBR_WEBDRIVER", "./chromedriver")

def scrape_website(website):
    # Ensure the ChromeDriver path is valid
    if not os.path.isfile(CHROME_DRIVER_PATH):
        raise ValueError("Invalid path to ChromeDriver. Please set SBR_WEBDRIVER in .env")

    print("Connecting to ChromeDriver...")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.binary_location = "/usr/local/bin/google-chrome"  # Adjust path if needed
    chrome_options.add_argument("--headless")  # Run headless if no UI is needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize ChromeDriver with specified path
    service = Service(CHROME_DRIVER_PATH)
    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            driver.get(website)

            # Allow the page content to load
            print("Navigated! Scraping page content...")
            time.sleep(2)  # Adjust as necessary for page load

            html = driver.page_source
            return html
    except Exception as e:
        print(f"Failed to scrape website: {e}")
        return ""

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Clean text with line stripping
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
