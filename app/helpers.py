import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .config import HEADLESS, SKIP_WORDS, MUST_HAVE_WORDS
from selenium.webdriver.common.by import By


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


def check_skip_keywords(title: str) -> list[str]:
    return [
        keyword for keyword in SKIP_WORDS
        if re.search(rf'(?<!\w){re.escape(keyword)}(?!\w)', title, re.IGNORECASE)
    ]


def check_must_have_keywords(title: str) -> list[str]:
    return [
        word for word in MUST_HAVE_WORDS
        if re.search(rf'\b{re.escape(word)}\b', title, re.IGNORECASE)
    ]


def find_elements_by_css(driver, selector):
    try:
        return driver.find_elements(By.CSS_SELECTOR, selector)
    except Exception as e:
        print(f"❌ Could not find elements with selector '{selector}': {e}")
        return []
