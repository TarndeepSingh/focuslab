from datetime import date, datetime, timedelta

import pytest

from focuslab import analytics, config, services
from focuslab.database import init_db


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    init_db()


def test_add_fetch_delete():
    sid = services.add_session("a", "Math", 25, 25, True)
    assert len(services.fetch_sessions("a")) == 1
    assert services.fetch_sessions("b").empty
    assert services.delete_session("a", sid)
    assert services.fetch_sessions("a").empty


def test_validation():
    with pytest.raises(ValueError):
        services.add_session("a", " ", 25, 25, True)


def test_streaks_and_summary():
    now = datetime.now()
    for d in (0, 1, 2, 5, 6):
        services.add_session("a", "Math", 30, 30, d != 6, started_at=now - timedelta(days=d))
    df = services.fetch_sessions("a")
    assert analytics.streaks(df, date.today()) == {"current": 3, "longest": 3}
    assert analytics.summary(df)["sessions"] == 5
    assert analytics.subject_distribution(df).iloc[0]["hours"] == pytest.approx(2.5)
    assert not analytics.weekly_trend(df).empty
    assert len(analytics.daily_minutes(df, 30)) == 30


def test_empty_frames():
    df = services.fetch_sessions("nobody")
    assert analytics.streaks(df) == {"current": 0, "longest": 0}
    assert analytics.weekly_trend(df).empty
