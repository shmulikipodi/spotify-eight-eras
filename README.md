# Eight Eras

Two pages built from my Spotify extended streaming history (May 2023 – September 2026):

- **Eight Eras** (`/`) – how my music taste changed: the genre river, eight eras and the seven changes between them (week by week), each genre on its own, music age, variety, month-to-month similarity and every artist's lifeline.
- **The Long Play** (`/long-play`) – listening habits: every day on a calendar, skips, who picks the songs, the weekly clock, sessions and side stories.

## How it's built

Plain Python (pandas) turns the export into JSON, which is embedded into self-contained HTML pages. No framework, no build step on the server.

1. Request "Extended streaming history" from Spotify's privacy settings and unzip it into `spotify_raw/` (not committed).
2. `python -m venv .venv && .venv/bin/pip install pandas openpyxl numpy`
3. Run the pipeline:
   - `build2.py` → `output/dash2.json` (habits, for The Long Play)
   - `build4.py` → `output/dash4.json` (eras and transitions; uses `build3.py`, `trends.py`, `tags.py`)
   - `make_story.py` → `output/eight_eras.html`
   - Long Play: inject `output/dash2.json` into `longplay_template.html` (replace `__DATA__`) → `output/the_long_play.html`
   - `build_site.py` → `site/`

Genres and decades in `tags.py` were assigned by hand to the 400 most-played artists (95% of listening time); Spotify's export has no genre data. Eras come from a segmentation of monthly genre and artist mixes.

Times are Israel time. A play counts at 30 seconds. Raw data, CSV and Excel exports are kept out of the repo because they include IP addresses and full play logs.
