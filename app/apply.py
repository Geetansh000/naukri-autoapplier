from .fetch_job_details import fetch_job_details
from .auto_apply import auto_answer_questions, make_final_apply
from .helpers import get_requests_session_from_selenium, extract_job_id
from selenium.webdriver.common.by import By
import time
import json
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .initiate_apply import initiate_apply


def apply_to_job(driver, job_url):
    job_id = extract_job_id(job_url)
    print(f"\n🚀 Applying to Job ID: {job_id}")
    driver.get(job_url)
    time.sleep(2)

    # Prepare session and headers
    cookie_str = get_requests_session_from_selenium(driver)
    session = requests.Session()
    for part in cookie_str.split("; "):
        if "=" in part:
            name, value = part.split("=", 1)
            session.cookies.set(name, value)

    auth_token = session.cookies.get("nauk_at", "")
    headers = {
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "appid": "121",
        "authorization": f"Bearer {auth_token}",
        "clientid": "d3skt0p",
        "content-type": "application/json",
        "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
        "nkparam": "",
        "priority": "u=1, i",
        "referer": job_url,
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "systemid": "Naukri",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
    }

    # Fetch job data
    job_data = fetch_job_details(job_id, headers)
    if not job_data:
        print(f"❌ Could not fetch job details for {job_id}. Skipping...")
        return
    # Initiate apply to get questions
    apply_info = initiate_apply(session, job_id, job_data)
    if apply_info.get("statusCode") != 0:
        print("❌ Could not initiate apply.")
        return

    questions = apply_info["jobs"][0].get("questionnaire", [])
    if not questions:
        print("ℹ️ No questions found. Proceeding to final step.")
    else:
        print(
            f"📋 Found {len(questions)} questions to answer.",
            json.dumps(questions, indent=2),
        )
        app_name = f"{job_id}_apply"
        print("🤖 Starting auto-answering bot flow...")
        ques = auto_answer_questions(app_name, auth_token, cookie_str, questions)
        print("✅ Bot flow complete. Answers:", ques)
        # Make final apply call
        print("🚀 Making final apply call...")
        make_final_apply(
            driver,
            auth_token,
            job_id,
            job_data,
            ques,
        )

    # Final apply redirect
    final_url = apply_info.get("applyRedirectUrl")
    if final_url:
        print(f"🔗 Final Apply URL: {final_url}")
        driver.get(final_url)
        time.sleep(2)
        print("✅ Application submitted successfully.")
        return

    # Fallback: try to click apply button manually
    print("⚠️ No final redirect URL. Trying to click Apply button manually...")
    try:
        apply_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "apply-button"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_btn)
        apply_btn.click()
        print("🖱️ Clicked Apply button manually.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to click Apply button: {e}")
