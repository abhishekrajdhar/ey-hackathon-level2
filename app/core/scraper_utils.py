import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

def get_selenium_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Sets up a Selenium Chrome driver.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Mask automation to avoid basic bot detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Selenium driver: {e}")
        raise

def solve_simple_captcha(image_path: str) -> str:
    """
    Uses Tesseract OCR to solve simple alphanumeric CAPTCHAs.
    """
    try:
        image = Image.open(image_path)
        # Basic preprocessing could be added here (grayscale, thresholding)
        text = pytesseract.image_to_string(image, config='--psm 8') # psm 8 = Single word
        clean_text = "".join(filter(str.isalnum, text))
        return clean_text
    except Exception as e:
        logger.error(f"CAPTCHA solving failed: {e}")
        return ""
