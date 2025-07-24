import requests
from urllib.parse import unquote, urlparse
import os

def get_filename_from_url(file_url):
    """
    Extracts a clean filename from the end of a URL.
    """
    path = urlparse(file_url).path
    filename = os.path.basename(path)
    return unquote(filename) if filename else "downloaded_file"

def download_file_as_bytes(session_token, file_url):
    """
    Fetches a file from a URL protected by MoodleSession.
    Returns file bytes (to use with Streamlit's download_button).
    """
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    with session.get(file_url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        return resp.content  # File as bytes

# ---- Example usage for plain Python testing (saves locally) ----
if __name__ == "__main__":
    token = input("Session token: ").strip()
    url = input("File URL: ").strip()
    # You can also test this in plain python (if you want local save, not for Streamlit):
    fname = get_filename_from_url(url)
    data = download_file_as_bytes(token, url)
    with open(fname, "wb") as f:
        f.write(data)
    print(f"Saved file: {fname}")
