import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing
from .config import PG_SETTINGS

def _conn():
    return psycopg2.connect(
        host=PG_SETTINGS["host"],
        port=PG_SETTINGS["port"],
        user=PG_SETTINGS["user"],
        password=PG_SETTINGS["password"],
        database=PG_SETTINGS["database"],
    )

def init_db():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS applied (
                    job_url TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS external_jobs (
                    job_id TEXT PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    description TEXT,
                    redirect_url TEXT,
                    saved_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            c.commit()

def already_applied(url: str) -> bool:
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT 1 FROM applied WHERE job_url = %s;", (url,))
            return cur.fetchone() is not None

def mark_applied(url: str):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO applied (job_url) VALUES (%s) ON CONFLICT DO NOTHING;",
                (url,)
            )
            c.commit()

def save_external_job(data: dict):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                INSERT INTO external_jobs (job_id, title, company, location, description, redirect_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    location = EXCLUDED.location,
                    description = EXCLUDED.description,
                    redirect_url = EXCLUDED.redirect_url;
            """, (
                data["job_id"],
                data["title"],
                data["company"],
                ", ".join(data["location"]),
                data["description"],
                data["redirect_url"]
            ))
            c.commit()
            print(f"✅ External job saved to DB: {data['job_id']}")
