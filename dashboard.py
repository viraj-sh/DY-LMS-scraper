import os
import io
import zipfile
import streamlit as st
from pages.content import content
from pages.attendance import attendance
from core.auth import login_and_get_session_token
from core.dashboard import parse_semesters_and_subjects
from core.classes import get_class_documents
from core.doc import get_document_resource
from core.downloader import download_file_as_bytes, get_filename_from_url
from core.attendance import fetch_detailed_attendance, fetch_overall_attendance

DATA_DIR = "data"
SESSION_ENV = os.path.join(DATA_DIR, ".env")
DASHBOARD_URL = "https://mydy.dypatil.edu/rait/my"
LOGIN_URL = "https://mydy.dypatil.edu/rait/login/index.php"

def save_token(token):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SESSION_ENV, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(SESSION_ENV):
        with open(SESSION_ENV, "r") as f:
            return f.read().strip()
    return ""

def remove_token():
    if os.path.exists(SESSION_ENV):
        os.remove(SESSION_ENV)
        
session_token = load_token()
overall_attendance = fetch_overall_attendance(session_token)
# Define pages
pages = {
    "Main Pages": [
        st.Page(content, title="Content"),
        st.Page(attendance, title=f"Attendance ({overall_attendance}%)")
    ]
}
pg = st.navigation(pages, position="top", expanded=True)
pg.run()
