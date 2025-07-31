import requests
import re
from bs4 import BeautifulSoup


session_token = "lfftu5eutbf3eoonnc0dccinb1"


def fetch_detailed_attendance(session_token):
    """
    """
    url = f"https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=attendance"
    headers = {
        "Cookie": "session_token"
    }
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    # print(resp.text)
    html_data = resp.text
    soup = BeautifulSoup(html_data, "html.parser")
    
    table_rows = soup.select("tbody > tr")
    data = []

    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue  # skip malformed rows

        subject = cells[0].text.strip()
        total_classes = cells[1].text.strip()
        present = cells[2].text.strip()
        absent = cells[3].text.strip()
        percentage = cells[4].text.strip()

        data.append({
            "Subject": subject,
            "Total Classes": total_classes,
            "Present": present,
            "Absent": absent,
            "Percentage": percentage
        })

    return data
def fetch_overall_attendance(session_token):
    """
    """
    url = f"https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=myclasses"
    headers = {
        "Cookie": "session_token"
    }
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    circular_value = soup.find("p", class_="circular_value")
    if circular_value:
        value = circular_value.get_text(strip=True)
        # value looks like: "67%Overall Attendance", so remove everything after first non-digit
        import re
        match = re.match(r"(\d+)", value)
        return match.group(1) if match else None
    return None    
