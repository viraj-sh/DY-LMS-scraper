# DY-LMS Scraper

A Python tool to log in to DY Patil LMS, scrape all course resources, and download them for offline use.

## Features

* Automatic secure login
* Complete scraping pipeline: dashboard, subjects, documents, links
* Interactive downloader: choose what to download
* Structured folders and meaningful filenames
* One command to run everything via a simple menu
* Safe local storage of your session and credentials


## Project Structure

```
.
├── data/
│   ├── credentials.json
│   ├── session.env
│   ├── dashboard.* (HTML/JSON)
│   ├── subjects/
│   ├── documents/
│   ├── endlinks/
│   ├── doclinks/
│   └── output/ (downloaded files)
├── requirements.txt
├── run.py (main menu)
├── src/ (all scripts)
│   ├── generate_session.py
│   ├── fetch_dashboard.py
│   ├── parse_dashboard.py
│   ├── fetch_subject.py
│   ├── parse_subject.py
│   ├── fetch_document.py
│   ├── parse_document.py
│   ├── ultimate_json.py
│   ├── output.py
│   └── analyze_modtypes.py
├── web/ (optional, planned web version)
└── README.md (this file)
```

---

## Getting Started

### 1. Clone the Repository

Open your terminal or command prompt and run:

```
git clone DY-LMS-scraper
cd DY-LMS-scraper
```

Replace `<your-repo-url>` with your actual Git repository URL.

### 2. Create and Activate a Virtual Environment

Create a virtual environment inside the cloned folder:

```
python -m venv venv
```

Activate it:

* **Windows:**

  ```
  venv\Scripts\activate
  ```

* **macOS/Linux:**

  ```
  source venv/bin/activate
  ```

### 3. Install Dependencies

Upgrade `pip` and install all required Python packages:

```
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Menu

Run the main menu to access all features:

```
python run.py
```

---

## How to Use the Menu

When you run `run.py`, you’ll see this menu:

```
1. Generate Login Token
2. Scrape All Data
3. Download Resources
0. Exit
```

**What each option does:**

1. **Generate Login Token:**
   Logs you in securely and saves your session info in `data/session.env`.

2. **Scrape All Data:**
   Runs the full scraping pipeline — fetches dashboard, subjects, documents, and builds all JSON data.

3. **Download Resources:**
   Downloads the actual files (PDFs, PPTs, etc.) into organized folders.

4. **Exit:**
   Closes the program.

---

## How It Works Internally

| Script                  | What it does                                                    |
| ----------------------- | --------------------------------------------------------------- |
| `generate_session.py`   | Handles LMS login and saves your session.                       |
| `fetch_*` and `parse_*` | Scrapes and processes LMS data step by step.                    |
| `ultimate_json.py`      | Combines all scraped data into a single JSON for easy download. |
| `output.py`             | Handles file downloading and organizing.                        |

---

## Data and Security

* Your credentials and session token are saved locally inside the `data/` folder.
* No data is sent anywhere except your LMS account.
* Use responsibly — generating too many sessions or scraping too fast may lead to IP blocking by your college.

## Disclaimer

* This tool is for downloading course materials you already have access to.
* Do not use it to share or misuse content.
* The author is not responsible for misuse.
* Use at your own risk.

## Planned Improvements

* Notifications when new resources are uploaded
* Automatic file conversion (e.g., PPTX to PDF)
* Web interface for easier use
* Cloud backups or integrations
* Open to suggestions and contributions

## Contributing

Pull requests, issues, and ideas are welcome!

## Contact

Open an issue on GitHub or reach out if you have questions, find bugs, or want to contribute.


