import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class BeaconHillJobScraper:
    def _init_(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Beacon Hill"
        self.contact = "617.326.4000"
        self.Work_type = "NA"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]

    def create_output_folder(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def create_subfolder_with_date(self, output_folder):
        subfolder_path = os.path.join(output_folder, self.current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def create_csv_file(self, subfolder_path):
        file_name = 'job_portal.csv'
        csv_path = os.path.join(subfolder_path, file_name)
        return csv_path

    def scrape_jobs(self):
        output_folder = self.create_output_folder()
        subfolder_path = self.create_subfolder_with_date(output_folder)
        csv_path = self.create_csv_file(subfolder_path)

        existing_job_urls = set()
        list2=[]

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            existing_job_urls = set(existing_data['Job Posting Url'])

        for value in self.keywords:
            print(f"Scraping data for the job role: {value}...")
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://jobs.beaconhillstaffing.com/job-search/")
            driver.maximize_window()

            wait = WebDriverWait(driver, 20)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')))
            element.click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@data-value="ea862cbfd4ee5a8cff48853fe0fdd701"]').click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@placeholder="Keyword or Job Title"]').send_keys(value)
            time.sleep(5)
            jobs = driver.find_elements(By.XPATH, '//*[@class="row parv_row_parent"]')

            for job in jobs:
                wait = WebDriverWait(driver, 20)
                joburl_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
                joburl = joburl_element.get_attribute('href')

                if joburl in existing_job_urls:
                    continue

                wait = WebDriverWait(driver, 20)
                job_name_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h3')))
                job_name = job_name_element.text

                if all(keyword.lower() in job_name.lower() for keyword in value.split()):
                    self.job_no += 1
                    wait = WebDriverWait(driver, 20)

                    # Explicitly wait for the location, type, pay, and post date elements to be located
                    job_location_element = wait.until(EC.presence_of_element_located((By.XPATH, './/*[@class="col-md-3 location"]//p')))
                    job_type_element = wait.until(EC.presence_of_element_located((By.XPATH, './/*[@class="col-md-3 job_Type type_col"]//p')))
                    job_pay_element = wait.until(EC.presence_of_element_located((By.XPATH, './/*[@class="col-md-3 pay_rate pay_col"]//p')))
                    job_post_date_element = wait.until(EC.presence_of_element_located((By.XPATH, './/*[@class="posted_date_job_search_custom"]')))

                    # Once located, get the text of each element
                    job_location = job_location_element.text
                    job_type = job_type_element.text
                    job_pay = job_pay_element.text
                    job_post_date = job_post_date_element.text
                    if job_name not in list2:
                        list2.append(job_name)
                        list1 = [self.company_name, self.current_date, job_name, job_type, job_pay, joburl, job_location,
                                 job_post_date, self.contact, self.Work_type]
                        self.npo_jobs[self.job_no] = list1
            # Close the browser after scraping data for each keyword
            driver.quit()

        # Append or create CSV file
        npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                             columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                      'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                      'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

        print(npo_jobs_df.head(self.job_no))

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, npo_jobs_df], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            npo_jobs_df.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

# Example usage:
# if _name_ == "_main_":
#     beacon_hill_scraper = BeaconHillJobScraper()
#     beacon_hill_scraper.scrape_jobs()