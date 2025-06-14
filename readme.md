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

* **Linux/macOS:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **Windows:**

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
streamlit run web/dashboard.py
```

This will open the dashboard in your default web browser.

---

## How to Use the Dashboard

### 1. Log In

* Enter your DY Patil LMS **email** and **password**.
* Optionally, click the **Documentation** button for detailed guidance.
* Credentials are only stored locally on your computer.

### 2. Fetch Your Data

* Click **Fetch Latest Data** to load all available semesters and subjects.

### 3. Select a Semester

* Use the radio buttons to choose your desired semester.

### 4. Fetch & Parse Semester

* Click **Fetch+Parse \[Semester Name]** to load and process documents.

### 5. Browse & Download Materials

* Expand any subject to view documents organized by week.
* Each document displays its name, type, and a **Download** button.

### 6. Log Out

* Click **Logout** to securely delete all session data and credentials.
* Recommended after each session.

### 7. Report Issues

* Use the GitHub repo link in the footer to report bugs or request features.

---

## Important Notes

**This tool is meant for personal use and convenience only.**

* **No unauthorized access:** Only use this tool with your own LMS credentials and data.
* **Data privacy:** All session data is stored locally in a `data/` folder. Keep it private.
* **Responsible usage:** Frequent login attempts or data fetching may trigger temporary bans.
* **Always log out after use** to ensure your session data is securely cleared.

---

## Upcoming Features

* New resource notifications
* Automatic file conversion (e.g., PPT/DOCX to PDF)
* Enhanced web interface
* Hosted version (zero setup)
* Credentials encryption
* Cloud integration (e.g., Google Drive, Discord)

**Contributions are welcome!**

* Open an issue or submit a pull request on GitHub.

**Interested in a hosted version?**

* Reach out to the project owner—limited hosted dashboards available (small fee may apply).

---

## Need Help?

* Click the **Documentation** button in the dashboard for detailed instructions.
* Visit the [GitHub Issues](https://github.com/viraj-sh/DY-LMS-scraper/issues) page for support.

Enjoy convenient access to your LMS resources—responsibly and securely!
