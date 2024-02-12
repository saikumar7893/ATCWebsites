import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class CollaberaJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Collabera"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.job_Type = "NA"
        self.contact = "877.264.6424"
        self.Work_Type = "NA"
        self.pay_rate = "NA"
        self.job_postdate = "NA"
        self.job_url="NA"
        self.job_title="NA"
        self.job_location="NA"
        self.job_date="NA"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientist", "Data Engineer", "Business System Analyst"]
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
        file_name = f'job_portal.csv'
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

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://collabera.com/job-search/")
        driver.maximize_window()

        for keyword in self.keywords:
            print(f"Scraping data for the job role: {keyword}...")

            search = driver.find_element(By.XPATH, '//*[@placeholder="Job Title or Keywords"]')
            search.clear()
            search.send_keys(keyword)
            click = driver.find_element(By.XPATH, '//*[@class="btn blue-teal-sm-btn"]').click()
            time.sleep(5)

            pagenumber = 2

            while pagenumber <= 3:
                jobs = driver.find_elements(By.XPATH, '//*[@class="card banking mt-3"]')
                for job in jobs:
                    self.job_url = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if self.job_url in self.previous_job_urls:
                        continue
                    self.job_title = job.find_element(By.TAG_NAME, 'h5').text
                    if all(word.lower() in self.job_title.lower() for word in keyword.split()):
                        self.job_no += 1
                        job_contract = job.find_element(By.XPATH, './/*[@class="p-secondary"]').text.split(":")[0]
                        self.job_location, self.pay_rate = [data.text for data in job.find_elements(By.XPATH, './/*[@class="p-secondary"]//span')[:2]]

                        if job_contract == 'Contract':
                            list1 = [self.company_name, self.current_date, self.job_title, job_contract, self.pay_rate, self.job_url, self.job_location,
                                     self.job_postdate, self.contact, self.Work_Type]
                            self.npo_jobs[self.job_no] = list1

                next_page = f"{driver.current_url}&q={pagenumber}"
                driver.get(next_page)
                time.sleep(5)
                pagenumber += 1

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

# Example usage:
# if __name__ == "__main__":
#     scraper = CollaberaJobScraper()
#     scraper.scrape_jobs()
#     scraper.generate_csv()
