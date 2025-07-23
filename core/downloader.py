import os
import requests
from urllib.parse import unquote, urlparse

DATA_DIR = "data"

def get_filename_from_url(file_url):
    """Extract the filename from the pluginfile.php URL."""
    path = urlparse(file_url).path
    filename = os.path.basename(path)
    # Sometimes filename has %20, etc.
    return unquote(filename) if filename else "downloaded_file"

def download_file(session_token, file_url, filename=None):
    """
    Downloads a file from the LMS using session token, saves to ./data directory.

    Args:
        session_token (str): MoodleSession token.
        file_url (str): Direct link to file (pluginfile.php...).
        filename (str, optional): Name to save the file as. Defaults to name from URL.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if filename is None:
        filename = get_filename_from_url(file_url)
    save_path = os.path.join(DATA_DIR, filename)

    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    with session.get(file_url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        downloaded = 0
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        done = int(50 * downloaded / total)
                        print(f"\r[{'=' * done:<50}] {downloaded//1024}KB/{total//1024}KB", end="")
        print(f"\nDownload finished: {save_path}")

# --- Example CLI usage ---
if __name__ == "__main__":
    token = input("Session token: ").strip()
    url = input("File URL: ").strip()
    # Optional: ask for filename, or leave blank to auto-extract
    filename = input("Save as (leave blank for auto): ").strip()
    filename = filename if filename else None
    download_file(token, url, filename)
