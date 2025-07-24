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
