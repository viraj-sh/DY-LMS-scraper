import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

CLASS_PAGE_URL = "https://mydy.dypatil.edu/rait/course/customview.php?id={class_id}"

def extract_resource_id(href):
    parsed = urlparse(href)
    if "/mod/" in parsed.path and "/view.php" in parsed.path:
        qs = parse_qs(parsed.query)
        if "id" in qs:
            return qs["id"][0]
    return None

def extract_module_type(href):
    # Extract the module type between /mod/ and /view.php in the URL path
    parsed = urlparse(href)
    path_parts = parsed.path.split('/')
    try:
        mod_idx = path_parts.index('mod')
        # module type is next segment after 'mod'
        return path_parts[mod_idx + 1]
    except (ValueError, IndexError):
        return None

def fetch_class_html(session_token, class_id):
    url = CLASS_PAGE_URL.format(class_id=class_id)
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_documents(html):
    soup = BeautifulSoup(html, "html.parser")
    docs = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        docid = extract_resource_id(href)
        if not docid:
            continue
        mod_type = extract_module_type(href)
        if not mod_type:
            continue

        # Try to get text from <div> if exists, else from <a> directly
        div = a.find("div")
        raw_text = div.get_text(" ", strip=True) if div else a.get_text(" ", strip=True)

        # Remove leading/trailing spaces including &nbsp; chars by replacing them with space first
        cleaned_text = raw_text.replace('\xa0', ' ').replace('&nbsp;', ' ').replace('&nbsp', ' ').strip()
        # Filter unwanted top entries: skip if first char is digit or first word is 'Training'
        first_word = cleaned_text.split()[0] if cleaned_text else ""
        if first_word.lower() == "training" or (first_word and first_word[0].isdigit()):
            continue

        # Append cleaned data with mod_type, id, and full (possibly with &nbsp) text for reference
        docs.append({
            "type": cleaned_text,
            "id": docid,
            "module_type": mod_type
        })

    return docs

def get_class_documents(session_token, class_id):
    html = fetch_class_html(session_token, class_id)
    return parse_documents(html)


