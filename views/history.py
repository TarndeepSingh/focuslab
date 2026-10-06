"""Session history page."""
import streamlit as st

from focuslab import services


def render(user: str):
    st.header("🗂 History")
    df = services.fetch_sessions(user)
    if df.empty:
        st.info("Nothing logged yet.")
        return
    subjects = st.multiselect("Filter by subject", sorted(df["subject"].unique()))
    if subjects:
        df = df[df["subject"].isin(subjects)]
    show = df[["id", "started_at", "subject", "planned_min", "actual_min", "completed", "notes"]]
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button("⬇ Export CSV", show.to_csv(index=False), "focuslab_sessions.csv", "text/csv")
    with st.expander("Delete a session"):
        sid = st.number_input("Session id", min_value=1, step=1)
        if st.button("Delete", type="secondary"):
            ok = services.delete_session(user, sid)
            st.success("Deleted.") if ok else st.error("No such session for your profile.")
            if ok:
                st.rerun()
