import os
import io
import zipfile
import streamlit as st
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

def fetch_dashboard_html(session_token):
    import requests
    session = requests.Session()
    session.cookies.set("MoodleSession", session_token)
    resp = session.get(DASHBOARD_URL, timeout=10)
    resp.raise_for_status()
    return resp.text

def attendance():
    st.title("LMS Attendance")

    session_token = load_token()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = bool(session_token)

    # LOGIN PAGE
    if not st.session_state.logged_in:
        st.subheader("Login")
        email = st.text_input("ID / Email")
        password = st.text_input("Password", type="password")
        login = st.button("Login")
        if login:
            try:
                token = login_and_get_session_token(email, password, LOGIN_URL)
                save_token(token)
                st.session_state.logged_in = True
                st.success("Login successful.")
                st.rerun()
            except Exception as e:
                st.error(f"{e}")
        return

    # LOGOUT
    if st.button("Logout"):
        remove_token()
        st.session_state.logged_in = False
        st.rerun()
        return
    
    
    
    
    data = fetch_detailed_attendance(session_token)

    # Display as simple HTML table
    html = "<table><tr>"
    # headers
    for key in data[0].keys():
        html += f"<th>{key}</th>"
    html += "</tr>"

    # rows
    for row in data:
        html += "<tr>"
        for cell in row.values():
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)  
    
      


    


