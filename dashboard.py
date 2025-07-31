import os
import io
import zipfile
import streamlit as st
from core.auth import login_and_get_session_token
from core.dashboard import parse_semesters_and_subjects
from core.classes import get_class_documents
from core.doc import get_document_resource
from core.downloader import download_file_as_bytes, get_filename_from_url

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

def main():
    st.title("LMS Dashboard")

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

    # DASHBOARD FETCH
    session_token = load_token()
    try:
        dashboard_html = fetch_dashboard_html(session_token)
    except Exception as e:
        st.error("Session expired or network error. Please login again.")
        remove_token()
        st.session_state.logged_in = False
        st.rerun()
        return

    semesters = parse_semesters_and_subjects(dashboard_html)
    if not semesters:
        st.error("No semesters found. Try refreshing or re-logging in.")
        return

    # SEMESTER AND CLASS SELECTION
    current_sem = semesters[-1]["semester"]
    st.subheader(f"Current Semester: {current_sem}")
    sem_options = [sem["semester"] for sem in semesters]
    selected_sem = st.selectbox("Select semester", sem_options, index=len(sem_options) - 1)
    subjects = next(s["subjects"] for s in semesters if s["semester"] == selected_sem)

    subj_names = [s['name'] for s in subjects]
    subject_choice = st.selectbox("Select subject/class", subj_names)
    selected_subject_id = next(s['id'] for s in subjects if s['name'] == subject_choice)

    # DOCUMENT LISTING
    docs = get_class_documents(session_token, selected_subject_id)
    if not docs:
        st.info("No documents found in this subject.")
        return

    MODTYPES = ["all", "flexpaper", "dyquestion", "presentation", "url"]
    tag = st.radio("Filter documents by type", MODTYPES, horizontal=True)
    DOWNLOADABLE_TYPES = ("flexpaper", "dyquestion", "presentation")
    NONDOWNLOADABLE_TYPES = ("url")
    if tag == "all":
        display_docs = [d for d in docs if d["module_type"] in DOWNLOADABLE_TYPES or d["module_type"] in NONDOWNLOADABLE_TYPES]
    else:
        display_docs = [d for d in docs if d["module_type"] == tag]

    st.write("### Documents in this class:")
    for doc in display_docs:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{doc['type']}")
        with col2:
            if doc['module_type'] in DOWNLOADABLE_TYPES:
                file_url = get_document_resource(session_token, doc["module_type"], doc["id"])
                if file_url:
                    file_bytes = download_file_as_bytes(session_token, file_url)
                    filename = get_filename_from_url(file_url)
                    st.download_button(
                        label="Download",
                        data=file_bytes,
                        file_name=filename,
                        mime="application/octet-stream",
                        key=f"download-{doc['id']}"  # Unique key per doc
                    )
                else:
                    st.write("-")
            elif doc['module_type'] in NONDOWNLOADABLE_TYPES:
                file_url = get_document_resource(session_token, doc["module_type"], doc["id"])
                st.markdown(
                    f"""
                    <style>
                    a.custom-view-link {{
                        text-decoration: none !important;
                        color: #FAFAFA !important;
                        font-weight: 500;
                        transition: color 0.2s ease-in-out;
                    }}
                    a.custom-view-link:hover {{
                        color: #FF4B4B !important;
                        text-decoration: underline !important;
                        text-underline-offset: 4px !important;
                    }}
                    </style>

                    <a href="{file_url}" target="_blank" class="custom-view-link">View</a>
                    """,
                    unsafe_allow_html=True
                )



            else:
                st.write("-")

    # --- DOWNLOAD ALL as ZIP ---
    if display_docs and st.button("Download All as ZIP"):
        with st.spinner("Preparing ZIP file..."):
            zip_buffer = io.BytesIO()
            added = 0
            with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for doc in display_docs:
                    if doc['module_type'] in DOWNLOADABLE_TYPES:
                        file_url = get_document_resource(session_token, doc["module_type"], doc["id"])
                        if file_url:
                            try:
                                file_bytes = download_file_as_bytes(session_token, file_url)
                                filename = get_filename_from_url(file_url)
                                zipf.writestr(filename, file_bytes)
                                added += 1
                            except Exception as e:
                                st.warning(f"Failed to add file: {filename}: {e}")
            zip_buffer.seek(0)
            if added:
                st.success(f"Prepared {added} files in ZIP archive.")
                st.download_button(
                    label="Download All as ZIP",
                    data=zip_buffer,
                    file_name=f"{subject_choice.replace(' ','_')}_documents.zip",
                    mime="application/zip",
                    key=f"zip-download-{selected_subject_id}"  # Ensures uniqueness per subject
                    
                )
            else:
                st.info("No files could be added to ZIP.")

if __name__ == "__main__":
    main()
