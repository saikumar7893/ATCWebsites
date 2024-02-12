import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests
import re

class PalmerGroupJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.job_title = "NA"    #yes
        self.job_Type = "NA"   #yes
        self.pay_rate = "NA"     #yes
        self.job_url = "NA"      #yes
        self.job_location = "NA"     #yes
        self.job_Posted_Date= "NA"   #yes
        self.Work_Type = "NA"    #yes
        self.list2 = []
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer","Business System Analyst"]
        self.company_name = "Palmer Group"
        self.contact = "(515) 225-7000"     #yes
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.output_folder = "output"
        self.create_output_folder()

    def create_output_folder(self):
        os.makedirs(self.output_folder, exist_ok=True)

    def create_subfolder_with_date(self):
        subfolder_path = os.path.join(self.output_folder, self.current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def create_csv_file(self):
        subfolder_path = self.create_subfolder_with_date()
        file_name = 'job_portal.csv'
        csv_path = os.path.join(subfolder_path, file_name)
        return csv_path

    def append_or_create_csv(self, data):
        csv_path = self.create_csv_file()

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            data.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

    def scrape_jobs(self):
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")

            driver.get("https://jobs.thepalmergroup.com/")
            driver.maximize_window()
            time.sleep(2)

            search = driver.find_element(By.XPATH,'//input[@class="facetwp-search"]')
            search.send_keys(user_input)
            time.sleep(3)

            contract_btn = driver.find_element(By.XPATH,'//div[@data-value="contract"]')
            contract_btn.click()
            time.sleep(3)

            type = 1
            while True:
                if type == 1:
                    hybrid_btn = driver.find_element(By.XPATH,'//div[@data-value="hybrid"]')
                    hybrid_btn.click()
                    Work_Type = 'hybrid'
                    time.sleep(3)
                elif type == 2:
                    remote_btn = driver.find_element(By.XPATH,'//div[@data-value="remote"]')
                    remote_btn.click()
                    Work_Type = 'remote'
                    time.sleep(3)
                else:
                    onsite_btn = driver.find_element(By.XPATH,'//div[@data-value="on-site"]')
                    onsite_btn.click()
                    Work_Type = 'on-site'
                    time.sleep(3)

                jobs = driver.find_elements(By.XPATH,"//*[contains(@class, 'job_listing') and contains(@class, 'type-job_listing') and contains(@class, 'status')]")
                for job in jobs:
                    self.job_url = job.find_element(By.TAG_NAME,'a').get_attribute('href')
                    self.job_title = job.find_element(By.XPATH,'.//div[@class="position"]//h3').text
                    self.job_location = job.find_element(By.XPATH,'.//li[@class="location"]').text
                    self.job_Type = job.find_element(By.XPATH,'.//li[@class="job-type contract"]').text
                    self.pay_rate = job.find_element(By.XPATH,'.//li[@class="xs-pay"]').text
                    self.job_Posted_Date = job.find_element(By.XPATH,'.//li[@class="date-posted"]//time').get_attribute('datetime')
                    if all(keyword.lower() in self.job_title.lower() for keyword in user_input.split()):
                        if self.job_title not in self.list2:
                            self.list2.append(self.job_title)
                            self.job_no += 1
                            list1=[self.company_name, self.current_date, self.job_title, self.job_Type, self.pay_rate, self.job_url, self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
                            self.npo_jobs[self.job_no] = list1

                if type == 1:
                    hybrid_btn1 = driver.find_element(By.XPATH,'//div[@data-value="hybrid"]')
                    hybrid_btn1.click()
                    time.sleep(5)
                    type += 1
                elif type == 2:
                    remote_btn1 = driver.find_element(By.XPATH,'//div[@data-value="remote"]')
                    remote_btn1.click()
                    time.sleep(5)
                    type += 1
                else:
                    break

        driver.quit()

    def generate_csv(self):
        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV file")
            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

            print(npo_jobs_df.head(self.job_no))
            self.append_or_create_csv(npo_jobs_df)

# Example usage:
# if __name__ == "__main__":
#     scraper = PalmerGroupJobScraper()
#     scraper.scrape_jobs()
#     scraper.generate_csv()
