import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class ExperisJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Experis"
        self.contact = "https://www.experis.com/en/about-us/contact-us"
        self.Work_Type = "NA"
        self.job_pay = "NA"
        self.job_title = "NA"
        self.job_type = "NA"
        self.job_url = "NA"
        self.job_location = "NA"
        self.job_post_date = "NA"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientist", "Data engineer","Business System Analyst"]
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

    def scrape_jobs(self):
        self.create_output_folder()
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")

            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.experis.com/en/search?page=1")
            driver.maximize_window()
            time.sleep(5)

            entervalue = driver.find_element(By.XPATH,'//*[@name="searchJobText"]')
            entervalue.send_keys(user_input)
            search = driver.find_element(By.XPATH,'(//*[@class="primary-button orange-sd"])[3]')
            search.click()
            time.sleep(5)
            select_jobtype = driver.find_element(By.XPATH,'(//*[@class="accordion-title "])[3]')
            select_jobtype.click()
            select_contract = driver.find_element(By.XPATH,'//*[@for="1da3cc47022443a5847f4a763213b22a"]')
            select_contract.click()
            time.sleep(10)
            pagenumber = 0

            while pagenumber < 2:
                jobs = driver.find_elements(By.XPATH,'//*[@class="card-body"]')
                pagenumber += 1
                for job in jobs:
                    self.job_no += 1
                    self.job_url = job.find_element(By.TAG_NAME,'a').get_attribute('href')
                    if self.job_url in self.previous_job_urls:
                        continue
                    self.job_title = job.find_element(By.TAG_NAME,'h2').text
                    self.job_location = job.find_element(By.XPATH,'.//*[@class="location"]').text
                    self.job_type = job.find_element(By.XPATH,'//*[@class="type"]').text
                    self.job_post_date = job.find_element(By.XPATH,'.//*[@class="job-actionbar"]').text

                    if all(keyword.lower() in self.job_title.lower() for keyword in user_input.split()):
                        if self.job_location == ',':
                            self.job_location = 'NA'
                        list1 = [self.company_name, self.current_date, self.job_title, self.job_type, self.job_pay, self.job_url, self.job_location, self.job_post_date, self.contact, self.Work_Type]
                        self.npo_jobs[self.job_no] = list1

                time.sleep(5)
                click_next = driver.find_element(By.XPATH,'//*[text()="2"]').click()
                time.sleep(5)

            driver.quit()

    def generate_csv(self):
        if self.job_no == 0:
            print("No jobs available for the particular job.")
        else:
            print("Generating CSV file")
            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

            print(npo_jobs_df.head(self.job_no))
            self.append_or_create_csv(npo_jobs_df)

# # Example usage:
# if __name__ == "__main__":
#     scraper = ExperisJobScraper()
#     scraper.scrape_jobs()
#     scraper.generate_csv()
