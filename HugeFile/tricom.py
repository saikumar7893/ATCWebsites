import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class JobScraperTricom:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "TRICOM Technical Services"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.job_Type = "NA"
        self.contact = "913-652-0600"
        self.Work_Type = "NA"
        self.pay_rate = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
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
        output_folder = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def create_subfolder_with_date(self, output_folder):
        subfolder_path = os.path.join(output_folder, self.current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def create_csv_file(self, subfolder_path):
        file_name = f'job_portal.csv'
        csv_path = os.path.join(subfolder_path, file_name)
        return csv_path

    def scrape_jobs(self):
        output_folder = self.create_output_folder()
        subfolder_path = self.create_subfolder_with_date(output_folder)
        csv_path = self.create_csv_file(subfolder_path)

        for value in self.keywords:
            print(f"Scraping data for the job role: {value}...")
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://tricomts.com/jobs/#!/")
            driver.maximize_window()
            search_ele = driver.find_element(By.XPATH, '//*[@id="job_type_search"]')
            search_ele.send_keys(value)
            driver.find_element(By.XPATH, '//*[@id="job_search_button"]').click()
            time.sleep(20)
            jobs = driver.find_elements(By.XPATH, '//*[@class="echojobs-job ng-scope"]')

            for job in jobs:
                self.job_no += 1
                jobtitle = job.find_element(By.XPATH, './/*[@class="echojobs-listing-job-title"]').text
                if all(keyword.lower() in jobtitle.lower() for keyword in value.split()):
                    joburl = job.find_element(By.XPATH, './/*[@class="echojobs-listing-job-title"]//a').get_attribute('href')
                    if joburl in self.previous_job_urls:
                        continue
                    joblocation = driver.find_element(By.XPATH, './/*[@class="echojobs-listing-location"]').text
                    jobdate = job.find_element(By.XPATH, './/*[@class="echojobs-listing-date-posted ng-binding"]').text[13:]

                    job_category = job.find_element(By.XPATH, '//*[@class="echojobs-listing-details-table"]//tr[1]').text
                    self.job_Type = job.find_element(By.XPATH, '//*[@class="echojobs-listing-details-table"]//tr[3]').text[10:]
                    if "CON" == self.job_Type:
                        self.job_Type = 'Contract'
                        list1 = [self.company_name, self.current_date, jobtitle, self.job_Type, self.pay_rate, joburl,
                                 joblocation, jobdate, self.contact, self.Work_Type]
                        self.npo_jobs[self.job_no] = list1

        # Append or create CSV file
        self.append_or_create_csv(csv_path)

    def append_or_create_csv(self, csv_path):
        print("Generating CSV file")
        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, pd.DataFrame.from_dict(self.npo_jobs, orient='index')],
                                     ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person',
                                                          'Work Type (Remote /Hybrid /Onsite)'])
            npo_jobs_df.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

# Example usage:
# if __name__ == "__main__":
#     scraper = JobScraperTricom()
#     scraper.scrape_jobs()