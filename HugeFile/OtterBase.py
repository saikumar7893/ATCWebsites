import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class OtterBaseJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Otter_Base"
        self.contact = "800.358.2098"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.work_type = "NA"
        self.job_Type = "NA"
        self.job_pay = "NA"
        self.job_postdate="NA"
        self.output_folder = "output"
        self.job_url="NA"
        self.job_location="NA"
        self.job_date="NA"
        self.job_title="NA"
    #     self.previous_job_urls = set()
    #     self.load_previous_job_urls()
    #
    # def load_previous_job_urls(self):
    #     output_folder = os.path.join(os.getcwd(), 'output')
    #     for root, dirs, files in os.walk(output_folder):
    #         for file in files:
    #             if file.endswith('.csv'):
    #                 df = pd.read_csv(os.path.join(root, file))
    #                 self.previous_job_urls.update(df['Job Posting Url'].tolist())


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
        driver.get("https://jobs.otterbase.com/")
        driver.maximize_window()
        time.sleep(3)
        print("Currently searching on OTTERBASE")

        while True:
            try:
                load_more = driver.find_element(By.XPATH, '//*[@class="facetwp-load-more"]')
                load_more.click()
                time.sleep(5)
            except Exception:
                break

        jobs = driver.find_elements(By.XPATH, '//*[contains(@class, "job_listing") and contains(@class, "type-job_listing")]')
        for job in jobs:
            job_title = job.find_element(By.XPATH, './/*[@class="position"]//h3').text

            for value in ["Data Analyst", "Business Analyst", "Systems Analyst", "Data Scientist", "Data Engineer", "Business System Analyst"]:
                if all(keyword.lower() in job_title.lower() for keyword in value.split()):
                    if job_title not in self.npo_jobs:
                        self.job_no += 1
                        job_url = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        # if job_url in self.previous_job_urls:
                        #     continue
                        job_location = job.find_element(By.XPATH, './/*[@class="location"]').text
                        job_date = job.find_element(By.XPATH, './/*[@class="date-posted"]').text

                        list1 = [self.company_name, self.current_date, job_title, self.work_type, self.job_pay, job_url, job_location, job_date, self.contact, self.work_type]
                        self.npo_jobs[job_title] = list1

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
#     scraper = OtterBaseJobScraper()
#     scraper.scrape_jobs()
#     scraper.generate_csv()
