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

class PDSJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "PDS Tech"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "Contract"
        self.pay_rate = "NA"
        self.contact = "https://jobs.pdstech.com/contact-us"
        self.Work_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_title = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer","Business System Analyst"]
        self.output_folder = "output"
        self.previous_job_urls = set()
        self.load_previous_job_urls()

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())


    def create_output_folder(self):
        os.makedirs(self.output_folder, exist_ok=True)

    def create_subfolder_with_date(self):
        today_date = date.today().strftime("%Y-%m-%d")
        subfolder_path = os.path.join(self.output_folder, today_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def create_csv_file(self, subfolder_path):
        file_name = 'job_portal.csv'
        csv_path = os.path.join(subfolder_path, file_name)
        return csv_path

    def append_or_create_csv(self, data):
        subfolder_path = self.create_subfolder_with_date()
        csv_path = self.create_csv_file(subfolder_path)

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            data.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

    def PDS_scrape_jobs(self):
        self.create_output_folder()
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            print("Currently fetching in PDS_Tech")

            driver.get("https://jobs.pdstech.com/jobs/job-search?k=&l=&jobtype=CONTRACT")
            wait = WebDriverWait(driver, 10)
            search = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@placeholder="Job title"])[2]')))
            search.send_keys(user_input)
            driver.maximize_window()
            time.sleep(5)
            search.send_keys(Keys.RETURN)
            time.sleep(5)

            jobs = driver.find_elements(By.XPATH,'//div[@class="job-main"]')
            for job in jobs:
                self.job_title = job.find_element(By.TAG_NAME,'h2')
                self.job_url = self.job_title.find_element(By.TAG_NAME,'a').get_attribute('href')
                if self.job_url in self.previous_job_urls:
                    continue
                details = job.find_elements(By.XPATH,'.//ul[@class="text-muted job--meta"]')
                list1 = []
                for detail in details:
                    for line in detail.text.split("\n"):
                        list1.append(line)
                if len(list1)==2:
                    self.job_loaction = list1[0]
                    self.pay_rate = list1[1]
                    self.job_Posted_Date = "NA"
                    self.Work_Type = "NA"
                elif len(list1)==3:
                    self.job_location = list1[0]
                    self.pay_rate = list1[2]
                    self.job_Posted_Date = list1[1]
                    self.Work_Type = "NA"
                elif len(list1)==4:
                    self.job_location = list1[1]
                    self.pay_rate = list1[3]
                    self.job_Posted_Date = list1[2]
                    self.Work_Type = list1[0]

                self.job_no+=1
                if all(keyword.lower() in self.job_title.text.lower() for keyword in user_input.split()):
                    if self.Work_Type == 'NA':
                        self.Work_Type = 'Hybrid'
                    list1=[self.company_name, self.current_date, self.job_title.text, self.job_Type, self.pay_rate, self.job_url, self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
                    self.npo_jobs[self.job_no] = list1
            driver.quit()

    def PDS_generate_csv(self):
        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV file")
            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])
            self.append_or_create_csv(npo_jobs_df)

# Example usage:
# if __name__ == "__main__":
#     scraper = PDSJobScraper()
#     scraper.PDS_scrape_jobs()
#     scraper.PDS_generate_csv()
