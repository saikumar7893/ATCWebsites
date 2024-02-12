from bs4 import BeautifulSoup
from datetime import date
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

class IODataSphereScraper:
    def __init__(self, base_folder):
        self.company_name = "IO Datasphere, Inc. 2016"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.keywords = ["Data Analyst", "Business Analyst", "Systems Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.base_folder = base_folder
        self.output_folder = os.path.join(base_folder, "output")
        self.previous_job_urls = set()
        self.npo_jobs = {}
        self.job_no = 0

        self.load_previous_job_urls()
        self.scrape_data()
        self.generate_csv()

    def create_output_folder(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def create_date_subfolder(self):
        today_date = date.today().strftime("%Y-%m-%d")
        date_folder = os.path.join(self.output_folder, today_date)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        return date_folder

    def create_csv_file(self, subfolder, filename, data_frame):
        file_path = os.path.join(subfolder, f'{filename}.csv')
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            updated_data = pd.concat([existing_data, data_frame], ignore_index=True)
            updated_data.to_csv(file_path, index=False)
            print(f"Appended data to existing CSV: {file_path}")
        else:
            data_frame.to_csv(file_path, index=False)
            print(f"Created new CSV: {file_path}")

    def load_previous_job_urls(self):
        for root, _, files in os.walk(self.output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())

    def scrape_data(self):
        print("Scraping the data...")

        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        url = "https://www.iodatasphere.com/jobs.php"
        response = requests.get(url)
        data = response.text

        soup = BeautifulSoup(data, 'html.parser')

        Jobs = soup.find_all('div', {'class': 'container-fluid text-center'})

        for Job in Jobs:
            links = Job.find_all('a', {'class': 'jobLink'})
            for i in range(0, len(links), 3):
                job_url = "https://www.iodatasphere.com/" + links[i].get('href')
                if job_url != "https://www.iodatasphere.com/apply.php?jobID= " and job_url not in self.previous_job_urls:
                    self.job_no += 1
                    driver.get(job_url)
                    job_title = driver.find_element(By.XPATH, '(//table[@class="table"]//tbody//tr//td)[2]').text
                    job_location = driver.find_element(By.XPATH, '(//table[@class="table"]//tbody//tr//td)[8]').text

                    try:
                        work_type = driver.find_element(By.XPATH, '//div[@class="container-fluid"]//p//b')
                        if "hybrid" in work_type.text.lower():
                            work_type = "Hybrid"
                        elif "onsite" in work_type.text.lower() or "on-site" in work_type.text.lower():
                            work_type = "Onsite"
                        elif "remote" in work_type.text.lower():
                            work_type = "Remote"
                        else:
                            work_type = "NA"
                    except Exception:
                        work_type = "NA"

                    for user_input in self.keywords:
                        if all(keyword.lower() in job_title.lower() for keyword in user_input.split()):
                            job_data = [self.company_name, self.current_date, job_title, "NA", "NA", job_url, job_location, "NA", "630.520.0260", work_type]
                            self.npo_jobs[self.job_no] = job_data
                            break

        driver.quit()

    def generate_csv(self):
        self.create_output_folder()

        if self.job_no == 0:
            print("No new jobs available since the last run.")
        else:
            print("Generating CSV file")
            npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                                 columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                          'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                          'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])
            print(npo_jobs_df.head(self.job_no))

            date_subfolder = self.create_date_subfolder()
            file_name = 'job_portal'
            self.create_csv_file(date_subfolder, file_name, npo_jobs_df)
            print(f"CSV file '{file_name}' has been generated.")

# if __name__ == "__main__":
#     io_datasphere_scraper = IODataSphereScraper(base_folder='.')
