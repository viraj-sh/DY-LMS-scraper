import requests
import logging
from pathlib import Path
from contextlib import suppress
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Configuration ===
DATA_DIR = Path("data")
SESSION_ENV_FILE = DATA_DIR / "session.env"
DASHBOARD_HTML_FILE = DATA_DIR / "dashboard.html"
DASHBOARD_URL = "https://mydy.dypatil.edu/rait/my/"

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def create_retry_session():
    """Same retry strategy as in generate_session.py"""
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def load_moodle_session():
    """Read the MoodleSession cookie from session.env"""
    with suppress(FileNotFoundError):
        with SESSION_ENV_FILE.open("r") as f:
            for line in f:
                if line.startswith("MOODLESESSION="):
                    return line.strip().split("=")[1]

    raise RuntimeError(f"MOODLESESSION not found in {SESSION_ENV_FILE}")


def fetch_dashboard_html():
    """Fetch dashboard page using MoodleSession cookie"""
    session = create_retry_session()
    moodle_session = load_moodle_session()
    session.cookies.set("MoodleSession", moodle_session, domain="mydy.dypatil.edu")

    logging.info(f"Fetching dashboard from {DASHBOARD_URL} ...")
    response = session.get(DASHBOARD_URL)

    if response.ok and "Dashboard" in response.text:
        DATA_DIR.mkdir(exist_ok=True)
        DASHBOARD_HTML_FILE.write_text(response.text, encoding="utf-8")
        logging.info(f"Dashboard saved to {DASHBOARD_HTML_FILE}")
    else:
        logging.error(f"Failed to fetch dashboard: HTTP {response.status_code}")
        response.raise_for_status()


def main():
    try:
        fetch_dashboard_html()
    except Exception as e:
        logging.exception("An error occurred while fetching dashboard")


if __name__ == "__main__":
    main()
