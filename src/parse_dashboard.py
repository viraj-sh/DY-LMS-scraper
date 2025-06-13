import json
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup

# === Configuration ===
DATA_DIR = Path("data")
DASHBOARD_HTML_FILE = DATA_DIR / "dashboard.html"
OUTPUT_JSON_FILE = DATA_DIR / "dashboard.json"

# === Logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# === Helpers ===
def to_safe_name(text: str) -> str:
    """Convert text to a safe lowercase name with only letters/numbers."""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def extract_semesters(soup: BeautifulSoup) -> list:
    """Extract semesters and subjects from the dashboard soup."""
    # Find the block with previous semester classes
    semester_block = soup.find("div", {"class": "block_stu_previousclasses"})

    if not semester_block:
        logging.warning("Semester block not found in HTML. Check if the block ID has changed.")
        return []

    semesters = []
    semester_lis = semester_block.select("li.type_course")

    logging.info(f"Found {len(semester_lis)} semester blocks.")

    for sem_idx, sem_li in enumerate(semester_lis, start=1):
        semester_name = sem_li.find("span", class_="usdimmed_text")
        semester_name = semester_name.get_text(strip=True) if semester_name else f"Semester {sem_idx}"
        semester_safe = to_safe_name(semester_name)

        subjects = []
        subject_lis = sem_li.find_all("li")

        for subj_idx, subj_li in enumerate(subject_lis, start=1):
            a_tag = subj_li.find("a")
            if not a_tag or not a_tag.has_attr("href"):
                continue

            subj_name = a_tag.get_text(strip=True)
            subj_safe = to_safe_name(subj_name)
            subj_url = a_tag["href"]

            subjects.append({
                "no": subj_idx,
                "name": subj_name,
                "shortName": subj_safe,
                "url": subj_url
            })

        semesters.append({
            "no": sem_idx,
            "name": semester_name,
            "shortName": semester_safe,
            "subjects": subjects
        })

    return semesters

def main():
    if not DASHBOARD_HTML_FILE.exists():
        logging.error(f"Dashboard HTML file not found at {DASHBOARD_HTML_FILE}")
        return

    logging.info(f"Parsing {DASHBOARD_HTML_FILE} ...")
    soup = BeautifulSoup(DASHBOARD_HTML_FILE.read_text(encoding="utf-8"), "lxml")

    semesters = extract_semesters(soup)

    OUTPUT_JSON_FILE.write_text(json.dumps(semesters, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info(f"Extracted {len(semesters)} semesters → saved to {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    main()
