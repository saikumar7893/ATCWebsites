import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class TalentGroupsJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Talent_groups"
        self.contact = "617.326.4000"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.work_type = "NA"
        self.job_pay = "NA"
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
        driver.get("https://www.talentgroups.com/jobs#/")
        driver.maximize_window()
        time.sleep(10)

        for keyword in ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientist", "Data Engineer", "Business System Analyst"]:
            print(f"Scraping data for the job role: {keyword}...")

            enter_job = driver.find_element(By.XPATH, '//*[@placeholder="Job, Title, Skills, etc"]')
            enter_job.clear()
            enter_job.send_keys(keyword)
            time.sleep(15)

            list2 = []
            page_number = 0

            while True:
                jobs = driver.find_elements(By.XPATH, '//*[@class="shmJobResultStd shmJobResultundefined"]')
                flag = 0

                for job in jobs:
                    job_title = job.find_element(By.XPATH, './/*[@class="shmJobtitle"]//a').text

                    if keyword.lower() in job_title.lower():
                        try:
                            job_location = job.find_element(By.XPATH, './/*[@class="shmLocation"]').text
                        except Exception:
                            job_location = 'NA'

                        if [job_title, job_location] in list2:
                            flag += 1
                            if flag >= 3:
                                break

                        self.job_no += 1
                        job_url = job.find_element(By.XPATH, './/*[@class="shmJobtitle"]//a').get_attribute('href')
                        if job_url in self.previous_job_urls:
                            continue
                        job_type = job.find_element(By.XPATH, './/*[@class="work-type"]').text
                        job_post_date = job.find_element(By.XPATH, '//*[@class="shmJobDetails"]//div[@class="shmJobDateCreated"]').text
                        work_type = job.find_element(By.XPATH, './/*[@class="work-model"]').text

                        list3 = [job_title, job_location]
                        list2.append(list3)

                        if job_type == 'Contract':
                            list1 = [self.company_name, self.current_date, job_title, job_type, self.job_pay, job_url, job_location, job_post_date, self.contact, work_type]
                            self.npo_jobs[self.job_no] = list1

                page_number += 1
                if flag >= 3:
                    break

                try:
                    next_page = job.find_element(By.XPATH, '//*[text()=">>"]')
                    if page_number == 4:
                        raise ValueError("Page number is 3")
                    next_page.click()
                    time.sleep(20)
                except Exception:
                    break

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
#     scraper = TalentGroupsJobScraper()
#     scraper.scrape_jobs()
#     scraper.generate_csv()
