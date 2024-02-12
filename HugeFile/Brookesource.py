from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os

class BrookSourceJobScraper:
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
        self.list1 = []
        self.company_name = "BrookSource"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "NA"
        self.contact = "800.611.3995"
        self.Work_Type = "NA"
        self.npo_jobs = {}
        self.job_no = 0
        self.pay_rate = "NA"
        self.job_postdate = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "Systems Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.previous_job_urls = set()
        self.load_previous_job_urls()

        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://jobs.brooksource.com/")
        self.driver.maximize_window()

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())

    def click_contract_checkbox(self):
        self.driver.find_element(By.XPATH, '//*[@data-value="contract"]').click()
        time.sleep(10)

    def load_more_jobs(self):
        while True:
            try:
                load_more_button = self.driver.find_element(By.XPATH, '//button[@class="fwp-load-more"]')
                load_more_button.click()
                time.sleep(2)
            except Exception:
                break

    def scrape_jobs(self):
        self.click_contract_checkbox()
        self.load_more_jobs()

        jobs = self.driver.find_elements(By.XPATH, '//*[contains(@class, "job-type-contract")]//a')

        for job in jobs:
            job_url = job.get_attribute('href')

            if job_url in self.previous_job_urls:
                continue

            content = job.find_elements(By.XPATH, './/*[@class="description"]')

            for ss in content:
                job_title = ss.find_element(By.TAG_NAME, 'h3').text

                job_data = ss.find_elements(By.TAG_NAME, 'li')

                try:
                    self.list1 = []  # Clear list1 for each iteration
                    for dd in job_data:
                        self.list1.append(dd.text)

                    self.job_Type = self.list1[0]
                    self.company_name = self.list1[1]
                    job_location = self.list1[2]

                    for user_input in self.keywords:
                        if all(keyword.lower() in job_title.lower() for keyword in user_input.split()):
                            list2 = [self.company_name, self.current_date, job_title, self.job_Type, self.pay_rate,
                                     job_url, job_location, self.job_postdate, self.contact, self.Work_Type]
                            list2 = ['NA' if value == '' else value for value in list2]
                            self.npo_jobs[self.job_no] = list2
                            self.job_no += 1
                except Exception as e:
                    print(f"Error processing job: {e}")

        # Call the generate_csv method after scraping data for each job
        self.generate_csv()

    def generate_csv(self):
        if self.job_no == 0:
            print("No new jobs available since the last run.")
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

# Example usage:
if __name__ == "__main__":
    brook_source_scraper = BrookSourceJobScraper()
    brook_source_scraper.scrape_jobs()