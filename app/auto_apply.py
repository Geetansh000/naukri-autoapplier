import time
import requests
import json
from .infer import infer_answer
from .helpers import get_requests_session_from_selenium


def auto_answer_questions(app_name: str, auth_token: str, session_cookie: str, questions: list):
    """
    Auto-answers Naukri chatbot questions based on infer_answer() logic.
    """
    print(f"🤖 Starting auto-answer for {app_name}...")

    url = "https://www.naukri.com/cloudgateway-chatbot/chatbot-services/botapi/v5/respond"
    job_id = app_name.split("_")[0]

    # Set common headers
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}",
        "content-type": "application/json",
        "origin": "https://www.naukri.com",
        "referer": f"https://www.naukri.com/job-listings-{job_id}",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }

    # Parse cookies safely
    cookies = dict(
        c.split("=", 1) for c in session_cookie.split("; ") if "=" in c
    )

    # Helper to build payload
    def build_payload(ans: str):
        return {
            "input": {"text": [ans], "id": ["-1"]},
            "appName": app_name,
            "domain": "Naukri",
            "conversation": app_name,
            "channel": "web",
            "status": "Fresh",
            "utmSource": "",
            "utmContent": "",
            "deviceType": "WEB",
        }

    question_ids = {}
    session = requests.Session()

    # Get first question
    if not questions:
        print("⚠️ No questions provided. Exiting.")
        return {}

    first_q = questions[0]
    opts = list(first_q.get("answerOption", {}).values()
                ) if first_q.get("answerOption") else None
    answer = infer_answer(first_q["questionName"], opts)

    question_ids[first_q["questionId"]] = [answer] if opts else answer
    payload = build_payload(answer)
    print(f"✍️ Q{first_q['questionId']}: {first_q['questionName']} → {answer}")

    i = 1
    retries = 0
    MAX_RETRIES = 10  # Prevent infinite loops

    while retries < MAX_RETRIES:
        try:
            res = session.post(url, headers=headers,
                               cookies=cookies, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            break

        # Check bot response
        if not data.get("speechResponse"):
            print("✅ No more questions from the bot.")
            break

        speech = data["speechResponse"][0]["response"]
        print(f"🧠 Bot asks: {speech}")

        # Final acknowledgement check
        if data.get("isLeafNode") and "thank" in speech.lower():
            # Answer skipped questions if any
            if len(question_ids) < len(questions):
                for q in questions:
                    if q["questionId"] not in question_ids:
                        opts = list(q.get("answerOption", {}).values()) if q.get(
                            "answerOption") else None
                        answer = infer_answer(q["questionName"], opts)
                        question_ids[q["questionId"]] = [
                            answer] if opts else answer
                        print(
                            f"✍️ Skipped Q{q['questionId']}: {q['questionName']} → {answer}")
                        payload = build_payload(answer)
            print("✅ Final response acknowledged. Exiting.")
            break

        # Extract options for current question if available
        opts = [opt["value"] for opt in data.get(
            "options", [])] if data.get("options") else None
        answer = infer_answer(speech, opts)

        # Use fallback question ID if missing
        qid = questions[i]["questionId"] if i < len(questions) else f"q_{i}"
        question_ids[qid] = [answer] if opts else answer
        print(f"✍️ Q{qid}: {speech} → {answer}")

        payload = build_payload(answer)
        i += 1
        retries += 1
        time.sleep(1)  # Prevent bot flood detection

    print("✅ Bot flow complete.")
    return question_ids


def answer_questions(
    app_name: str, auth_token: str, session_cookie: str, questions: list
):
    print(f"🤖 Auto-answering questions for {app_name}...")
    url = (
        "https://www.naukri.com/cloudgateway-chatbot/chatbot-services/botapi/v5/respond"
    )
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}",
        "content-type": "application/json",
        "origin": "https://www.naukri.com",
        "referer": f"https://www.naukri.com/job-listings-{app_name.split('_')[0]}",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }
    cookies = {
        name.strip(): value.strip()
        for name, value in [
            c.split("=", 1) for c in session_cookie.split("; ") if "=" in c
        ]
    }

    session = requests.Session()
    current_node = 0
    apply_answers = {}

    for q in questions:
        qid = q["questionId"]
        qname = q["questionName"]
        opts = list(q["answerOption"].values()) if q.get(
            "answerOption") else None
        answer = infer_answer(qname, opts)

        print(f"✍️ Q{qid}: {qname} → {answer}")
        payload = {
            "editResponse": answer,
            "editResponseType": "1",
            "currentNode": current_node,
            "applyData": {
                app_name.split("_")[0]: {"answers": {
                    qid: [answer] if opts else answer}}
            },
            "currentConversationName": app_name,
        }

        res = session.post(url, headers=headers, cookies=cookies, json=payload)
        print(f"🤖 Sent answer, response: {res.status_code}")
        apply_answers[qid] = [answer] if opts else answer
        time.sleep(1.5)
        current_node += 1

    print("✅ Bot flow complete. Now sending final apply payload...")

    final_url = "https://www.naukri.com/cloudgateway-workflow/workflow-services/apply-workflow/v1/apply"
    job_id = app_name.split("_")[0]
    payload = {
        "strJobsarr": [job_id],
        "logstr": "----F-0-1---",
        "flowtype": "show",
        "crossdomain": True,
        "jquery": 1,
        "rdxMsgId": "",
        "chatBotSDK": True,
        "mandatory_skills": [],
        "optional_skills": [],
        "applyTypeId": "107",
        "closebtn": "y",
        "applySrc": "----F-0-1---",
        "sid": "",
        "mid": "",
        "applyData": {
            job_id: {
                "answers": {
                    qid: val if isinstance(val, list) else [val]
                    for qid, val in apply_answers.items()
                }
            }
        },
        "qupData": {},
    }

    final_res = session.post(final_url, headers=headers,
                             cookies=cookies, json=payload)
    print("🚀 Final apply call response:",
          final_res.status_code, final_res.text[:300])


