from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re

def extract_id_from_href(href):
    parsed_url = urlparse(href)
    query = parse_qs(parsed_url.query)
    # Ensure link matches actual course pattern
    if "/course/view.php" in parsed_url.path and 'id' in query:
        return query['id'][0]
    return None

def is_semester_title(title):
    return re.fullmatch(r"Semester\s+[IVX0-9]+", title, flags=re.IGNORECASE) is not None

def parse_semesters_and_subjects(html: str):
    soup = BeautifulSoup(html, "html.parser")
    semesters = []

    # Only process semester blocks that have a proper semester name
    for li in soup.find_all("li", class_="type_course"):
        span = li.find("span", class_="usdimmed_text")
        if not span:
            continue
        semester_name = span.get_text(strip=True)
        if not is_semester_title(semester_name):
            continue  # skip non-semesters

        # Get the <ul> of subjects
        p_tag = span.find_parent("p")
        ul_tag = None
        if p_tag:
            ul_tag = p_tag.find_next_sibling("ul")
        if not ul_tag:
            ul_tag = li.find("ul")  # fallback

        if not ul_tag:
            continue

        subjects = []
        for subject_li in ul_tag.find_all("li", recursive=False):
            a_tag = subject_li.find("a", href=True)
            if a_tag:
                subject_id = extract_id_from_href(a_tag["href"])
                if subject_id:
                    subjects.append({
                        "name": a_tag.get_text(strip=True),
                        "id": subject_id
                    })

        if subjects:
            semesters.append({
                "semester": semester_name,
                "subjects": subjects
            })

    return semesters


