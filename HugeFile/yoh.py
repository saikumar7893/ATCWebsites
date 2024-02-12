import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.common.keys import Keys

class JobScraperYoh:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "data engineer", "Business System Analyst"]
        self.company_name = "yoh, A Day & Zimmermann Company"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "215.656.2650"
        self.Work_Type = "NA"
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
        folder_path = os.path.join('output', folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def create_subfolder_with_date(self):
        today_date = date.today().strftime("%Y-%m-%d")
        subfolder_path = self.create_folder(today_date)
        return subfolder_path

    def scrape_jobs(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")

            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://jobs.yoh.com/")
            driver.maximize_window()

            wait = WebDriverWait(driver, 10)
            search_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@class="filter-field"]')))
            search_bar.send_keys(user_input)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(8)

            jobs = driver.find_elements(By.XPATH, '//div[@class="shmJobResultStd shmJobResultundefined"]')
            for job in jobs:
                job_title = job.find_element(By.XPATH, './/div[@class="shmJobtitle"]//a')
                if all(keyword.lower() in job_title.text.lower() for keyword in user_input.split()):
                    #print(job_title.text)
                    self.job_no += 1
                    self.job_url = job_title.get_attribute('href')
                    if self.job_url in self.previous_job_urls:
                        continue
                    #print(self.job_url)
                    self.job_location = job.find_element(By.XPATH, './/div[@class="shmLocation"]').text
                    #print(self.job_location)
                    driver1 = webdriver.Chrome(options=chrome_options)
                    driver1.get(self.job_url)
                    driver1.maximize_window()

                    self.job_Posted_Date = driver1.find_element(By.XPATH, '//span[@data-inline-binding="dynamic_page_collection.postedDate"]').text
                    #print(self.job_Posted_Date)

                    self.job_Type = driver1.find_element(By.XPATH, '(//span[@data-inline-binding="dynamic_page_collection.workType"])[2]').text
                    #print(self.job_Type)

                    list1 = [self.company_name, self.current_date, job_title.text, self.job_Type, self.pay_rate, self.job_url, self.job_location,
                             self.job_Posted_Date, self.contact, self.Work_Type]
                    list1 = ['NA' if value == '' else value for value in list1]
                    self.npo_jobs[self.job_no] = list1
                    driver1.quit()

        # Call the generate_csv method after scraping data for each keyword
        self.generate_csv()

    def generate_csv(self):

        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV file")
            subfolder = self.create_subfolder_with_date()

            csv_file_name = 'job_portal.csv'
            csv_path = os.path.join(subfolder, csv_file_name)

            if os.path.exists(csv_path):
                existing_data = pd.read_csv(csv_path)
                updated_data = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                      columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                               'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                               'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])
                updated_data = pd.concat([existing_data, updated_data], ignore_index=True)
                updated_data.to_csv(csv_path, index=False)
                print(f"Appended data to existing CSV: {csv_path}")
            else:
                npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                     columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                              'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                              'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])
                npo_jobs_df.to_csv(csv_path, index=False)
                print(f"Created new CSV: {csv_path}")

# # # Example usage:
# if __name__ == "__main__":
#     yoh_scraper = JobScraperYoh()
#     yoh_scraper.scrape_jobs()