import requests
import json
from .db import save_external_job
import re
from .config import SKIP_WORDS, MUST_HAVE_WORDS


def fetch_job_details(job_id, headers):
    url = f"https://www.naukri.com/jobapi/v4/job/{job_id}?microsite=y&src=cluster&sid=17513733396487352_2&xp=1&px=1&nignbevent_src=jobsearchDeskGNB"
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200 and response.headers.get(
            "content-type", ""
        ).startswith("application/json"):
            job_data = response.json()
            title = job_data.get('jobDetails', {}).get('title', '')
            print(f"📄 Job Title: {title}")
            print(
                f"🏢 Company: {job_data.get('jobDetails', {}).get('companyDetail', {}).get('name')}"
            )
            print(
                f"📍 Location: {[loc.get('label') for loc in job_data.get('jobDetails', {}).get('locations', [])]}"
            )
            print(
                f"🗘️ Description (short): {job_data.get('jobDetails', {}).get('shortDescription', '')[:100]}..."
            )

            # Skip external apply jobs (microsite or external URL)
            redirect_url = job_data.get("jobDetails", {}).get("applyRedirectUrl", "")
            if redirect_url and not redirect_url.startswith("https://www.naukri.com"):
                save_external_job(
                    {
                        "job_id": job_id,
                        "title": job_data["jobDetails"].get("title"),
                        "company": job_data["jobDetails"]
                        .get("companyDetail", {})
                        .get("name"),
                        "location": [
                            l.get("label")
                            for l in job_data["jobDetails"].get("locations", [])
                        ],
                        "description": job_data["jobDetails"].get(
                            "shortDescription", ""
                        )[:500],
                        "redirect_url": redirect_url,
                    }
                )
                print(f"⛔ Skipping external job with redirect: {redirect_url}")
                return None
            elif job_data.get("jobDetails", {}).get("applyDate", "") and not job_data.get("jobDetails", {}).get("applyDate", "") == "":
                print("⛔ Already applied to this job. Skipping...")
                return None

            skip_keywords = SKIP_WORDS
            must_have_keywords = MUST_HAVE_WORDS
            title_lower = title.lower()

            # ✅ First, check if the title contains any MUST-HAVE keyword
            contains_must_have = any(
                must_word.lower() in title_lower for must_word in must_have_keywords
            )

            # ✅ If the title has a must-have word, do NOT skip, regardless of skip list
            if not contains_must_have:
                for keyword in skip_keywords:
                    if keyword.lower() in title_lower or re.search(r"\bjava\b", title_lower, re.IGNORECASE):
                        # Allow JavaScript jobs (handles javascript, java-script, and java script)
                        if not re.search(r"java[\s-]?script", title_lower, re.IGNORECASE):
                            print(f"⛔ Skipping unwanted job: {title}")
                            return None
                        
            return job_data

        else:
            print(
                f"⚠️ Non-JSON or error response for Job ID {job_id}: {response.status_code}"
            )
            print(response.text[:300])
            return None

    except json.JSONDecodeError:
        print(
            f"❌ JSON decode failed for Job ID {job_id}. Likely empty or invalid JSON."
        )
        print(response.text[:300])
        return None
    except Exception as e:
        print(f"❌ Unexpected error for Job ID {job_id}: {e}")
        return None
