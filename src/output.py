import os
import json
import requests
import time
import random
import re
from pathlib import Path
from urllib.parse import unquote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Configuration ===
DATA_DIR = Path("data")
SESSION_ENV = DATA_DIR / "session.env"
ENDLINKS_DIR = DATA_DIR / "endlinks"
OUTPUT_DIR = DATA_DIR / "output"
MIN_DELAY = 0.5
MAX_DELAY = 2.5

def load_moodle_session():
    """Load MoodleSession from session.env"""
    with SESSION_ENV.open("r") as f:
        for line in f:
            if line.startswith("MOODLESESSION="):
                return line.strip().split("=", 1)[1]
    raise ValueError("MoodleSession not found in session.env")

def create_session():
    """Create requests session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.cookies.set("MoodleSession", load_moodle_session(), domain="mydy.dypatil.edu")
    return session

def clean_name(name):
    """Clean up resource name: remove common trailing junk & normalize"""
    name = name.lower().strip()

    # Remove common trailing words
    junk_patterns = [
        r"(download)$",
        r"(securedpdf)$",
        r"(presentation)$",
        r"(ppt presentation)$",
        r"(ppt)$",
        r"(copy)$",
        r"( \(\d+\))$"
    ]
    for pat in junk_patterns:
        name = re.sub(pat, "", name).strip()

    # Replace spaces & multiple underscores
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)

    # Remove unsafe chars
    name = re.sub(r"[^a-zA-Z0-9_\-]", "", name)

    return name.strip("_")

def get_filename_from_url(url):
    """Extract filename from URL"""
    return unquote(Path(url).name.split("?")[0])

def download_resource(session, url, save_path):
    """Download a single resource"""
    try:
        response = session.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return False

def select_semester():
    """Prompt user to select a semester"""
    semesters = sorted([d for d in ENDLINKS_DIR.iterdir() if d.is_dir()])
    if not semesters:
        print("No semesters found in endlinks directory.")
        return []
    print("\n📚 Available Semesters:")
    for i, sem in enumerate(semesters, 1):
        print(f"{i}. {sem.name}")
    print("0. Download ALL semesters")
    selection = input("Enter selection (number): ")
    try:
        index = int(selection)
        if index == 0:
            return semesters
        return [semesters[index-1]]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return []

def select_subjects(semester_dir):
    """Prompt user to select subjects"""
    subjects = sorted(f.stem for f in semester_dir.glob("*.json"))
    if not subjects:
        print(f"No subjects found in {semester_dir.name}.")
        return []
    print(f"\n📖 Subjects in {semester_dir.name}:")
    for i, sub in enumerate(subjects, 1):
        print(f"{i}. {sub}")
    print("0. All subjects")
    selection = input("Enter selection (number/comma-separated): ")
    try:
        if selection.strip() == "0":
            return subjects
        indices = [int(s.strip())-1 for s in selection.split(",")]
        return [subjects[i] for i in indices if 0 <= i < len(subjects)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return []

def process_subject(session, semester_dir, subject):
    """Download all resources for a subject"""
    json_file = semester_dir / f"{subject}.json"
    with open(json_file, "r", encoding="utf-8") as f:
        resources = json.load(f)

    output_dir = OUTPUT_DIR / semester_dir.name / subject
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📥 Downloading resources for {subject}:")

    for resource in resources:
        url = resource['url']

        # Figure out file extension
        file_ext = resource.get('filetype')
        if not file_ext:
            url_filename = get_filename_from_url(url)
            if '.' in url_filename:
                file_ext = url_filename.split('.')[-1]
            else:
                file_ext = 'bin'

        safe_name = clean_name(resource['name'])
        # Ensure extension not duplicated
        if not safe_name.lower().endswith(f".{file_ext.lower()}"):
            filename = f"{safe_name}.{file_ext}"
        else:
            filename = safe_name

        save_path = output_dir / filename

        if save_path.exists():
            print(f"✔️ Skipping existing: {filename}")
            continue

        print(f"⬇️  Downloading: {filename}")
        if download_resource(session, url, save_path):
            print(f"✅ Saved: {filename}")
        else:
            print(f"❌ Failed: {filename}")

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"⏳ Waiting {delay:.2f}s...\n")
        time.sleep(delay)

def main():
    session = create_session()
    selected_semesters = select_semester()
    if not selected_semesters:
        return
    for sem_dir in selected_semesters:
        subjects = select_subjects(sem_dir)
        if not subjects:
            continue
        for subject in subjects:
            process_subject(session, sem_dir, subject)

if __name__ == "__main__":
    main()
