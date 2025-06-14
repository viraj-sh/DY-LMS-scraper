import requests
import json
import logging
import re
import time
import random
import argparse
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Configuration ===
DATA_DIR = Path("data")
SESSION_ENV_FILE = DATA_DIR / "session.env"
DASHBOARD_JSON = DATA_DIR / "dashboard.json"
SUBJECTS_DIR = DATA_DIR / "subjects"
MAX_WORKERS = 5  # Use a slightly lower number to reduce server load
MIN_DELAY = 0.5  # Minimum delay in seconds
MAX_DELAY = 1.5  # Maximum delay in seconds

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def create_retry_session():
    """Create session with retry strategy"""
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def load_moodle_session():
    """Read MoodleSession from session.env"""
    try:
        for line in SESSION_ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("MOODLESESSION="):
                return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        raise RuntimeError(f"Session file not found: {SESSION_ENV_FILE}")
    raise RuntimeError(f"MOODLESESSION not found in {SESSION_ENV_FILE}")

def sanitize_filename(name: str) -> str:
    """Clean filenames for safe filesystem use"""
    return re.sub(r'[^\w\-_.]', '_', name.strip())

def download_subject_html(session, url: str, save_path: Path):
    """Download and save subject HTML, then delay"""
    response = session.get(url)
    response.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(response.text, encoding="utf-8")
    logging.info(f"[✓] Saved: {save_path}")

    # Random delay to be polite
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)

def process_subjects():
    """Main processing function with concurrency + polite delay + filtering"""
    parser = argparse.ArgumentParser(description='Fetch LMS subject data')
    parser.add_argument('--semester', help='Short name of semester to fetch')
    parser.add_argument('--subject', help='Specific subject URL to fetch')
    args = parser.parse_args()

    session = create_retry_session()
    moodle_session = load_moodle_session()
    session.cookies.set("MoodleSession", moodle_session, domain="mydy.dypatil.edu")

    semesters = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for semester in semesters:
            # If filtering for a specific semester, skip others
            if args.semester and semester["shortName"] != args.semester:
                continue

            sem_dir = SUBJECTS_DIR / sanitize_filename(semester["shortName"])
            for subject in semester["subjects"]:
                # If filtering for a specific subject URL, skip others
                if args.subject and subject["url"] != args.subject:
                    continue

                filename = f"{sanitize_filename(subject['shortName'])}.html"
                save_path = sem_dir / filename

                if save_path.exists():
                    logging.info(f"[=] Skipping existing: {save_path}")
                    continue

                logging.info(f"[→] Queued: {subject['name']}")
                tasks.append(executor.submit(
                    download_subject_html,
                    session,
                    subject["url"],
                    save_path
                ))

        # Wait for all tasks to complete
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logging.error(f"[!] Error: {str(e)}")

if __name__ == "__main__":
    try:
        process_subjects()
        logging.info("✅ All subjects processed successfully.")
    except Exception:
        logging.exception("❌ Fatal error during processing.")