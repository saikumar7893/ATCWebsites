import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

class JobScraperApexSystems:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Apex Systems"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "415-767-7224"
        self.Work_Type = "NA"
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

    def create_subfolder_with_date(self):
        subfolder_path = os.path.join(self.create_output_folder(), self.current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def append_or_create_csv(self, subfolder_path, csv_name, data):
        csv_path = os.path.join(subfolder_path, csv_name)
        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            # print(f"Appended data to existing CSV: {csv_path}")
        else:
            data.to_csv(csv_path, index=False)
            # print(f"Created new CSV: {csv_path}")

    def scrape_jobs(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")

            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.apexsystems.com/search-results-usa")
            driver.maximize_window()

            time.sleep(3)
            cookie = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            cookie.click()
            wait = WebDriverWait(driver, 10)
            search = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Keyword"]')))
            search.send_keys(user_input)
            search.send_keys(Keys.RETURN)
            time.sleep(5)

            Jobs = driver.find_elements(By.XPATH, '//a[@class="job-td-link job-title-link"]')
            for job in Jobs:
                job_title = job.text
                job_url = job.get_attribute('href')
                if job_url in self.previous_job_urls:
                    continue
                if all(keyword.lower() in job_title.lower() for keyword in user_input.split()):
                    self.job_no += 1
                    driver2 = webdriver.Chrome(options=chrome_options)
                    driver2.get(job_url)
                    driver2.maximize_window()

                    details = driver2.find_elements(By.XPATH,
                                                    '//*[@class="job-snapshot-wrapper bg-white p-4 mb-4 ab-nav-border-l"]//p')
                    li = []
                    for dt in details:
                        A = dt.text.split(':')
                        li.append(A)
                    driver2.quit()
                    dic = {}
                    for i in range(len(li)):
                        dic[li[i][0]] = li[i][1].strip()

                    self.job_Type = dic.get("Employee Type", "NA")
                    self.pay_rate = dic.get("Pay Range", "NA")
                    self.job_location = dic.get("Location", "NA")
                    self.job_Posted_Date = dic.get("Date Posted", "NA")
                    self.Work_Type = dic.get("Remote", "NA")

                    if self.Work_Type == 'Yes':
                        self.Work_Type = "Remote"
                    else:
                        self.Work_Type = "Onsite"

                    # print(self.job_Type)
                    # print(self.pay_rate)
                    # print(self.job_location)
                    # print(self.job_Posted_Date)
                    # print(self.Work_Type)

                    if self.job_Type == "Contract":
                        list1 = [self.company_name, self.current_date, job_title, self.job_Type, self.pay_rate,
                                 job_url, self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
                        list1 = ['NA' if value == '' else value for value in list1]
                        self.npo_jobs[self.job_no] = list1

        # print("Generating CSV file")
        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV File")
            subfolder = self.create_subfolder_with_date()

            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person',
                                                          'Work Type (Remote /Hybrid /Onsite)'])

            print(npo_jobs_df.head(self.job_no))
            current_date = date.today().strftime("%d_%m_%Y").replace('/', '_')
            file_name = f'job_portal.csv'
            self.append_or_create_csv(subfolder, file_name, npo_jobs_df)
            print(f"CSV file '{file_name}' has been generated.")

# # Example usage:
# if __name__ == "__main__":
#     apex_systems_scraper = JobScraperApexSystems()
#     apex_systems_scraper.scrape_jobs()
