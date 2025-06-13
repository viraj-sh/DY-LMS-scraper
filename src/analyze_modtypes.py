import json
from collections import Counter, defaultdict
from pathlib import Path

# === Config ===
DOCUMENTS_DIR = Path("data/documents")
ENDLINKS_DIR = Path("data/endlinks")

# === Stats ===
modtype_counts_documents = Counter()
modtype_counts_endlinks = Counter()
filetype_counts_endlinks = Counter()
subject_counts_endlinks = defaultdict(int)
errors_documents = []
errors_endlinks = []
files_processed_documents = 0
files_processed_endlinks = 0

# === Scan all JSON files in data/documents ===
for json_file in DOCUMENTS_DIR.rglob("*.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            sections = json.load(f)
        for section in sections:
            for doc in section.get("documents", []):
                modtype = str(doc.get("modtype", "unknown")).lower()
                modtype_counts_documents[modtype] += 1
        files_processed_documents += 1
    except Exception as e:
        errors_documents.append(f"⚠️ {json_file}: {e}")

# === Scan all JSON files in data/endlinks ===
for json_file in ENDLINKS_DIR.rglob("*.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            docs = json.load(f)
        for doc in docs:
            modtype = str(doc.get("modtype", "unknown")).lower()
            filetype = str(doc.get("filetype", "unknown")).lower()
            modtype_counts_endlinks[modtype] += 1
            filetype_counts_endlinks[filetype] += 1
        # Also count by subject for extra insight
        subject = json_file.parent.name
        subject_counts_endlinks[subject] += len(docs)
        files_processed_endlinks += 1
    except Exception as e:
        errors_endlinks.append(f"⚠️ {json_file}: {e}")

# === Output ===

print(f"\n✅ Processed {files_processed_documents} JSON file(s) in {DOCUMENTS_DIR}")
print("\n📊 Mod Type Distribution (data/documents):")
for modtype, count in modtype_counts_documents.most_common():
    print(f"{modtype:<20} → {count:,} occurrence(s)")

print(f"\n✅ Processed {files_processed_endlinks} JSON file(s) in {ENDLINKS_DIR}")
print("\n📊 Mod Type Distribution (data/endlinks):")
for modtype, count in modtype_counts_endlinks.most_common():
    print(f"{modtype:<20} → {count:,} occurrence(s)")

print("\n📂 File Type Distribution (data/endlinks):")
for filetype, count in filetype_counts_endlinks.most_common():
    print(f"{filetype:<20} → {count:,} occurrence(s)")

print("\n📚 Subject-wise Total Extracted Documents (data/endlinks):")
for subject, count in sorted(subject_counts_endlinks.items(), key=lambda x: -x[1]):
    print(f"{subject:<20} → {count:,} document(s)")

# === Errors ===
if errors_documents or errors_endlinks:
    print("\n⚠️ Some files failed to parse:")
    for e in errors_documents + errors_endlinks:
        print(e)