def make_final_apply(
    driver,
    auth_token: str,
    job_id,
    job_data,
    question_answers: dict,
):
    logstr = job_data.get("jobDetails", {}).get("logStr", "----F-0-1---")
    preferred_skills = [
        s.get("label")
        for s in job_data.get("jobDetails", {})
        .get("keySkills", {})
        .get("preferred", [])
        if s.get("label")
    ]
    optional_skills = [
        s.get("label")
        for s in job_data.get("jobDetails", {}).get("keySkills", {}).get("other", [])
        if s.get("label")
    ]

    # Ensure all answers are in correct format: string or list
    formatted_answers = {qid: val for qid, val in question_answers.items()}

    payload = {
        "strJobsarr": [job_id],
        "logstr": "----F-0-1---",  # logstr,
        "flowtype": "show",
        "crossdomain": True,
        "jquery": 1,
        "rdxMsgId": "",
        "chatBotSDK": True,
        "mandatory_skills": preferred_skills,
        "optional_skills": optional_skills,
        "applyTypeId": "107",
        "closebtn": "y",
        "applySrc": "----F-0-1---",  # logstr,
        "sid": "",
        "mid": "",
        "applyData": {job_id: {"answers": formatted_answers}},
        "qupData": {},
    }

    headers = {
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "appid": "121",
        "authorization": f"Bearer {auth_token}",
        "clientid": "d3skt0p",
        "content-type": "application/json",
        "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
        "Cookie": get_requests_session_from_selenium(driver),
    }

    url = "https://www.naukri.com/cloudgateway-workflow/workflow-services/apply-workflow/v1/apply"
    print(
        f"📤 Sending final apply request for Job ID: {job_id}", json.dumps(payload))
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if data.get("jobs") and data["jobs"][0].get("validationError"):
        print(
            f"⚠️ Validation errors for Job ID {data["jobs"][0].get("validationError")}:"
        )
        raise Exception(data["jobs"][0].get("validationError"))

    print(f"🚀 Final apply response: {json.dumps(data.get("jobs"), indent=2)}")

    if response.ok:
        print("✅ Final apply successful.")
        return response.json()

    print(
        f"❌ Failed to make final apply for {job_id}. Status: {response.status_code}")
    print(response.text[:300])
    return None
