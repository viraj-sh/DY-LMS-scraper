import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path
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

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def create_retry_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def save_session_token(token: str):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    session_line = f"MOODLESESSION={token}\n"
    timestamp_line = f"# SAVED_AT={datetime.utcnow().isoformat()}\n"

    lines = []

    with suppress(FileNotFoundError):
        with SESSION_ENV_FILE.open("r") as f:
            lines = f.readlines()

    updated = False
    for idx, line in enumerate(lines):
        if line.startswith("MOODLESESSION="):
            lines[idx] = session_line
            updated = True
        elif line.startswith("# SAVED_AT="):
            lines[idx] = timestamp_line

    if not updated:
        lines.append(session_line)
        lines.append(timestamp_line)

    with SESSION_ENV_FILE.open("w") as f:
        f.writelines(lines)

    logging.info(f"Session token saved to {SESSION_ENV_FILE}")


def get_login_token(session: requests.Session) -> str:
    response = session.get(LOGIN_URL)
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

    response = session.post(LOGIN_URL, data=payload)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # === Detect login failure ===
    error_span = soup.select_one("div.loginerrors span.error")
    if error_span:
        error_msg = error_span.text.strip()
        raise ValueError(f"Login failed: {error_msg}")

    if "Dashboard" not in response.text:
        raise RuntimeError("Login failed for unknown reason.")

    for cookie in session.cookies:
        if cookie.name == "MoodleSession":
            return cookie.value

    raise RuntimeError("MoodleSession cookie not found after login.")


def is_session_expired() -> bool:
    with suppress(FileNotFoundError):
        with SESSION_ENV_FILE.open("r") as f:
            for line in f:
                if line.startswith("# SAVED_AT="):
                    try:
                        saved_time = datetime.fromisoformat(line.strip().split("=")[1])
                        return datetime.utcnow() - saved_time > timedelta(hours=SESSION_MAX_AGE_HOURS)
                    except ValueError:
                        pass
    return True


def generate_session(email=None, password=None) -> str:
    if not email or not password:
        logging.info("Prompting for credentials...")
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()

    # Try login first, but don't save credentials yet
    try:
        token = login_and_get_session_token({"email": email, "password": password})
    except ValueError as ve:
        logging.error(str(ve))
        raise
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise

    # Only save credentials if login was successful
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CREDENTIALS_FILE.open("w") as f:
        json.dump({"email": email, "password": password}, f, indent=4)

    save_session_token(token)
    return token



def main():
    if not is_session_expired():
        logging.info("Session is still valid. Nothing to do.")
        return

    credentials = None
    if CREDENTIALS_FILE.exists():
        with CREDENTIALS_FILE.open("r") as f:
            credentials = json.load(f)

    email = credentials.get("email") if credentials else None
    password = credentials.get("password") if credentials else None

    if not email or not password:
        logging.info("Credentials incomplete or missing.")
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()

    generate_session(email=email, password=password)


if __name__ == "__main__":
    main()
