import os
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class TSR_Scraper():
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
        self.company_name = "TSR Consulting"
        self.current_date = date.today().strftime("%d/%m/%Y")
        self.job_Type = "Contract"
        self.pay_rate = "NA"
        self.joburl = "NA"
        self.job_loction = "NA"
        self.job_Posted_Date = "NA"
        self.contact = "(631) 231-0333"
        self.Work_Type = "NA"
        self.jobtitle="NA"
        self.previous_job_urls = set()
        self.load_previous_job_urls()
        self.output_manager = self.OutputManager('output')
        self.keywords = ["Data Analyst", "Business Analyst", "Systems Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]

    def TSR_Scrape(self):
        for user_input in self.keywords:
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://tsrconsulting.com/job-finder/")

            driver.maximize_window()

            filter=driver.find_element(By.XPATH,"//select[@name='matador-types']//option[@value='contract']").click()
            inputfield=driver.find_element(By.XPATH,"//input[@placeholder='Search Jobs']")
            inputfield.send_keys(user_input)
            inputfield.send_keys(Keys.RETURN)

            jobs=driver.find_elements(By.XPATH,"//div[@class='matador-jobs matador-jobs-listing matador-jobs-shortcode']//article")
            # print(len(jobs))

            for job in jobs:
                title=job.find_element(By.TAG_NAME,'h4')
                self.jobtitle=title.text
                # print(jobtitle)
                if all(keyword.lower() in self.jobtitle.lower() for keyword in user_input.split()):

                    self.joburl=title.find_element(By.TAG_NAME,'a').get_attribute("href")
                    if self.joburl in self.previous_job_urls:continue
                    self.job_loction=job.find_element(By.XPATH,".//ul//span[@class='matador-job-meta-value']").text
                    if "Remote" in self.job_loction:
                        self.Work_Type="Remote"
                        self.job_loction=self.job_loction.replace("Remote","")
                    else:
                        self.Work_Type="NA"

                    # print(Work_Type,job_loction)

                    self.list1 = [self.company_name, self.current_date, self.jobtitle, self.job_Type, self.pay_rate, self.joburl, self.job_loction, self.job_Posted_Date,self.contact, self.Work_Type]
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
        self.TSR_Scrape()
        self.generate_csv()

# if __name__=="__main__":
#     tsr_scraper=TSR_Scraper()
#     tsr_scraper.scrape_and_generate_csv()