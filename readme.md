# DY-LMS Scraper Dashboard

Easily download and organize your DY Patil LMS course materials with this user-friendly dashboard—no technical knowledge required!

---

## Quick Start

### 1. Installation (Windows, macOS, Linux)

**Clone the repository:**

```bash
git clone https://github.com/viraj-sh/DY-LMS-scraper.git
cd DY-LMS-scraper
```

**Set up a Python virtual environment:**

- **Linux/macOS:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows:**

  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

**Upgrade pip and install dependencies:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Start the dashboard:**

```bash
streamlit run dashboard.py
```

This will open the dashboard in your default web browser.

---

## How to Use the Dashboard

### 1. Log In

- Enter your DY Patil LMS **email** and **password**.
- Credentials are only stored locally on your computer.
- _(Documentation button to be implemented in a future update)_

---

### 2. Select Semester & Subject

- The dashboard **automatically selects the latest semester** from the dropdown.
- Choose your desired **subject** from the subject dropdown.
- _(Currently only PDF files are supported. Support for .docx and other formats may be added in future updates.)_

---

### 3. Filter Documents by Type

Use the tag system to filter documents:

- **All** → Lists every document in the selected subject.
- **Presentation** → Only shows presentation files.
- **FlexPaper** → Only shows FlexPaper materials.
- **DYQuestions** → Only shows question papers.

---

### 4. Download Files

- Click the **Download** button on any document to save it individually.
- Use the **Download All** button at the bottom to save all files in the currently selected category to `./data`.

---

### 5. Log Out

- Click **Logout** to:
  - Securely delete the session token.
  - Clear locally stored credentials.
- _(Recommended after each session.)_

---

### 6. Report Issues

- Use the GitHub repo link in the footer to report bugs or request features.

---

## Important Notes

**This tool is meant for personal use and convenience only.**

- **No unauthorized access:** Only use this tool with your own LMS credentials and data.
- **Data privacy:** All session data is stored locally in a `data/` folder. Keep it private.
- **Responsible usage:** Frequent login attempts or data fetching may trigger temporary bans.
- **Always log out after use** to ensure your session data is securely cleared.

---

## Upcoming Features

- New resource notifications
- Automatic file conversion (e.g., PPT/DOCX to PDF)
- Enhanced web interface
- Hosted version (zero setup)
- Credentials encryption
- Cloud integration (e.g., Google Drive, Discord)

**Contributions are welcome!**

- Open an issue or submit a pull request on GitHub.

**Interested in a hosted version?**

- Reach out to the project owner—limited hosted dashboards available (small fee may apply).

---

## Need Help?

- Click the **Documentation** button in the dashboard for detailed instructions.
- Visit the [GitHub Issues](https://github.com/viraj-sh/DY-LMS-scraper/issues) page for support.

Enjoy convenient access to your LMS resources—responsibly and securely!
