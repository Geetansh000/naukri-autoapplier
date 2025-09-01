def initiate_apply(session, job_id, job_data):
    url = "https://www.naukri.com/cloudgateway-workflow/workflow-services/apply-workflow/v1/apply"
    headers = {
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "appid": "121",
        "authorization": "Bearer " + session.cookies.get("nauk_at", ""),
        "clientid": "d3skt0p",
        "content-type": "application/json",
        "origin": "https://www.naukri.com",
        "priority": "u=1, i",
        "referer": f"https://www.naukri.com/job-listings-{job_id}",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "systemid": "jobseeker",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }

    preferred = [
        s["label"]
        for s in job_data.get("jobDetails", {})
        .get("keySkills", {})
        .get("preferred", [])
    ]
    other = [
        s["label"]
        for s in job_data.get("jobDetails", {}).get("keySkills", {}).get("other", [])
    ]
    logstr = job_data.get("jobDetails", {}).get("logStr", "")

    payload = {
        "strJobsarr": [job_id],
        "logstr": logstr,
        "flowtype": "show",
        "crossdomain": True,
        "jquery": 1,
        "rdxMsgId": "",
        "chatBotSDK": True,
        "mandatory_skills": preferred,
        "optional_skills": other,
        "applyTypeId": "107",
        "closebtn": "y",
        "applySrc": "jobsearchDesk",
        "sid": logstr.split("--")[-2] if "--" in logstr else "",
        "mid": "",
    }
    response = session.post(url, headers=headers, json=payload)
    print(f"🔗 Initiating apply for Job ID: {job_id}")
    return response.json()