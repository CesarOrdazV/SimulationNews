# AGENTS.md

## Cursor Cloud specific instructions

### What this project is
A single-file Python job (`competitor_monitor.py`) that fetches industrial-automation
news from RSS / Google News / YouTube feeds via `feedparser`, dedupes against
`data/seen.json`, and writes three regenerated outputs:
- `business_intelligence_brief.md`
- `business_intelligence_brief.csv`
- `docs/index.html` (styled static page served via GitHub Pages)

In production it runs daily via GitHub Actions (`.github/workflows/daily_business_brief.yml`).

### Dependencies
Only one runtime dependency (`feedparser`, in `requirements.txt`). The startup update
script installs it into the Python user site (`pip install --user`), so run the script
with the system `python3` (no venv is used; `python3 -m venv` is unavailable because the
`python3.12-venv` system package is not installed).

### Running / testing
- Run the job: `python3 competitor_monitor.py` (needs outbound internet to reach the feeds).
- There is no lint config and no automated test suite in this repo.
- Preview the generated page locally: `python3 -m http.server 8000` from the repo root,
  then open `http://localhost:8000/docs/index.html`.

### Gotchas
- Running the script mutates tracked files (`business_intelligence_brief.md/.csv`,
  `docs/index.html`, `data/seen.json`). If you only ran it to verify the environment,
  restore them with `git checkout -- business_intelligence_brief.md business_intelligence_brief.csv docs/index.html data/seen.json`
  so you don't commit incidental data churn.
- `data/seen.json` already contains a large seen-link history, so a normal run may report
  "0 new posts". To see fully-populated output, temporarily reset it (`echo "{}" > data/seen.json`),
  run, then restore it — this mirrors the workflow's `reset_seen` dispatch input.
