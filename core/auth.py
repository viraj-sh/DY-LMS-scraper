import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_retry_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504, 408],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def _fetch_login_token(session, login_url):
    """Fetch CSRF login token from the LMS login page."""
    res = session.get(login_url, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    input_tag = soup.find("input", attrs={"name": "logintoken"})
    return input_tag["value"] if input_tag else None

def login_and_get_session_token(email: str, password: str, login_url: str) -> str:
    """
    Logs into the LMS portal and returns the MoodleSession token.
    Raises ValueError or RuntimeError on failure.
    """

    session = create_retry_session()
    login_token = _fetch_login_token(session, login_url)

    payload = {
        "uname_static": email,
        "username": email,
        "uname": email,
        "password": password,
        "rememberusername": "1",
    }
    if login_token:
        payload["logintoken"] = login_token

    resp = session.post(login_url, data=payload, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.select_one("div.loginerrors span.error"):
        raise ValueError("Login failed: Invalid credentials.")

    # Check typical login success condition
    if "Dashboard" not in resp.text and "dashboard" not in resp.url.lower():
        raise RuntimeError("Login failed for an unknown reason.")

    for cookie in session.cookies:
        if cookie.name.lower() == "moodlesession":
            return cookie.value

    raise RuntimeError("Session token not found after login.")

# ---- Example Reusable Usage ----
# from core.auth import login_and_get_session_token
# token = login_and_get_session_token(email, password, "https://mydy.dypatil.edu/rait/login/index.php")
