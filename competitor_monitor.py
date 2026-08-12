#!/usr/bin/env python3
"""
Competitor Monitor for Virtual Commissioning Market

Sources:
- RSS feeds
- YouTube channel feeds (no API required)
- Company blogs with RSS

Outputs:
- data/seen.json
- data/latest_by_topic.json
- business_intelligence_brief.md
- business_intelligence_brief.csv
- docs/index.html
"""

from collector import build_display_items, collect_all
from datetime_utils import format_mexico_now
from config import CSV_OUTPUT, HTML_OUTPUT, MARKDOWN_OUTPUT
from storage import (
    load_latest_by_topic,
    load_seen,
    save_latest_by_topic,
    save_seen,
)
from writers import write_csv, write_html, write_markdown


def main() -> None:
    seen = load_seen()
    latest = load_latest_by_topic()

    new_items = collect_all(seen, latest)
    save_seen(seen)
    save_latest_by_topic(latest)

    display_items = build_display_items(new_items, latest)
    generated_at = format_mexico_now()

    write_csv(display_items, CSV_OUTPUT)
    write_markdown(display_items, generated_at, MARKDOWN_OUTPUT)
    write_html(display_items, generated_at, HTML_OUTPUT)

    fallback_count = sum(1 for item in display_items if item.get("is_fallback"))
    print(
        f"Found {len(new_items)} new posts; "
        f"{len(display_items)} display rows "
        f"({fallback_count} topic fallbacks)"
    )


if __name__ == "__main__":
    main()
