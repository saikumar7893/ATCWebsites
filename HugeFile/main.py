from iodatasphere import IODataSphereScraper
from kfac import KforceJobScraper
from apexsystems import JobScraperApexSystems
from thejudgegroup import JudgeJobScraper
from insightglobal import JobScraperInsightGlobal
from yoh import JobScraperYoh
from Brookesource import BrookSourceJobScraper
from huxley import HuxleyJobScraper
from  beacon import BeaconHillJobScraper
from tricom import JobScraperTricom
from OAKridge import OakridgeStaffingJobScraper
from PDS_Tech import PDSJobScraper
from kore1 import Kore1JobScraper
from Experis import ExperisJobScraper
from Paragon import ParagonITJobScraper
from Vitaver import VitaverStaffingJobScraper
from Collabera import CollaberaJobScraper
from TalentGroups import TalentGroupsJobScraper
from OtterBase import OtterBaseJobScraper
from Palmer import PalmerGroupJobScraper
from fastswitch import FastSwitch_Scraper
from TSR import TSR_Scraper
from LRS import LRS_Scraper
def main():

    try:
        beacon_hill_scraper = BeaconHillJobScraper()
        beacon_hill_scraper.scrape_jobs()
    except Exception:
        print("error in the BeaconHill")

    scraper = JobScraperTricom()
    scraper.scrape_jobs()

    scraper = PDSJobScraper()
    scraper.PDS_scrape_jobs()
    scraper.PDS_generate_csv()

    scraper = OakridgeStaffingJobScraper()
    scraper.scrape_jobs()

    scraper = Kore1JobScraper()
    scraper.scrape_kore1_jobs()
    scraper.generate_kore1_csv()

    scraper = ExperisJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = ParagonITJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = VitaverStaffingJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = CollaberaJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = TalentGroupsJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = OtterBaseJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    scraper = PalmerGroupJobScraper()
    scraper.scrape_jobs()
    scraper.generate_csv()

    fastswitch_scraper=FastSwitch_Scraper()
    fastswitch_scraper.scrape_and_generate_csv()

    tsr_scraper=TSR_Scraper()
    tsr_scraper.scrape_and_generate_csv()

    lrs_scraper = LRS_Scraper()
    lrs_scraper.scrape_and_generate_csv()

    io_datasphere_scraper = IODataSphereScraper(base_folder='.')

    kforce_scraper = KforceJobScraper()
    kforce_scraper.scrape_and_generate_csv()

    apex_systems_scraper = JobScraperApexSystems()
    apex_systems_scraper.scrape_jobs()

    try:

        judge_scraper = JudgeJobScraper()
        judge_scraper.scrape_jobs()
        judge_scraper.generate_csv()

    except Exception:
        print("Exception occuring in JudgeWebsite")

    insight_global_scraper = JobScraperInsightGlobal()
    insight_global_scraper.scrape_jobs()

    yoh_scraper = JobScraperYoh()
    yoh_scraper.scrape_jobs()

    brook_source_scraper = BrookSourceJobScraper()
    brook_source_scraper.scrape_jobs()

    huxley_scraper = HuxleyJobScraper()
    huxley_scraper.scrape_and_generate_csv()



if __name__ == "__main__":
    main()