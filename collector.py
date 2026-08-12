from config import BUSINESS_KEYWORD_FEEDS, COMPETITOR_FEEDS
from datetime_utils import format_entry_published, is_published_newer
from feeds import extract_entry_description, fetch_feed
from filter import is_relevant

ARTICLE_FIELDS = (
    "section",
    "topic",
    "title",
    "summary",
    "link",
    "published",
    "source_url",
)


def _article_record(item: dict) -> dict:
    return {field: item.get(field, "") for field in ARTICLE_FIELDS}


def _update_latest(latest: dict, key: str, item: dict) -> None:
    record = _article_record(item)
    existing = latest.get(key)
    if not existing:
        latest[key] = record
        return
    if is_published_newer(record.get("published", ""), existing.get("published", "")):
        latest[key] = record


def collect_from_feed_group(
    section: str,
    feeds_by_topic: dict,
    seen: dict,
    latest: dict,
) -> list[dict]:
    new_items = []

    for topic, urls in feeds_by_topic.items():
        seen_key = f"{section}:{topic}"
        seen.setdefault(seen_key, [])

        for url in urls:
            try:
                feed = fetch_feed(url)

                if feed.bozo:
                    bozo_msg = getattr(feed, "bozo_exception", "unknown error")
                    print(f"  WARN {topic} ({url}): {bozo_msg}")

                total = len(feed.entries)
                already_seen = 0
                not_relevant = 0

                for entry in feed.entries:
                    link = getattr(entry, "link", "")
                    title = getattr(entry, "title", "")
                    summary = extract_entry_description(entry)

                    if not is_relevant(title + " " + summary):
                        not_relevant += 1
                        continue

                    item = {
                        "section": section,
                        "topic": topic,
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": format_entry_published(entry),
                        "source_url": url,
                    }

                    # Keep the newest relevant article per topic for fallback display.
                    _update_latest(latest, seen_key, item)

                    if link in seen[seen_key]:
                        already_seen += 1
                        continue

                    new_items.append(item)
                    seen[seen_key].append(link)

                print(
                    f"  [{section}] {topic}: {total} entradas | "
                    f"{already_seen} ya vistas | {not_relevant} sin keywords | "
                    f"{total - already_seen - not_relevant} nuevas"
                )

            except Exception as exc:
                print(f"  ERROR [{section}] {topic} ({url}): {exc}")

    return new_items


def collect_all(seen: dict, latest: dict) -> list[dict]:
    new_items = []
    new_items.extend(
        collect_from_feed_group("competitors", COMPETITOR_FEEDS, seen, latest)
    )
    new_items.extend(
        collect_from_feed_group("business", BUSINESS_KEYWORD_FEEDS, seen, latest)
    )
    new_items.sort(key=lambda item: (item["section"], item["topic"]))
    return new_items


def build_display_items(new_items: list[dict], latest: dict) -> list[dict]:
    """
    Build report rows so every configured topic shows content:
    - new articles only when the topic has new items this run
    - otherwise the last stored article for that topic (fallback)
    """
    new_by_key: dict[str, list[dict]] = {}
    for item in new_items:
        key = f"{item['section']}:{item['topic']}"
        new_by_key.setdefault(key, []).append(item)

    display_items: list[dict] = []
    feed_groups = (
        ("competitors", COMPETITOR_FEEDS),
        ("business", BUSINESS_KEYWORD_FEEDS),
    )

    for section, feeds_by_topic in feed_groups:
        for topic in feeds_by_topic:
            key = f"{section}:{topic}"
            topic_new = new_by_key.get(key, [])
            if topic_new:
                display_items.extend(_article_record(item) for item in topic_new)
                continue

            fallback = latest.get(key)
            if fallback:
                row = _article_record(fallback)
                row["is_fallback"] = True
                display_items.append(row)

    return display_items
