import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests

class JudgeJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "The Judge Group Inc"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_title = "NA"
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "(800)-301-0110"
        self.Work_Type = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.output_folder = "output"
        self.subfolder = self.create_subfolder_with_date()
        self.csv_file_name = 'job_portal.csv'
        self.csv_file_path = os.path.join(self.subfolder, self.csv_file_name)
        self.previous_job_urls = set()
        self.load_previous_job_urls()

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())

    def create_folder(self, folder_name):
        folder_path = os.path.join(self.output_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def create_subfolder_with_date(self):
        today_date = date.today().strftime("%Y-%m-%d")
        subfolder_path = self.create_folder(today_date)
        return subfolder_path

    def append_or_create_csv(self, data):
        if os.path.exists(self.csv_file_path):
            existing_data = pd.read_csv(self.csv_file_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_csv(self.csv_file_path, index=False)
            print(f"Appended data to existing CSV: {self.csv_file_path}")
        else:
            data.to_csv(self.csv_file_path, index=False)
            print(f"Created new CSV: {self.csv_file_path}")

    def scrape_jobs(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.judge.com/jobs/")
            driver.maximize_window()

            wait = WebDriverWait(driver, 10)
            try:
                pop_up = wait.until(EC.presence_of_element_located((By.XPATH,'//button[@class="pum-close popmake-close"]')))
                pop_up.click()
            except Exception:
                continue

            search = wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="jdg-job-search"]')))
            search.send_keys(user_input)
            search.send_keys(Keys.RETURN)
            time.sleep(5)

            contract = wait.until(EC.presence_of_element_located ((By.XPATH,'(//label[@class="jdg-form-label-choice"])[1]')))
            contract.click()
            time.sleep(2)

            jobs = driver.find_elements(By.XPATH,'//div[@class="jdg-job-preview"]')
            for i in range(20):
                self.job_no += 1
                self.job_title = jobs[i].find_element(By.TAG_NAME,'h2').text
                self.job_url = jobs[i].find_element(By.TAG_NAME,'a').get_attribute('href')
                if self.job_url in self.previous_job_urls:
                    continue
                self.job_location = jobs[i].find_element(By.XPATH,'.//p[@class="jdg-job-location jdg-type-body--large"]').text
                self.job_Posted_Date = jobs[i].find_element(By.XPATH,'.//p[@class="jdg-job-date"]').text

                details = jobs[i].find_elements(By.XPATH,'.//span[@class="jdg-tag jdg-type-utility--reduced"]')
                list1 = [detail.text for detail in details]

                self.job_Type = list1[0]
                if len(list1) == 3:
                    self.pay_rate = list1[2]
                else:
                    self.pay_rate = 'NA'

                if 'contract' in self.job_Type.lower():
                    list1 = [self.company_name, self.current_date, self.job_title, self.job_Type, self.pay_rate, self.job_url,
                             self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
                    list1 = ['NA' if value == '' else value for value in list1]
                    self.npo_jobs[self.job_no] = list1

            driver.quit()

    def generate_csv(self):

        if self.job_no == 0:
            print("No new jobs available since the last run.")
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
#     judge_scraper = JudgeJobScraper()
#     judge_scraper.scrape_jobs()
#     judge_scraper.generate_csv()