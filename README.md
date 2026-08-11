# Industrial Automation Business Intelligence Brief

This repository generates a daily brief focused on:

- Business keyword news (virtual commissioning, digital twin, PLC/robot simulation, intralogistics)
- Competitor updates

## Outputs

- `business_intelligence_brief.md` : human-readable report for GitHub
- `business_intelligence_brief.csv` : structured data export
- `data/seen.json` : history of seen links to avoid duplicates

## Project structure

- `competitor_monitor.py` — entry point
- `config.py` — feed URLs, keywords, output paths
- `feeds.py`, `filter.py`, `storage.py`, `collector.py`, `writers.py` — fetch, filter, dedup, and report logic

## Run locally

```bash
python -m pip install -r requirements.txt
python competitor_monitor.py
```

## Daily automation on GitHub

Workflow file: `.github/workflows/daily_business_brief.yml`

- Runs every day at `12:00 UTC` (targeting `06:00` Mexico City time)
- Can also be triggered manually from the Actions tab
- Commits updated report files back to the repository automatically

## Recommended view in GitHub

Open `business_intelligence_brief.md` directly in the repository to read the latest report.
