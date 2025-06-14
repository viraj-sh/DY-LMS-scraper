import json
import random
import time
import re
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Configuration ===
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
MAX_WORKERS = 3

# === Utils ===
def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')

def load_moodle_session():
    for line in SESSION_ENV.read_text().splitlines():
        if line.startswith("MOODLESESSION="):
            return line.split("=", 1)[1]
    raise RuntimeError("MOODLESESSION not found in session.env")

def create_session():
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# === Core Logic ===
def download_document(doc, output_dir, session):
    modtype = doc.get("modtype", "").lower()
    if modtype not in TARGET_MODTYPES:
        return "skipped"

    safe_name = sanitize_filename(doc["shortName"])
    file_path = output_dir / f"{safe_name}.html"

    if file_path.exists():
        return f"exists: {file_path.name}"

    try:
        response = session.get(doc["url"], timeout=10)
        response.raise_for_status()
        file_path.write_text(response.text, encoding="utf-8")
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
        return f"saved: {file_path.name}"
    except Exception as e:
        return f"❌ Failed: {doc['name']} | {e}"

def process_documents():
    parser = argparse.ArgumentParser(description="Fetch LMS document content")
    parser.add_argument("--url", help="Specific document URL to fetch")
    parser.add_argument("--semester", help="Semester short name for organization")
    parser.add_argument("--subject", help="Subject short name for organization")
    args = parser.parse_args()

    cookie_value = load_moodle_session()
    session = create_session()
    session.cookies.set("MoodleSession", cookie_value, domain="mydy.dypatil.edu")

    results = []

    if args.url and args.semester and args.subject:
        # Single document mode
        output_dir = DOCLINKS_DIR / args.semester / args.subject
        output_dir.mkdir(parents=True, exist_ok=True)
        
        doc = {
            "url": args.url,
            "shortName": sanitize_filename(args.url.split("/")[-1]),
            "name": args.subject,
            "modtype": "resource"
        }
        
        result = download_document(doc, output_dir, session)
        print(f"🔍 Single document result: {result}")
    else:
        # Batch processing mode
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
                            continue

                    output_dir = DOCLINKS_DIR / semester_dir.name / subject_file.stem
                    output_dir.mkdir(parents=True, exist_ok=True)

                    for section in sections:
                        for doc in section.get("documents", []):
                            futures.append(
                                executor.submit(download_document, doc, output_dir, session)
                            )

            for future in as_completed(futures):
                results.append(future.result())

        # Batch processing summary
        saved = sum(1 for r in results if r.startswith("saved"))
        skipped = sum(1 for r in results if r.startswith("exists") or r == "skipped")
        failed = [r for r in results if r.startswith("❌")]
        
        print(f"\n📦 Batch complete: {saved} new | {skipped} existing | {len(failed)} failed")
        if failed:
            print("\n❌ Failed downloads:")
            for f in failed:
                print(f)

if __name__ == "__main__":
    try:
        process_documents()
    except Exception as e:
        print(f"💣 Critical error: {str(e)}")