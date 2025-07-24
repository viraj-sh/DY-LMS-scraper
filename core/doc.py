import requests
import re
from bs4 import BeautifulSoup

DOC_URL = "https://mydy.dypatil.edu/rait/mod/{mod_type}/view.php?id={doc_id}"

def fetch_document_html(session_token, mod_type, doc_id):
    url = DOC_URL.format(mod_type=mod_type, doc_id=doc_id)
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def extract_flexpaper_pdf_url(html):
    match = re.search(
        r"PDFFile\s*:\s*'(https://mydy\.dypatil\.edu/rait/pluginfile\.php[^']+)'", html)
    if match:
        return match.group(1)
    return None

def extract_dyquestion_pdf_url(html):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="dyquestioncontent")
    if not content:
        return None
    for a in content.find_all("a", href=True):
        if "pluginfile.php" in a["href"]:
            return a["href"]
    obj = content.find("object", attrs={"data": True})
    if obj and "pluginfile.php" in obj["data"]:
        return obj["data"]
    return None

def extract_presentation_pdf_url(html):
    soup = BeautifulSoup(html, "html.parser")
    
    presentation = soup.find("div", class_="presentationcontent")
    if presentation:
        obj = presentation.find("object", attrs={"data": True})
        if obj and "pluginfile.php" in obj["data"]:
            return obj["data"]
        # 2. Or fallback: a <a href="...pluginfile.php/...">
        for a in presentation.find_all("a", href=True):
            if "pluginfile.php" in a["href"]:
                return a["href"]
    
    obj = soup.find("object", attrs={"data": True})
    if obj and "pluginfile.php" in obj["data"]:
        return obj["data"]
    for a in soup.find_all("a", href=True):
        if "pluginfile.php" in a["href"]:
            return a["href"]
    return None

def get_document_resource(session_token, mod_type, doc_id):
    html = fetch_document_html(session_token, mod_type, doc_id)
    if mod_type == "flexpaper":
        return extract_flexpaper_pdf_url(html)
    elif mod_type == "dyquestion":
        return extract_dyquestion_pdf_url(html)
    elif mod_type == "presentation":
        return extract_presentation_pdf_url(html)
    else:
        return None
