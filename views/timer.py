"""Focus timer page."""
import time
from datetime import datetime

import streamlit as st

from focuslab import config, services


def _save(user, elapsed_min, completed):
    services.add_session(user, st.session_state.t_subject, st.session_state.t_planned,
                         round(elapsed_min, 2), completed, st.session_state.t_notes,
                         datetime.fromtimestamp(st.session_state.t_start))
    for k in ("t_start", "t_planned", "t_subject", "t_notes"):
        st.session_state.pop(k, None)


@st.fragment(run_every=1)
def _running_panel(user):
    s = st.session_state
    if "t_start" not in s:
        return
    total = s.t_planned * 60
    elapsed = time.time() - s.t_start
    if elapsed >= total:
        _save(user, s.t_planned, True)
        st.balloons()
        st.rerun()
    m, sec = divmod(int(total - elapsed), 60)
    st.caption(f"Focusing on **{s.t_subject}**")
    st.markdown(f"<h1 style='text-align:center;font-size:5.5rem;margin:0'>{m:02d}:{sec:02d}</h1>",
                unsafe_allow_html=True)
    st.progress(min(elapsed / total, 1.0))
    c1, c2 = st.columns(2)
    if c1.button("⏹ Stop & save", use_container_width=True):
        _save(user, elapsed / 60, False)
        st.rerun()
    if c2.button("🗑 Discard", use_container_width=True):
        for k in ("t_start", "t_planned", "t_subject", "t_notes"):
            s.pop(k, None)
        st.rerun()


def render(user: str):
    st.header("⏱ Focus Timer")
    if "t_start" in st.session_state:
        _running_panel(user)
        st.info("Keep this tab open. Stay on this page so the session auto-saves when time is up.")
        return

    subjects = services.list_subjects(user) or config.DEFAULT_SUBJECTS
    c1, c2 = st.columns([2, 1])
    choice = c1.selectbox("Subject", subjects + ["➕ New subject…"])
    subject = c1.text_input("New subject name") if choice.startswith("➕") else choice
    minutes = c2.number_input("Minutes", 1, 240, config.DEFAULT_MINUTES, step=5)
    notes = st.text_input("Notes (optional)")
    if st.button("▶ Start focus session", type="primary", use_container_width=True):
        if not subject.strip():
            st.error("Please enter a subject.")
        else:
            st.session_state.update(t_start=time.time(), t_planned=minutes,
                                    t_subject=subject.strip(), t_notes=notes)
            st.rerun()

    with st.expander("Log a past session manually"):
        with st.form("manual", clear_on_submit=True):
            m_subject = st.text_input("Subject", value=subject)
            d = st.date_input("Date", datetime.now().date())
            t = st.time_input("Start time", datetime.now().time().replace(second=0, microsecond=0))
            dur = st.number_input("Minutes studied", 1, 600, 25)
            done = st.checkbox("Completed", value=True)
            if st.form_submit_button("Save session"):
                try:
                    services.add_session(user, m_subject, dur, dur, done, "", datetime.combine(d, t))
                    st.success("Saved!")
                except ValueError as e:
                    st.error(str(e))
