from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os

class HuxleyJobScraper:
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

    def __init__(self):
        self.output_manager = self.OutputManager('output')
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Huxley"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "Contract"
        self.contact = "913-652-0600"
        self.Work_Type = "NA"
        self.pay_rate = "NA"
        self.job_postdate = "NA"
        self.joburl = "NA"
        self.jobtitle = "NA"
        self.joblocation = "NA"
        self.jobdate = "NA"
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


    def scrape_data(self, user_input):
        print(f"Scraping data for the job role: {user_input}...")

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.huxley.com/en-gb/job-search/")
        driver.maximize_window()
        time.sleep(5)

        contract = driver.find_element(By.XPATH, '(//span[@class="job-search__checkbox"])[21]')
        contract.click()
        time.sleep(5)

        select_role = driver.find_element(By.XPATH, '//*[@id="keyword"]')
        select_role.send_keys(user_input)

        filter_button = driver.find_element(By.XPATH, '//*[@onclick="js.doFilteredSearch()"]')
        filter_button.click()
        time.sleep(5)

        jobs = driver.find_elements(By.XPATH, '//*[@class="job-search__item"]')
        for job in jobs:
            self.jobtitle = job.find_element(By.TAG_NAME, 'h2').text

            if all(keyword.lower() in self.jobtitle.lower() for keyword in user_input.split()):
                self.job_no += 1
                self.joburl = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if self.joburl in self.previous_job_urls:
                    continue
                details = job.find_elements(By.XPATH, './/*[@class="job-search__details-item"]')
                list1 = [data.text for data in details]
                self.joblocation = list1[0]
                try:
                    self.pay_rate = list1[1]
                except Exception:
                    self.pay_rate = "NA"
                self.jobdate = list1[-1]
                list2 = [self.company_name, self.current_date, self.jobtitle, self.job_Type, self.pay_rate,
                         self.joburl, self.joblocation, self.jobdate, self.contact, self.Work_Type]
                list2 = ['NA' if value == '' else value for value in list2]
                self.npo_jobs[self.job_no] = list2
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
        for keyword in self.keywords:
            self.scrape_data(keyword)
        self.generate_csv()

# Example usage:
# if __name__ == "__main__":
#     huxley_scraper = HuxleyJobScraper()
#     huxley_scraper.scrape_and_generate_csv()