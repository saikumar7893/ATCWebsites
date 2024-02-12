import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class OakridgeStaffingJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "oakridgestaffing"
        self.current_date = date.today().strftime("%d_%m_%Y")
        self.job_title = "NA"
        self.job_Type = "Contract"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "(914) 471-4290"
        self.Work_Type = "NA"
        self.keywords = ["Data Scientists", "Data engineer", "Business System Analyst"]
        self.previous_job_urls = set()
        self.load_previous_job_urls()

        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())

    def scrape_jobs(self):
        self.driver.get("https://oakridgestaffing.com/jobs/")
        self.driver.maximize_window()
        time.sleep(3)
        self.select_job_types()
        time.sleep(3)
        print("Currently searching on OTTERBASE")

        jobs = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'job_listing') and contains(@class, 'type-job_listing')]")
        for job in jobs:

            self.job_url = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if self.job_url in self.previous_job_urls:
                continue
            self.job_title = job.find_element(By.TAG_NAME, 'h3').text
            self.job_location = job.find_element(By.XPATH, './/div[@class="location"]').text

            for user_input in self.keywords:
                if all(keyword.lower() in self.job_title.lower() for keyword in user_input.split()):
                    self.job_no += 1
                    self.add_job_to_dict()

        if self.job_no == 0:
            print("No jobs available for the particular Role.")
        else:
            self.generate_csv_file()

    def select_job_types(self):
        self.driver.find_element(By.XPATH, '//*[@class="full-time"]').click()
        self.driver.find_element(By.XPATH, '//*[@class="part-time"]').click()
        self.driver.find_element(By.XPATH, '//*[@class="temp-to-perm"]').click()

    def add_job_to_dict(self):
        list1 = [self.company_name, self.current_date, self.job_title, self.job_Type,
                 self.pay_rate, self.job_url, self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
        self.npo_jobs[self.job_no] = list1

    def generate_csv_file(self):
        output_folder = 'output'
        date_folder = os.path.join(output_folder, self.current_date)

        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        print("Generating CSV file")
        npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                             columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                      'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                      'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

        print(npo_jobs_df.head(self.job_no))
        file_name = f'output_oakridgestaffing_{self.current_date}.csv'
        file_path = os.path.join(date_folder, file_name)
        npo_jobs_df.to_csv(file_path, index=False)
        print(f"CSV file '{file_path}' has been generated.")

# if __name__ == "__main__":
#     scraper = OakridgeStaffingJobScraper()
#     scraper.scrape_jobs()