from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

EMAIL = os.getenv("NAUKRI_EMAIL")
PWD = os.getenv("NAUKRI_PASSWORD")
QUERY = os.getenv("SEARCH_QUERY", "software engineer")
LOC = os.getenv("SEARCH_LOCATION", "Bangalore")
# Name to use in AI prompts (override via .env AUTHOR_NAME)
AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Candidate")
# Accept several common truthy values for headless mode
HEADLESS = os.getenv("RUN_HEADLESS", "False").lower() in ("1", "true", "yes")
# split and drop empty entries
SKIP_WORDS = [word.strip() for word in os.getenv("SKIP_WORDS", "").split(",") if word.strip()]
MUST_HAVE_WORDS = [word.strip() for word in os.getenv("MUST_HAVE_WORDS", "").split(",") if word.strip()]
API_KEY = os.getenv("API_KEY")
DB_PATH = ROOT / "applied_jobs.db"
RESULTS_PER_RUN = 20  # stop after first N jobs each run

PG_SETTINGS = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "database": os.getenv("PG_DB"),
}

print(f"🔍 Searching for: {QUERY}")
EXP = os.getenv("SEARCH_EXP", "2")  # default to 0-2 years experience
SEARCH_URL = f"https://www.naukri.com/{QUERY.replace(' ', '-')}-jobs?experience={EXP}&jobAge=1&glbl_qcrc=1028&ctcFilter=6to10&ctcFilter=10to15"
LOGIN_URL = "https://www.naukri.com/mnjuser/homepage"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")