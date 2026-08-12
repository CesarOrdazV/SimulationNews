# AGENTS.md

Context guide for AI agents. Read this file before exploring the full repository.

## What this project is

A daily competitive-intelligence monitor for **industrial automation** (virtual commissioning, digital twin, PLC/robot simulation, intralogistics). Python modules collect news from RSS, Google News, and YouTube feeds, filter by keywords, deduplicate entries, and generate reports.

**Entry point:** `competitor_monitor.py` (`main()`)  
**Automation:** GitHub Actions (`.github/workflows/daily_business_brief.yml`) — runs daily at 12:00 UTC (~06:00 Mexico City) and can be triggered manually.

## Repository layout

```
competitor_monitor.py          # Entry point: orchestrates load → collect → write
config.py                      # Feeds, keywords, paths, section labels
feeds.py                       # Feed fetching and entry text extraction
filter.py                      # Keyword relevance check
storage.py                     # seen.json load/save
collector.py                   # Feed-group iteration and deduplication
datetime_utils.py              # America/Mexico_City formatting helpers
writers.py                     # CSV, Markdown, and HTML output writers
requirements.txt               # feedparser>=6.0.11
.github/workflows/
  daily_business_brief.yml     # CI: install deps, run script, commit outputs
data/
  seen.json                    # Seen-link history (deduplication)
docs/
  index.html                   # Styled static page (GitHub Pages)
business_intelligence_brief.md # Human-readable Markdown report
business_intelligence_brief.csv# Structured CSV export
README.md                      # Human-facing documentation
```

There is no test suite, linter, or formatter config.

## Data flow

1. **Load** `data/seen.json` — dict `{ "section:topic": [link, ...] }`.
2. **Iterate two feed groups:**
   - `COMPETITOR_FEEDS` — NVIDIA, RoboDK, Siemens, Visual Components, Rockwell/Emulate3D, AnyLogic, F.EE.
   - `BUSINESS_KEYWORD_FEEDS` — Virtual Commissioning, Digital Twin, PLC Simulation, Robot Simulation, Intralogistics Simulation (via Google News RSS).
3. **For each entry:** skip if the link is already in `seen`; discard if title+summary contain none of `KEYWORDS`.
4. **Normalize timestamps** via `datetime_utils.py` (`America/Mexico_City`, format `YYYY-MM-DD HH:MM`) for entry `published` and report generation time.
5. **Write outputs** with only **new** entries from this run (not a cumulative history).
6. **Persist** the updated `seen.json`.

## Date and time

- All user-facing timestamps use **`America/Mexico_City`** (stdlib `zoneinfo`; no extra deps).
- Helpers live in `datetime_utils.py`: `format_mexico_now()`, `format_entry_published()`, `format_mexico_datetime()`.
- Format is `YYYY-MM-DD HH:MM` (no seconds). Markdown/HTML headers label the zone as `(Mexico City)`.
- RSS `published` / `updated` values are converted from feedparser struct times (UTC) into Mexico City local time in `collector.py`.

## Sources and filtering

- Direct blog RSS feeds, YouTube channel feeds (`/feeds/videos.xml`), and Google News RSS searches.
- `_fetch_feed()` fetches manually with SSL bypass, gzip/deflate decompression, and `feedparser` parsing.
- `KEYWORDS` includes: virtual commissioning, digital twin, simulation, factory, robot, plc, automation, opc ua, industrial, intralogistics, material handling, tia portal, omniverse.
- To add a competitor or topic: edit `COMPETITOR_FEEDS` / `BUSINESS_KEYWORD_FEEDS` in `config.py`.

## Generated outputs

| File | Format | Content |
|------|--------|---------|
| `business_intelligence_brief.md` | Markdown | Header `Generated: … (Mexico City)`; Business Keywords / Competitors sections, grouped by topic |
| `business_intelligence_brief.csv` | CSV | columns: section, topic, title, summary, published, link, source_url (`published` in Mexico City time) |
| `docs/index.html` | Static HTML | Header `Updated: … (Mexico City)`; same data with dark-mode UI; links to .md and .csv |
| `data/seen.json` | JSON | Deduplication state (mutated on every run) |

If there are no new articles, reports say *"No new relevant articles found."*

## Running locally

```bash
python -m pip install -r requirements.txt
python competitor_monitor.py
```

Requires outbound internet (external feeds). Preview the page:

```bash
python -m http.server 8000
# Open http://localhost:8000/docs/index.html
```

## CI / GitHub Actions

Workflow: `Daily Business Intelligence Brief`

- **Schedule:** `0 12 * * *` (UTC)
- **Manual dispatch:** `reset_seen` input (boolean) — clears `data/seen.json` before generating
- **Auto-commit** of: `business_intelligence_brief.md`, `.csv`, `data/seen.json`, `docs/index.html`
- Commit message: `chore: update daily business intelligence brief`

## Important gotchas for agents

1. **Running the script mutates tracked files.** If you only test the environment, restore afterward:
   ```bash
   git checkout -- business_intelligence_brief.md business_intelligence_brief.csv docs/index.html data/seen.json
   ```
2. **`seen.json` already has extensive history** — a normal run often reports `0 new posts`. To see populated output, temporarily reset it (`echo "{}" > data/seen.json`), run, then restore (or use `reset_seen` in Actions).
3. **Modular layout** — logic is split across flat modules at repo root; `competitor_monitor.py` is only the orchestrator.
4. **Do not commit accidental data changes** — outputs are updated automatically by CI; manual brief edits are usually noise.
5. **`data/latest_by_topic.json`** exists in the repo but is **not used** by the current script; ignore it unless explicitly integrated.

## Common tasks

| Task | Where to change |
|------|-----------------|
| Add competitor / feed | `COMPETITOR_FEEDS` in `config.py` |
| Add business topic | `BUSINESS_KEYWORD_FEEDS` in `config.py` |
| Adjust relevance filter | `KEYWORDS` list in `config.py` |
| Change feed fetch logic | `feeds.py` |
| Change collection / dedup logic | `collector.py` |
| Change timezone / datetime format | `datetime_utils.py` |
| Change HTML styling | inline CSS block in `writers.py` |
| Change CI schedule | cron in `daily_business_brief.yml` |
| Change dependencies | `requirements.txt` |
