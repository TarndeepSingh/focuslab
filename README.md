# 🎯 FocusLab — Study Session Tracker & Analytics

Pomodoro-style focus timer + analytics dashboard. Python, Streamlit, SQLite, Pandas, Plotly.

## Structure
```
focuslab/
├── app.py               # entry point (sidebar, routing)
├── focuslab/            # backend package
│   ├── config.py        # paths & defaults (DB path via FOCUSLAB_DB env var)
│   ├── database.py      # SQLite connection + schema
│   ├── services.py      # add / fetch / delete sessions
│   ├── analytics.py     # Pandas: weekly trend, subjects, streaks, heatmap
│   └── charts.py        # Plotly figures
├── views/               # frontend pages: timer, dashboard, history
├── tests/test_core.py   # pytest suite
├── .streamlit/config.toml
├── Dockerfile
└── requirements.txt
```

## Run locally
1. Install Python 3.10+.
2. `cd focuslab`
3. `python -m venv .venv` then activate it
   (Windows: `.venv\Scripts\activate`, Mac/Linux: `source .venv/bin/activate`)
4. `pip install -r requirements.txt`
5. `streamlit run app.py` → opens http://localhost:8501
6. (Optional) `pytest` to run the tests.

## Using it
- **Timer**: pick a subject (or add one), set minutes, Start. Finishing auto-logs a *completed* session;
  "Stop & save" logs elapsed time as *incomplete*. Stay on the Timer page while it runs.
- **Dashboard**: KPIs, streaks, weekly hours, subject split, daily minutes, weekday×hour heatmap.
- **History**: filter, export CSV, delete sessions.
- Data is separated by the *profile name* in the sidebar (no password).

## Deploy
**Streamlit Community Cloud (free, public):**
1. Push this folder to a GitHub repo.
2. Go to share.streamlit.io → New app → choose repo, branch, main file `app.py` → Deploy.
3. Note: its disk is ephemeral, so SQLite data may reset on restarts. For persistent data use Docker/VPS below.

**Docker (persistent data):**
```
docker build -t focuslab .
docker run -d -p 8501:8501 -v focuslab_data:/data focuslab
```
Works on Render, Railway, Fly.io or any VPS (mount a persistent volume at `/data`).

## Next steps
Add real auth (e.g. streamlit-authenticator), or swap SQLite for Postgres in `database.py` for heavy multi-user use.
