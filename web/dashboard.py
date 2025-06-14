import sys
import os
import json
import shutil
import subprocess
import requests
from pathlib import Path
from urllib.parse import unquote
import streamlit as st

# --- Setup Path ---
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.generate_session import generate_session, SESSION_ENV_FILE, session_exists

# --- Page Config: Use wide layout for full-width dashboard ---
st.set_page_config(page_title="DY-LMS Scraper", layout="centered")

# --- Optional: Minimal Button Styling ---
st.markdown("""
    <style>
    .stButton > button {
        padding: 0.5em 1.5em;
        border-radius: 6px;
        font-weight: 500;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = session_exists()
if "selected_semester" not in st.session_state:
    st.session_state.selected_semester = None
if "show_docs" not in st.session_state:
    st.session_state.show_docs = False  # For documentation page

# --- Documentation Page ---
def show_documentation():
    if st.button("← Back"):
        st.session_state.show_docs = False
        st.rerun()
    st.title("Project Documentation")
    st.markdown("""
    ---
    ## Project Structure

    ![Project Structure](https://i.ibb.co/s9f0HcfW/2025-06-14-121957-hyprshot.png "Project Structure Diagram")
    ... (documentation content unchanged) ...
    """)

# --- Logout Function ---
def logout_session():
    data_dir = project_root / "data"
    try:
        if SESSION_ENV_FILE.exists():
            SESSION_ENV_FILE.unlink()
        if data_dir.exists():
            shutil.rmtree(data_dir)
            st.info("All session data cleared successfully")
    except Exception as e:
        st.error(f"Error clearing data: {str(e)}")
    st.session_state.logged_in = False
    st.session_state.selected_semester = None
    st.rerun()

# --- Helper: Load Moodle Session ---
def load_moodle_session():
    session_env = project_root / "data" / "session.env"
    with open(session_env, "r") as f:
        for line in f:
            if line.startswith("MOODLESESSION="):
                return line.strip().split("=", 1)[1]
    raise ValueError("MOODLESESSION not found in session.env")

# --- Helper: Create Requests Session ---
def create_session():
    session = requests.Session()
    session.cookies.set("MoodleSession", load_moodle_session(), domain="mydy.dypatil.edu")
    return session

# --- Login Page ---
def show_login():
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Documentation"):
            st.session_state.show_docs = True
            st.rerun()
    st.title("DY-LMS Scraper Login")
    st.markdown("Enter your DY Patil LMS credentials to begin. Your session is saved locally.")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    with st.spinner("Logging in..."):
                        generate_session(email=email, password=password)
                    st.session_state.logged_in = True
                    st.success("Login successful. Session saved locally.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
                    st.warning(
                        'If your credentials are correct but login fails, please visit '
                        '[mydy.dypatil.edu](https://mydy.dypatil.edu/) and verify manually.'
                    )
    st.markdown(
        """
        <p style="margin-top:20px; font-size:0.9rem;">
        Encounter an issue?
        <a href="https://github.com/viraj-sh/DY-LMS-scraper/issues" target="_blank"
        style="text-decoration: none; color: #1E88E5;">
        Report a bug
        </a>
        </p>
        """,
        unsafe_allow_html=True
    )

# --- Dashboard Page ---
def show_dashboard():
    # --- Top bar: Logout (left), Documentation (right) ---
    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        if st.button("Logout", key="logout_top", use_container_width=True):
            logout_session()
    with col3:
        if st.button("Documentation", key="docs_top", use_container_width=True):
            st.session_state.show_docs = True
            st.rerun()

    st.title("DY-LMS Scraper Dashboard")

    with st.container(border=True):
        if st.button("Fetch Latest Data", help="Retrieve updated information from LMS"):
            try:
                with st.spinner("Fetching and parsing data..."):
                    subprocess.run(["python", "src/fetch_dashboard.py"], check=True)
                    subprocess.run(["python", "src/parse_dashboard.py"], check=True)
                st.success("Data updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Data update failed: {str(e)}")

    data_path = project_root / "data" / "dashboard.json"
    if data_path.exists():
        try:
            with open(data_path) as f:
                dashboard_data = json.load(f)
            # --- Minimal semester selection: radio buttons with correct logic ---
            semester_options = {sem["name"]: sem for sem in dashboard_data}
            # Determine default semester (last one or previously selected)
            default_sem = next(
                (sem for sem in dashboard_data if sem["shortName"] == st.session_state.selected_semester),
                dashboard_data[-1]
            )
            semester_names = list(semester_options.keys())
            default_index = semester_names.index(default_sem["name"])
            selected_label = st.radio(
                "Select Semester",
                semester_names,
                index=default_index
            )
            selected_sem = semester_options[selected_label]
            st.session_state.selected_semester = selected_sem["shortName"]

            st.subheader(f"{selected_sem['name']} Subjects")

            # --- Minimal fetch/parse actions for subjects ---
            fetch_col1, fetch_col2 = st.columns([1, 2])
            with fetch_col1:
                if st.button("Fetch+Parse All Semesters"):
                    try:
                        with st.spinner("Fetching and parsing all subjects for all semesters..."):
                            subprocess.run(["python", "src/fetch_subject.py"], check=True)
                            subprocess.run(["python", "src/parse_subject.py"], check=True)
                        st.success("Fetched and parsed all subjects for all semesters!")
                    except Exception as e:
                        st.error(f"Operation failed: {str(e)}")
            with fetch_col2:
                if st.button(f"Fetch+Parse {selected_sem['name']}"):
                    try:
                        with st.spinner(f"Fetching and parsing all subjects for {selected_sem['name']}..."):
                            subprocess.run([
                                "python", "src/fetch_subject.py",
                                "--semester", selected_sem["shortName"]
                            ], check=True)
                            subprocess.run([
                                "python", "src/parse_subject.py",
                                "--semester", selected_sem["shortName"]
                            ], check=True)
                        st.success(f"Fetched and parsed all subjects for {selected_sem['name']}!")
                    except Exception as e:
                        st.error(f"Operation failed: {str(e)}")

            # --- Subject and document display ---
            for subject in selected_sem["subjects"]:
                subject_dir = project_root / "data" / "documents" / selected_sem["shortName"]
                json_file = subject_dir / f"{subject['shortName']}.json"
                with st.expander(f"{subject['name']}", expanded=False):
                    if json_file.exists():
                        try:
                            with open(json_file) as f:
                                weeks_data = json.load(f)
                            for week in weeks_data:
                                st.markdown(f"**Week {week['no']}: {week['name']}**")
                                # Table of documents
                                for doc in week["documents"]:
                                    cols = st.columns([0.7, 4, 2, 2])
                                    cols[0].write(f"{doc['no']}.")
                                    cols[1].write(doc['name'])
                                    cols[2].write(doc["modtype"].upper())
                                    with cols[3]:
                                        if st.button(
                                            "Download",
                                            key=f"download_{selected_sem['shortName']}_{subject['shortName']}_{week['no']}_{doc['no']}_{doc['url'][-10:]}",
                                            help=f"Download {doc['name']}"
                                        ):
                                            try:
                                                with st.spinner(f"Processing {doc['name']}..."):
                                                    # Clean up any existing parsed data for this subject to avoid conflicts
                                                    cleanup_path = project_root / "data" / "endlinks" / selected_sem["shortName"] / f"{subject['shortName']}.json"
                                                    if cleanup_path.exists():
                                                        cleanup_path.unlink()
                                                    doclinks_dir = project_root / "data" / "doclinks" / selected_sem["shortName"] / subject["shortName"]
                                                    if doclinks_dir.exists():
                                                        for html_file in doclinks_dir.glob("*.html"):
                                                            html_file.unlink()
                                                    subprocess.run([
                                                        "python", "src/fetch_document.py",
                                                        "--url", doc["url"],
                                                        "--semester", selected_sem["shortName"],
                                                        "--subject", subject["shortName"]
                                                    ], check=True)
                                                    subprocess.run([
                                                        "python", "src/parse_document.py",
                                                        "--semester", selected_sem["shortName"],
                                                        "--subject", subject["shortName"]
                                                    ], check=True)
                                                    json_path = project_root / "data" / "endlinks" / selected_sem["shortName"] / f"{subject['shortName']}.json"
                                                    if not json_path.exists():
                                                        st.error("Failed to generate download link. Please try again.")
                                                        continue
                                                    with open(json_path, "r", encoding="utf-8") as pf:
                                                        parsed_data = json.load(pf)
                                                    if not parsed_data:
                                                        st.error("No download URLs found in parsed data.")
                                                        continue
                                                    final_url = parsed_data[0]["url"]
                                                    session = create_session()
                                                    response = session.get(final_url, timeout=30)
                                                    response.raise_for_status()
                                                    file_content = response.content
                                                    filename = unquote(Path(final_url).name.split("?")[0])
                                                    if not filename or filename == "":
                                                        filename = f"{doc['name']}.pdf"
                                                    st.download_button(
                                                        label=f"Save {filename}",
                                                        data=file_content,
                                                        file_name=filename,
                                                        mime="application/octet-stream",
                                                        key=f"save_{selected_sem['shortName']}_{subject['shortName']}_{doc['no']}"
                                                    )
                                                    st.success(f"{filename} is ready for download!")
                                            except subprocess.CalledProcessError as e:
                                                st.error(f"Script execution failed: {str(e)}")
                                            except requests.RequestException as e:
                                                st.error(f"Download failed: {str(e)}")
                                            except Exception as e:
                                                st.error(f"Unexpected error: {str(e)}")
                        except Exception as e:
                            st.error(f"Error loading documents: {str(e)}")
                    else:
                        st.info("No documents available. Fetch & parse first.")
        except Exception as e:
            st.error(f"Error loading dashboard data: {str(e)}")
    else:
        st.info("No data available. Click 'Fetch Latest Data' to retrieve your course information.")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.9rem;">
        GitHub repo:
        <a href="https://github.com/viraj-sh/DY-LMS-scraper" target="_blank"
        style="text-decoration: none; color: #1E88E5;">
        viraj-sh/DY-LMS-scraper  
        </a>      Encounter an issue?<a href="https://github.com/viraj-sh/DY-LMS-scraper/issues" target="_blank"
        style="text-decoration: none; color: #1E88E5;">   Report a bug</a>
        
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Main App Routing ---
if st.session_state.show_docs:
    show_documentation()
elif st.session_state.logged_in:
    show_dashboard()
else:
    show_login()