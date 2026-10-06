"""FocusLab entry point:  streamlit run app.py"""
import streamlit as st

from focuslab.database import init_db
from views import dashboard, history, timer

st.set_page_config(page_title="FocusLab", page_icon="🎯", layout="wide")
init_db()

st.sidebar.title("🎯 FocusLab")
user = st.sidebar.text_input("Your profile name", value="guest", help="Sessions are stored per profile name.")
user = user.strip().lower() or "guest"
page = st.sidebar.radio("Navigate", ["Timer", "Dashboard", "History"])
st.sidebar.caption("Profiles are name-based (no password). Don't store sensitive notes.")

{"Timer": timer, "Dashboard": dashboard, "History": history}[page].render(user)
