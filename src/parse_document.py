import json
import re
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Configuration ===
DATA_DIR = Path("data")
DOCLINKS_DIR = DATA_DIR / "doclinks"
ENDLINKS_DIR = DATA_DIR / "endlinks"

def extract_flexpaper_url(html):
    match = re.search(r"PDFFile\s*:\s*['\"](https?://[^'\"]+\.pdf)['\"]", html)
    return match.group(1) if match else None

def extract_resource_url(html):
    pdfs = re.findall(r'href=["\'](https?://[^"\']+\.pdf)["\']', html, re.I)
    if pdfs:
        return pdfs[0]
    docs = re.findall(r'href=["\'](https?://[^"\']+\.(docx?|pptx?|xlsx?))["\']', html, re.I)
    return docs[0] if docs else None

def extract_iframe_url(html):
    match = re.search(r'<iframe[^>]+src=["\'](https?://[^"\']+)["\']', html)
    return match.group(1) if match else None

def extract_general_url(html):
    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.I)
    for link in links:
        if any(x in link for x in ["profile.php", "user/view.php"]):
            continue
        if any(link.lower().endswith(ext) for ext in [".pdf", ".doc", ".docx", ".ppt", ".pptx"]):
            return link
    return None

MODTYPE_HANDLERS = {
    "flexpaper": extract_flexpaper_url,
    "resource": extract_resource_url,
    "presentation": extract_iframe_url,
    "url": extract_general_url,
    "dyquestion": extract_general_url,
    "questionpaper": extract_resource_url
}

def detect_modtype(html, fallback):
    if 'flexpaper_viewer' in html:
        return "flexpaper"
    if 'modtype_resource' in html:
        return "resource"
    if 'iframe' in html:
        return "presentation"
    if 'modtype_url' in html:
        return "url"
    return fallback

def detect_filetype(url):
    if not url:
        return "unknown"
    url = url.lower().split("?")[0].split("#")[0]
    if url.endswith(".pdf"):
        return "pdf"
    elif url.endswith(".doc"):
        return "doc"
    elif url.endswith(".docx"):
        return "docx"
    elif url.endswith(".ppt"):
        return "ppt"
    elif url.endswith(".pptx"):
        return "pptx"
    elif url.endswith(".xls"):
        return "xls"
    elif url.endswith(".xlsx"):
        return "xlsx"
    elif "viewer" in url and "pdf" in url:
        return "pdf"
    return "unknown"

def process_html(html_file):
    try:
        content = html_file.read_text(encoding="utf-8")
        fallback_modtype = html_file.stem.split("_")[0].lower()
        modtype = detect_modtype(content, fallback_modtype)
        handler = MODTYPE_HANDLERS.get(modtype, extract_general_url)
        final_url = handler(content)
        if final_url:
            filetype = detect_filetype(final_url)
            return {
                "name": re.sub(r'_+', ' ', html_file.stem).title(),
                "modtype": modtype,
                "url": final_url,
                "filetype": filetype
            }
    except Exception as e:
        print(f"⚠️ Error: {html_file} → {e}")
    return None

def process_subject(subject_dir, semester_name):
    html_files = list(subject_dir.glob("*.html"))
    if not html_files:
        print(f"🚫 No HTML files found in {subject_dir}")
        return

    docs = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_html, file): file for file in html_files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                docs.append(result)

    if docs:
        output_dir = ENDLINKS_DIR / semester_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{subject_dir.name}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        print(f"✅ {output_file} written with {len(docs)} items")
    else:
        print(f"🚫 No valid documents found in {subject_dir}")

def main():
    parser = argparse.ArgumentParser(description="Parse downloaded LMS documents")
    parser.add_argument("--semester", help="Target semester short name")
    parser.add_argument("--subject", help="Target subject short name")
    args = parser.parse_args()

    if args.semester and args.subject:
        # Single subject mode
        subject_dir = DOCLINKS_DIR / args.semester / args.subject
        if subject_dir.exists():
            process_subject(subject_dir, args.semester)
        else:
            print(f"🚫 Directory not found: {subject_dir}")
    else:
        # Batch processing mode
        for semester_dir in DOCLINKS_DIR.iterdir():
            if semester_dir.is_dir():
                for subject_dir in semester_dir.iterdir():
                    if subject_dir.is_dir():
                        process_subject(subject_dir, semester_dir.name)

if __name__ == "__main__":
    main()
    print("\n✅ Document parsing completed")