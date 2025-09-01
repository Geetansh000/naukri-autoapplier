from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .config import HEADLESS


def get_requests_session_from_selenium(driver):
    cookies = driver.get_cookies()
    cookie_str = "; ".join(
        [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
    )
    return cookie_str


def extract_job_id(job_url: str):
    return job_url.split("-")[-1]


def _driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    return webdriver.Chrome(options=opts)
