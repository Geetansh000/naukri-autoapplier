from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .config import SEARCH_URL
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .db import already_applied, mark_applied
from .apply import apply_to_job
from .apply_web import apply_web

def apply_once(driver, str1, PAGE=1):
    url = SEARCH_URL.replace("?", str1)
    print("🔎 Navigating to job search page...", url)
    driver.get(url)

    print("⏳ Waiting 20 seconds for manual inspection...")
    time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cust-job-tuple"))
        )

        jobs = driver.find_elements(By.CLASS_NAME, "cust-job-tuple")
        print(f"✅ Found {len(jobs)} job cards.")

        # ✅ Extract job links before page navigation
        job_links = []
        for job in jobs:
            try:
                link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                if link:
                    job_links.append(link)
            except Exception as e:
                print(f"⚠️ Could not extract link: {e}")

        for link in job_links:
            try:
                if already_applied(link):
                    print(f"🔁 Already applied: {link}")
                    continue
                if(apply_web(driver, link)):
                    print(f"✅ Applied to job: {link}")
                    mark_applied(link)
                    continue
                apply_to_job(driver, link)
            except Exception as e:
                print(f"⚠️ Error while applying to job: {e}")
        print("✅ All jobs processed.")
        print("🔄 Restarting search for new jobs...")
        print(f"🔄 Next page: {PAGE + 1}")
        PAGE += 1
        str1 = f"-{PAGE}?"
        apply_once(driver, str1, PAGE)

    except Exception as e:
        print("🔴 Could not find job listings.")
        print(e)

