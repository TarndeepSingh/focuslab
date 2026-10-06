"""Analytics dashboard page."""
import streamlit as st

from focuslab import analytics, charts, services

RANGES = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": None}


def render(user: str):
    st.header("📊 Dashboard")
    df = services.fetch_sessions(user)
    if df.empty:
        st.info("No sessions yet — head to the Timer and complete your first one!")
        return
    label = st.radio("Range", list(RANGES), horizontal=True, index=1)
    view = analytics.filter_days(df, RANGES[label])

    s, st_ = analytics.summary(view), analytics.streaks(df)
    k = st.columns(5)
    k[0].metric("Total focus", f"{s['total_hours']:.1f} h")
    k[1].metric("Sessions", s["sessions"])
    k[2].metric("Completion", f"{s['completion_rate']:.0f}%")
    k[3].metric("🔥 Current streak", f"{st_['current']} d")
    k[4].metric("🏆 Longest streak", f"{st_['longest']} d")

    left, right = st.columns(2)
    wk = analytics.weekly_trend(view)
    if not wk.empty:
        left.plotly_chart(charts.weekly_chart(wk), use_container_width=True)
    sub = analytics.subject_distribution(view)
    if not sub.empty:
        right.plotly_chart(charts.subject_chart(sub), use_container_width=True)
    st.plotly_chart(charts.daily_chart(analytics.daily_minutes(view, RANGES[label] or 30)),
                    use_container_width=True)
    st.plotly_chart(charts.heatmap_chart(analytics.weekday_hour_heatmap(view)), use_container_width=True)
