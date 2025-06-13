import json
import random
import time
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Config ===
DATA_DIR = Path("data")
DOCUMENTS_DIR = DATA_DIR / "documents"
DOCLINKS_DIR = DATA_DIR / "doclinks"
SESSION_ENV = DATA_DIR / "session.env"

TARGET_MODTYPES = {
    "url", "flexpaper", "presentation", "dyquestion", "questionpaper", "resource"
}

MIN_DELAY = 1.2
MAX_DELAY = 3.8
MAX_RETRIES = 3
MAX_WORKERS = 3  # Safe limit to avoid rate-limits

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')

def load_moodle_session():
    for line in SESSION_ENV.read_text().splitlines():
        if line.startswith("MOODLESESSION="):
            return line.split("=", 1)[1]
    raise RuntimeError("MOODLESESSION not found in session.env")

def create_session():
    retry = Retry(total=MAX_RETRIES, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def download_document(doc, output_dir, session):
    modtype = doc.get("modtype", "").lower()
    if modtype not in TARGET_MODTYPES:
        return "skipped"

    safe_name = sanitize_filename(doc["shortName"])
    file_path = output_dir / f"{safe_name}.html"

    if file_path.exists():
        return f"exists: {file_path.name}"

    try:
        print(f"📥 Downloading: {doc['name']} ({modtype})")
        response = session.get(doc["url"], timeout=10)
        response.raise_for_status()
        file_path.write_text(response.text, encoding="utf-8")
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"✅ Saved: {file_path.name} — waiting {delay:.1f}s")
        time.sleep(delay)
        return f"saved: {file_path.name}"
    except Exception as e:
        return f"❌ Failed: {doc['name']} | {e}"

def process_documents():
    cookie_value = load_moodle_session()
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for semester_dir in DOCUMENTS_DIR.iterdir():
            if not semester_dir.is_dir():
                continue
            for subject_file in semester_dir.glob("*.json"):
                with open(subject_file, "r", encoding="utf-8") as f:
                    try:
                        sections = json.load(f)
                    except json.JSONDecodeError:
                        print(f"⚠️ Invalid JSON: {subject_file}")
                        continue

                output_dir = DOCLINKS_DIR / semester_dir.name / subject_file.stem
                output_dir.mkdir(parents=True, exist_ok=True)

                # Each subject file gets its own session to reuse cookies + retry
                session = create_session()
                session.cookies.set("MoodleSession", cookie_value, domain="mydy.dypatil.edu")

                for section in sections:
                    for doc in section.get("documents", []):
                        futures.append(
                            executor.submit(download_document, doc, output_dir, session)
                        )

        for future in as_completed(futures):
            results.append(future.result())

    # === Summary ===
    saved = sum(1 for r in results if r.startswith("saved"))
    skipped = sum(1 for r in results if r.startswith("exists") or r == "skipped")
    failed = [r for r in results if r.startswith("❌")]

    print(f"\n✅ Completed: {saved} downloaded | {skipped} skipped | {len(failed)} failed")
    if failed:
        print("\n❌ Failures:")
        for f in failed:
            print(f)

if __name__ == "__main__":
    process_documents()
