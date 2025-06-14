import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path
import shutil
from contextlib import suppress
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === Configuration ===
DATA_DIR = Path("data")
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
SESSION_ENV_FILE = DATA_DIR / "session.env"
LOGIN_URL = "https://mydy.dypatil.edu/rait/login/index.php"
SESSION_MAX_AGE_HOURS = 6

# === Logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def create_retry_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504, 408],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def save_session_token(token: str):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = f"# SAVED_AT={datetime.utcnow().isoformat()}"
    SESSION_ENV_FILE.write_text(f"MOODLESESSION={token}\n{timestamp}\n")
    logging.info("Session token saved.")

def get_login_token(session: requests.Session) -> str:
    response = session.get(LOGIN_URL, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    token_input = soup.find("input", attrs={"name": "logintoken"})
    return token_input["value"] if token_input else ""

def login_and_get_session_token(credentials: dict) -> str:
    session = create_retry_session()
    logintoken = get_login_token(session)

    payload = {
        "uname_static": credentials["email"],
        "username": credentials["email"],
        "uname": credentials["email"],
        "password": credentials["password"],
        "rememberusername": "1",
        "logintoken": logintoken
    }

    response = session.post(LOGIN_URL, data=payload, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    if soup.select_one("div.loginerrors span.error"):
        raise ValueError("Login failed: Invalid credentials")

    if "Dashboard" not in response.text:
        raise RuntimeError("Login failed for unknown reason.")

    for cookie in session.cookies:
        if cookie.name == "MoodleSession":
            return cookie.value

    raise RuntimeError("Session token not found in cookies.")

def is_session_expired() -> bool:
    with suppress(FileNotFoundError):
        for line in SESSION_ENV_FILE.read_text().splitlines():
            if line.startswith("# SAVED_AT="):
                try:
                    saved_time = datetime.fromisoformat(line.split("=")[1])
                    return datetime.utcnow() - saved_time > timedelta(hours=SESSION_MAX_AGE_HOURS)
                except ValueError:
                    break
    return True

def session_exists() -> bool:
    return SESSION_ENV_FILE.exists() and not is_session_expired()

def generate_session(email: str, password: str) -> str:
    if not email or not password:
        raise ValueError("Email and password are required.")

    # Optional: Clear the data directory before creating a new session
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    token = login_and_get_session_token({"email": email, "password": password})
    CREDENTIALS_FILE.write_text(json.dumps({"email": email, "password": password}, indent=4))
    save_session_token(token)
    return token