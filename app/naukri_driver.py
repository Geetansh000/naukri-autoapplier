from .config import SEARCH_URL
from .db import init_db
from rich import print
import time
import requests
from .login import login
from .helpers import _driver
from .getjobs import apply_once


def run():
    init_db()
    driver = _driver()
    try:
        login(driver)
        print("📍 Navigating to search after login redirect...")
        driver.get(SEARCH_URL)
        time.sleep(2)
        apply_once(driver, "?", 1)
    finally:
        driver.quit()


# def answer_question(session, job_id, question_id, answer, current_node):
#     url = (
#         "https://www.naukri.com/cloudgateway-chatbot/chatbot-services/botapi/v5/respond"
#     )
#     payload = {
#         "editResponse": answer,
#         "editResponseType": "1",
#         "currentNode": current_node,
#         "applyData": {job_id: {"answers": {question_id: [answer]}}},
#         "currentConversationName": f"{job_id}_apply",
#     }
#     headers = {
#         "Content-Type": "application/json",
#         "Referer": f"https://www.naukri.com/job-listings-{job_id}",
#     }
#     response = session.post(url, headers=headers, json=payload)
#     return response.json()


def get_similar_jobs(job_id, headers):
    url = f"https://www.naukri.com/jobapi/v2/search/simjobs/{job_id}?noOfResults=6&searchType=sim"
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get("simJobDetails", {}).get("content", [])
    print(f"❌ Failed to fetch similar jobs for {job_id}")
    return []
