"""Demo data generator so new users can explore the dashboard."""
import random
from datetime import datetime, timedelta, timezone

from . import config, db


def seed_demo(username: str, days: int = 45, db_path=None) -> int:
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    n = 0
    for d in range(days):
        if rng.random() < 0.25:
            continue
        for _ in range(rng.randint(1, 4)):
            planned = rng.choice([25, 25, 45, 50])
            done = rng.random() < 0.82
            actual = planned if done else rng.randint(5, planned - 1)
            start = now - timedelta(days=d, hours=rng.randint(0, 10))
            db.add_session(username, rng.choice(config.DEFAULT_SUBJECTS[:5]), start,
                           planned, actual, done, db_path=db_path)
            n += 1
    return n
