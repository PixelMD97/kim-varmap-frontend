
import streamlit as st

def require_project():
    if "project" not in st.session_state:
        st.warning("No project selected. Please start from the Overview page.")
        st.switch_page("pages/1_overview.py")
        st.stop()
