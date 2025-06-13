import json
from pathlib import Path

DATA_DIR = Path("data")
DASHBOARD_JSON = DATA_DIR / "dashboard.json"
DOCUMENTS_DIR = DATA_DIR / "documents"
ENDLINKS_DIR = DATA_DIR / "endlinks"
OUTPUT_FILE = DATA_DIR / "ultimate.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def main():
    dashboard = load_json(DASHBOARD_JSON)
    if not dashboard:
        raise ValueError("dashboard.json not found or invalid!")

    ultimate = []

    for semester in dashboard:
        semester_entry = {
            "semester_number": semester["no"],
            "semester_name": semester["name"],
            "semester_short": semester["shortName"],
            "subjects": []
        }
        for subject in semester["subjects"]:
            subject_short = subject["shortName"]
            documents_path = DOCUMENTS_DIR / semester["shortName"] / f"{subject_short}.json"
            endlinks_path = ENDLINKS_DIR / semester["shortName"] / f"{subject_short}.json"
            documents = load_json(documents_path) or []
            endlinks_raw = load_json(endlinks_path) or []

            # Transform endlinks to required structure
            resources = []
            for item in endlinks_raw:
                resources.append({
                    "name": item.get("name"),
                    "type": item.get("modtype"),
                    "filetype": item.get("filetype", "unknown"),
                    "endurl": item.get("url")
                })

            subject_entry = {
                "no": subject["no"],
                "name": subject["name"],
                "shortName": subject["shortName"],
                "url": subject["url"],
                "documents": documents,
                "resources": resources
            }
            semester_entry["subjects"].append(subject_entry)
        ultimate.append(semester_entry)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(ultimate, f, indent=2, ensure_ascii=False)
    print(f"✅ Combined data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()