import undetected_chromedriver as uc

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import matplotlib.pyplot as plt
import random
import pandas as pd
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import math
class TeacherScraper:
    def __init__(self,url:str,max_page:int=math.inf):
        self.url = url 
        self.max_page = max_page
        self.driver = self.open_chrome()
        self.open_url()
        self.history = pd.DataFrame(columns=["title", "link", "address", "deadline", "salary"]) 
    def open_chrome(self):
        # Set up Chrome options
        chrome_options = uc.ChromeOptions() 
        # Appearance
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        # Stealth
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--headless=new")
  

        # Use a custom user-agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/119.0.0.0 Safari/537.36")

        # Load Chrome with a user profile (to open with an account)
        # Replace below path with your actual user profile path
        temp_profile_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chrome_options.add_argument(r"--profile-directory=Default")
        chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Path to Chrome binary
        # Set up the Chrome WebDriver
        driver = uc.Chrome( options=chrome_options,version_main=135)

        return driver
    def open_url(self): 
        self.driver.get(self.url)
        time.sleep(random.uniform(0.5, 1.5))  # Random sleep between 0.5 and 1.5 seconds
    def scrape_website(self): 
        self.set_max_page()
        while True: 
            self.scrape_page_data() 
            if not self.go_to_next_page():
                break
        self.driver.quit()
        self.history.to_csv("scraped_data.csv", index=False)  # Save the data to a CSV file
    def go_to_next_page(self):
        parsed_url = urlparse(self.url)
        query_params = parse_qs(parsed_url.query)

        if 'page' in query_params:
            query_params['page'] = [str(int(query_params['page'][0]) + 1)]
        else:
            query_params['page'] = ['2']
        if int(query_params['page'][0]) > self.max_page:
            return False
        updated_query = urlencode(query_params, doseq=True)
        self.url = urlunparse(parsed_url._replace(query=updated_query))
        self.driver.get(self.url)
        return True
    def set_max_page(self):  
        try:
            # Wait for the <li> elements to load
            WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
            )
            # Find all <li> elements
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")
            if len(li_elements) >= 2:    
                second_last_li = li_elements[-2]
                text_content = second_last_li.text
                if int(text_content) < self.max_page:
                    self.max_page = int(text_content)
                print("Max page:", self.max_page)
        except Exception as e:
            print("Error while collecting data on page:", e) 
    def scrape_page_data(self): 
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job-contain"))
            )
            job_elements = self.driver.find_elements(By.CLASS_NAME, "job-contain")
            for job in job_elements:
                title_element = job.find_element(By.CLASS_NAME, "card-job-title")
                title = title_element.text
                link = title_element.get_attribute("href")
                address_deadline_element = job.find_element(By.CLASS_NAME, "address-deadline")
                address_deadline_parts = address_deadline_element.find_elements(By.CLASS_NAME, "mb-0")
                address = address_deadline_parts[0].text if len(address_deadline_parts) > 0 else None
                deadline = address_deadline_parts[1].text if len(address_deadline_parts) > 1 else None
                salary_element = job.find_element(By.CLASS_NAME, "salary-cont")
                salary = salary_element.text if salary_element else None
                deadline = deadline.replace("Deadline: ", "") if deadline else None
                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Address: {address}")
                print(f"Deadline: {deadline}")
                print(f"Salary: {salary}")
                print("-" * 40)
                self.history = pd.concat([self.history, pd.DataFrame({"title": [title], "link": [link], "address": [address], "deadline": [deadline], "salary": [salary]})], ignore_index=True)
        except Exception as e:
            print("Error while collecting data on page:", e)

if __name__ == "__main__": 
    teacherScraper:TeacherScraper = TeacherScraper("https://www.edjoin.org/Home/Jobs?keywords=teacher&searchType=all")
    teacherScraper.scrape_website()