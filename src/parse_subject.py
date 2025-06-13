import json
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# === Config ===
DATA_DIR = Path("data")
SUBJECTS_DIR = DATA_DIR / "subjects"
DOCUMENTS_DIR = DATA_DIR / "documents"
MAX_WORKERS = 5

# === Logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# === Utils ===
sanitize_name = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())

# === Extract logic ===

def extract_documents(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    course_content = soup.find("div", class_="course-content")
    if not course_content:
        logging.warning(f"No course content in {html_path}")
        return []

    sections = []
    section_no = 0

    # General section
    general_section = course_content.find("li", id="section-0")
    if general_section:
        section_no += 1
        sections.append(process_section(general_section, section_no))

    # Other sections
    for section in course_content.find_all("li", class_="section main clearfix"):
        section_no += 1
        sections.append(process_section(section, section_no))

    return sections

def process_section(section, section_no):
    title_tag = section.find("h3", class_="section-title")
    section_name = title_tag.get_text(strip=True) if title_tag else f"Week {section_no}"

    documents = []
    for idx, activity in enumerate(section.find_all("li", class_="activity"), 1):
        a_tag = activity.find("a")
        if not a_tag:
            continue

        # Detect modtype
        modtype = next(
            (cls.replace("modtype_", "") for cls in activity.get("class", []) if cls.startswith("modtype_")),
            "unknown"
        )

        instancename = a_tag.find("span", class_="instancename")
        name = instancename.get_text(strip=True) if instancename else f"Document {idx}"

        documents.append({
            "no": idx,
            "name": name,
            "shortName": sanitize_name(name),
            "url": a_tag.get("href", ""),
            "modtype": modtype
        })

    return {
        "no": section_no,
        "name": section_name,
        "shortName": sanitize_name(section_name),
        "documents": documents
    }

# === Worker ===

def process_subject(html_path):
    semester_short = html_path.parent.name
    subject_short = html_path.stem
    output_dir = DOCUMENTS_DIR / semester_short
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{subject_short}.json"

    sections = extract_documents(html_path)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

    logging.info(f"[✓] Saved: {output_file}")

# === Main ===

def main():
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for semester_dir in SUBJECTS_DIR.iterdir():
            if semester_dir.is_dir():
                for html_file in semester_dir.glob("*.html"):
                    tasks.append(executor.submit(process_subject, html_file))
    logging.info("✅ All subjects processed")

if __name__ == "__main__":
    main()
