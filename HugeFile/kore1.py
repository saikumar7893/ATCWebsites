import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class Kore1JobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.company_name = "KORE1"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.contact = "NA"
        self.Work_Type = "NA"
        self.job_title = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_Posted_Date = "NA"
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
        subfolder_path = os.path.join(self.output_folder, self.current_date)
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

    def scrape_kore1_jobs(self):
        self.create_output_folder()
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://search10.smartsearchonline.com/koreone/jobs/")
        time.sleep(5)
        print("Currently Fetching jobs in the KORE1")

        jobs = driver.find_elements(By.XPATH, '//div[@class="list-group-item"]')
        for job in jobs:
            job_title = job.find_element(By.XPATH, './/a[@class="coloredlink bold"]').text
            job_url = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if job_url in self.previous_job_urls:
                continue
            for user_input in self.keywords:
                if all(keyword.lower() in job_title.lower() for keyword in user_input.split()):
                    driver1 = webdriver.Chrome(options=chrome_options)
                    driver1.get(job_url)
                    time.sleep(5)
                    job_Posted_Date = driver1.find_element(By.XPATH, '(//*[@class="col-xs-8 col-sm-9 col-md-10"])[2]').text
                    pay_rate = driver1.find_element(By.XPATH, '(//*[@class="col-xs-8 col-sm-9 col-md-10"])[7]').text
                    job_loaction = driver1.find_element(By.XPATH, '(//*[@class="col-xs-8 col-sm-9 col-md-10"])[6]').text
                    job_Type_1 = driver1.find_element(By.XPATH, '(//*[@class="col-xs-8 col-sm-9 col-md-10"])[4]').text
                    if "contract".lower() in job_Type_1.lower():
                        self.job_Type = job_Type_1
                        self.job_no += 1
                        list1 = [self.company_name, self.current_date, job_title, self.job_Type, pay_rate, job_url, job_loaction, job_Posted_Date, self.contact, self.Work_Type]
                        self.npo_jobs[self.job_no] = list1
                    driver1.quit()
                    break

        driver.quit()

    def generate_kore1_csv(self):
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
#     scraper = Kore1JobScraper()
#     scraper.scrape_kore1_jobs()
#     scraper.generate_kore1_csv()
