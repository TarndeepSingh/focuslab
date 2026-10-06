"""Pandas analytics: pure functions that take a sessions DataFrame."""
from datetime import date, timedelta

import pandas as pd


def summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total_hours": 0.0, "sessions": 0, "completion_rate": 0.0, "avg_min": 0.0}
    return {
        "total_hours": df["actual_min"].sum() / 60,
        "sessions": len(df),
        "completion_rate": df["completed"].mean() * 100,
        "avg_min": df["actual_min"].mean(),
    }


def filter_days(df: pd.DataFrame, days: int | None) -> pd.DataFrame:
    if days is None or df.empty:
        return df
    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=days - 1)
    return df[df["started_at"] >= cutoff]


def weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Hours studied per ISO week (Monday start), gaps filled with 0."""
    if df.empty:
        return pd.DataFrame(columns=["week", "hours"])
    week = df["started_at"].dt.to_period("W").dt.start_time
    s = (df.groupby(week)["actual_min"].sum() / 60)
    full = pd.date_range(s.index.min(), s.index.max(), freq="7D")
    s = s.reindex(full, fill_value=0)
    return s.rename_axis("week").reset_index(name="hours")


def daily_minutes(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    end = pd.Timestamp.now().normalize()
    idx = pd.date_range(end - pd.Timedelta(days=days - 1), end, freq="D")
    if df.empty:
        s = pd.Series(0.0, index=idx)
    else:
        s = df.groupby(df["started_at"].dt.normalize())["actual_min"].sum().reindex(idx, fill_value=0)
    return s.rename_axis("day").reset_index(name="minutes")


def subject_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["subject", "hours"])
    out = (df.groupby("subject")["actual_min"].sum() / 60).sort_values(ascending=False)
    return out.rename("hours").reset_index()


def weekday_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if df.empty:
        return pd.DataFrame(0.0, index=days, columns=range(24))
    pivot = df.pivot_table(index=df["started_at"].dt.dayofweek, columns=df["started_at"].dt.hour,
                           values="actual_min", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(index=range(7), columns=range(24), fill_value=0)
    pivot.index = days
    return pivot


def streaks(df: pd.DataFrame, today: date | None = None) -> dict:
    """Current and longest streak of consecutive days with >0 focus minutes."""
    today = today or date.today()
    if df.empty:
        return {"current": 0, "longest": 0}
    active = df[df["actual_min"] > 0]["started_at"].dt.date
    days = sorted(set(active))
    if not days:
        return {"current": 0, "longest": 0}
    longest = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if cur - prev == timedelta(days=1) else 1
        longest = max(longest, run)
    day_set, current = set(days), 0
    cursor = today if today in day_set else today - timedelta(days=1)
    while cursor in day_set:
        current += 1
        cursor -= timedelta(days=1)
    return {"current": current, "longest": longest}
