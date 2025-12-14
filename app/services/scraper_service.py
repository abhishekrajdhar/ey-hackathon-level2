import logging
import time
import os
import requests
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.core.scraper_utils import get_selenium_driver
from app.db import models
from datetime import date, timedelta

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self, download_dir: str = "tmp_downloads"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
    
    def fetch_page_source(self, url: str) -> str:
        driver = get_selenium_driver()
        try:
            driver.get(url)
            # Wait for potential dynamic content
            time.sleep(3) 
            return driver.page_source
        finally:
            driver.quit()

    def download_file(self, url: str) -> Optional[str]:
        """
        Downloads a file from a URL and returns the local path.
        """
        try:
            local_filename = url.split('/')[-1]
            # Sanitize filename if needed
            if not local_filename.lower().endswith('.pdf'):
                local_filename += ".pdf"
                
            path = os.path.join(self.download_dir, local_filename)
            
            # Simple requests download (for direct links)
            # For authorized downloads, cookies would need to be passed from Selenium
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return path
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

class GenericPSUScraper(ScraperService):
    """
    A specific implementation for a generic PSU portal structure.
    Needs to be adapted for specific websites.
    """
    
    def scrape_listings(self, url: str) -> List[Dict]:
        """
        Scrapes a table of tenders from a PSU portal.
        Handles generic tables and specific etenders.gov.in CAPTCHA flows.
        """
        driver = get_selenium_driver()
        listings = []
        try:
            logger.info(f"Navigating to {url}")
            driver.get(url)
            
            # Check for CAPTCHA
            if self._handle_captcha(driver):
                 logger.info("CAPTCHA handled, waiting for results...")
                 time.sleep(5) # Wait for reload
            
            # Logic for etenders.gov.in table structure (often class="list_table")
            # Try to find the main results table
            tables = driver.find_elements(By.CLASS_NAME, "list_table")
            target_table = tables[-1] if tables else None # Usually the last one is results
            
            if not target_table:
                 # Fallback to any table
                 target_table = driver.find_element(By.TAG_NAME, "table")
            
            rows = target_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                # Heuristic: Valid rows usually have 4+ columns (ID, Title, Dates, Links)
                if len(cols) >= 4:
                    try:
                        title_text = cols[1].text.strip() # Assuming Title is 2nd col
                        if not title_text or "Title" in title_text: continue 

                        links = cols[-1].find_elements(By.TAG_NAME, "a")
                        doc_url = links[0].get_attribute("href") if links else None
                        
                        # sometimes link is in other columns
                        if not doc_url:
                             for col in cols:
                                 alink = col.find_elements(By.TAG_NAME, "a")
                                 if alink and "Download" in alink[0].get_attribute("title"):
                                     doc_url = alink[0].get_attribute("href")
                                     break
                        
                        listings.append({
                            "title": title_text,
                            "doc_url": doc_url,
                        })
                    except Exception as e:
                        continue
                    
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
        finally:
            driver.quit()
            
        return listings

    def _handle_captcha(self, driver) -> bool:
        """
        Detects and attempts to solve a CAPTCHA if present.
        Returns True if a captcha was found and submitted.
        """
        try:
            from app.core.scraper_utils import solve_simple_captcha
            
            # Specific selectors for etenders.gov.in
            captcha_img = driver.find_elements(By.ID, "captchaImage")
            captcha_input = driver.find_elements(By.ID, "captchaText")
            submit_btn = driver.find_elements(By.ID, "Submit")
            
            if captcha_img and captcha_input and submit_btn:
                logger.info("Found CAPTCHA. Attempting to solve...")
                
                # Take screenshot of the captcha element
                img_element = captcha_img[0]
                img_path = os.path.join(self.download_dir, "captcha_tmp.png")
                img_element.screenshot(img_path)
                
                # Solve
                solution = solve_simple_captcha(img_path)
                logger.info(f"Solved Text: {solution}")
                
                # Input
                captcha_input[0].clear()
                captcha_input[0].send_keys(solution)
                
                # Submit
                submit_btn[0].click()
                return True
                
        except Exception as e:
            logger.warning(f"Captcha handling failed: {e}")
        
        return False
