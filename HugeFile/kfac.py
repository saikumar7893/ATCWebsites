import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import date
import pandas as pd
import time

class OutputManager:
    def __init__(self, base_folder):
        self.base_folder = base_folder

    def create_folder(self, folder_name):
        folder_path = os.path.join(self.base_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def create_subfolder_with_date(self):
        today_date = date.today().strftime("%Y-%m-%d")
        subfolder_path = self.create_folder(today_date)
        return subfolder_path

    def append_or_create_csv(self, subfolder_path, csv_name, data):
        csv_path = os.path.join(subfolder_path, csv_name)

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            data.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

class KforceJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Kforce Inc"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_title = "NA"
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "1-877-453-6723"
        self.Work_Type = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer",
                         "Business System Analyst"]
        self.output_manager = OutputManager('output')
        self.previous_job_urls = set()
        self.load_previous_job_urls()

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())


    def scrape_data(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")

            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.kforce.com/find-work/search-jobs/#/?t=&l=%5B%5D")
            driver.maximize_window()

            wait = WebDriverWait(driver, 10)
            search = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@placeholder='Search by Job Title or Skill']")))
            search.send_keys(user_input)
            search.send_keys(Keys.RETURN)
            time.sleep(3)

            jobs = driver.find_elements(By.XPATH, "//ul[@class='data-jobs']//li[@class='row']")

            for job in jobs:
                self.job_title = job.find_element(By.TAG_NAME, "a")
                self.job_url = self.job_title.get_attribute("href")
                if self.job_url in self.previous_job_urls:
                    continue
                self.job_no += 1

                self.job_Posted_Date = job.find_element(By.TAG_NAME, "span").text
                self.job_Type = job.find_element(By.XPATH, ".//span[@class='type']").text
                self.job_location = job.find_element(By.XPATH, ".//span[@class='locations']").text


                if all(keyword.lower() in self.job_title.text.lower() for keyword in user_input.split()):
                    if 'contract' in self.job_Type.lower():
                        list1 = [self.company_name, self.current_date, self.job_title.text, self.job_Type,
                                 self.pay_rate, self.job_url, self.job_location, self.job_Posted_Date, self.contact,
                                 self.Work_Type]
                        list1 = ['NA' if value == '' else value for value in list1]
                        self.npo_jobs[self.job_no] = list1

            driver.quit()

    def generate_csv(self):

        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV file")
            subfolder = self.output_manager.create_subfolder_with_date()

            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person',
                                                          'Work Type (Remote /Hybrid /Onsite)'])

            print(npo_jobs_df.head(self.job_no))
            current_date = date.today().strftime("%d_%m_%Y").replace('/', '_')
            file_name = f'job_portal.csv'
            self.output_manager.append_or_create_csv(subfolder, file_name, npo_jobs_df)
            print(f"CSV file '{file_name}' has been generated.")

    def scrape_and_generate_csv(self):
        self.scrape_data()
        self.generate_csv()
#
# if __name__ == "__main__":
#     kforce_scraper = KforceJobScraper()
#     kforce_scraper.scrape_and_generate_csv()