#!/usr/bin/env python3
"""
Competitor Monitor for Virtual Commissioning Market

Sources:
- RSS feeds
- YouTube channel feeds (no API required)
- Company blogs with RSS

Outputs:
- data/seen.json
- business_intelligence_brief.md
- business_intelligence_brief.csv
- docs/index.html
"""

from datetime import datetime, timezone

from collector import collect_all
from config import CSV_OUTPUT, HTML_OUTPUT, MARKDOWN_OUTPUT
from storage import load_seen, save_seen
from writers import write_csv, write_html, write_markdown


def main() -> None:
    seen = load_seen()
    new_items = collect_all(seen)
    save_seen(seen)

    generated_at = datetime.now(timezone.utc).isoformat()

    write_csv(new_items, CSV_OUTPUT)
    write_markdown(new_items, generated_at, MARKDOWN_OUTPUT)
    write_html(new_items, generated_at, HTML_OUTPUT)

    print(f"Found {len(new_items)} new posts")


if __name__ == "__main__":
    main()
