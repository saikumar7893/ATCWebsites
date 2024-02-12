import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

class JobScraperInsightGlobal:
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
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Insight Global"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_title = "NA"
        self.job_Type = "NA"
        self.pay_rate = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "855-485-8853"
        self.Work_Type = "NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.output_manager = self.OutputManager('output')  # Instantiating OutputManager
        self.previous_job_urls = set()
        self.load_previous_job_urls()

    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())

    def scrape_jobs(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")
            i = 2

            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://jobs.insightglobal.com/")
            driver.maximize_window()

            search_bar = driver.find_element(By.XPATH, '//input[@placeholder="Title or keyword"]')
            search_bar.send_keys(user_input)
            search_icon = driver.find_element(By.XPATH, '//input[@id="homesearch"]')
            search_icon.click()

            while True:
                jobs = driver.find_elements(By.XPATH, '//div[@class="result"]')
                for job in jobs:
                    self.job_no += 1
                    job_title = job.find_element(By.XPATH, './/div[@class="job-title"]//a')

                    if all(keyword.lower() in job_title.text.lower() for keyword in user_input.split()):
                        self.job_Posted_Date = job.find_element(By.XPATH, './/p[@class="date"]').text
                        self.job_url = job_title.get_attribute('href')
                        if self.job_url in self.previous_job_urls:
                            continue
                        details = job.find_elements(By.XPATH, './/div[@class="job-info"]//p')

                        list1 = [detail.text for detail in details]

                        self.job_location = list1[0]
                        self.job_Type = list1[2]

                        try:
                            self.pay_rate = list1[3]
                        except Exception:
                            self.pay_rate = "NA"

                        if 'contract' in self.job_Type.lower():
                            list1 = [self.company_name, self.current_date, job_title.text, self.job_Type, self.pay_rate,
                                     self.job_url, self.job_location, self.job_Posted_Date, self.contact, self.Work_Type]
                            list1 = ['NA' if value == '' else value for value in list1]
                            self.npo_jobs[self.job_no] = list1


                next_url = "https://jobs.insightglobal.com/jobs/find_a_job/" + str(i) + "/?rd=Distance&remote=false&miles=False&srch=" + user_input.replace(" ", "+")
                driver.get(next_url)
                if i == 10:
                    break
                i += 1
                time.sleep(2)

            # Close the browser after scraping data for each keyword
            driver.quit()

            # Call the generate_csv method after scraping data for each keyword
            self.generate_csv()

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

# Example usage:
# if __name__ == "__main__":
#     insight_global_scraper = JobScraperInsightGlobal()
#     insight_global_scraper.scrape_jobs()