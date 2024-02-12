import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.chrome.options import Options
import pandas as pd

class LRS_Scraper():
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
        self.previous_job_urls = set()
        self.load_previous_job_urls()
        self.output_manager = self.OutputManager('output')
        self.company_name = "LRSConsultingServices"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "Contract"
        self.contact = "https://www.lrs.com/contact/"
        self.Work_Type = "NA"
        self.pay_rate="NA"
        self.job_postdate="NA"
        self.joburl="NA"
        self.jobtitle="NA"
        self.joblocation="NA"
        self.keywords = ["Data Analyst", "Business Analyst", "Systems Analyst", "Data Scientist", "Data engineer", "Business System Analyst"]
    def LRS_Scrape(self):
        for user_input in self.keywords:
            chrome_options=Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver=webdriver.Chrome(options=chrome_options)
            time.sleep(3)
            driver.get("https://jobs.lrsconsultingservices.com/")
            driver.maximize_window()
            search=driver.find_element(By.XPATH,"//*//input[@placeholder='Keyword Search']")
            search.send_keys(user_input)
            search.send_keys(Keys.RETURN)

            try:
                checkbox = driver.find_element(By.XPATH, "//*[@id='Contract']").click()
            except Exception:
                continue
            jobs=driver.find_elements(By.XPATH,"//div[@class='card-wrapper']//a")
            # print(len(jobs))
            for job in jobs:

                self.jobtitle=job.find_element(By.XPATH,".//span[@class='card-title-category']").text
                if all(keyword.lower() in self.jobtitle.lower() for keyword in user_input.split()):
                    self.joburl=job.get_attribute("href")
                    if self.joburl in self.previous_job_urls:
                        continue
                    self.job_postdate=job.find_element(By.XPATH,".//span[@class='card-date']").text
                    self.job_postdate=self.job_postdate.replace("Added ","")
                    self.joblocation=job.find_element(By.XPATH,".//span[@class='card-location']").text

                    self.list1 = [self.company_name, self.current_date, self.jobtitle, self.job_Type, self.pay_rate, self.joburl, self.joblocation, self.job_postdate,self.contact, self.Work_Type]
                    flag=1
                    for i in self.npo_jobs:
                        if self.npo_jobs[i]==self.list1:flag=0
                    if flag==1:
                        self.job_no +=1
                        self.npo_jobs[self.job_no] = self.list1

            driver.quit()
    def load_previous_job_urls(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file))
                    self.previous_job_urls.update(df['Job Posting Url'].tolist())
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

    def scrape_and_generate_csv(self):
        self.LRS_Scrape()
        self.generate_csv()
#
# if __name__ == "__main__":
#     lrs_scraper = LRS_Scraper()
#     lrs_scraper.scrape_and_generate_csv()