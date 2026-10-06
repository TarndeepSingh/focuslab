"""Central configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("FOCUSLAB_DB", BASE_DIR / "data" / "focuslab.db"))
DEFAULT_SUBJECTS = ["Mathematics", "Physics", "Programming", "Reading", "Writing"]
DEFAULT_MINUTES = 25
