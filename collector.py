from config import BUSINESS_KEYWORD_FEEDS, COMPETITOR_FEEDS
from feeds import extract_entry_description, fetch_feed
from filter import is_relevant


def collect_from_feed_group(section: str, feeds_by_topic: dict, seen: dict) -> list[dict]:
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

                    if link in seen[seen_key]:
                        already_seen += 1
                        continue

                    title = getattr(entry, "title", "")
                    summary = extract_entry_description(entry)

                    if not is_relevant(title + " " + summary):
                        not_relevant += 1
                        continue

                    new_items.append(
                        {
                            "section": section,
                            "topic": topic,
                            "title": title,
                            "summary": summary,
                            "link": link,
                            "published": getattr(entry, "published", ""),
                            "source_url": url,
                        }
                    )

                    seen[seen_key].append(link)

                print(
                    f"  [{section}] {topic}: {total} entradas | "
                    f"{already_seen} ya vistas | {not_relevant} sin keywords | "
                    f"{total - already_seen - not_relevant} nuevas"
                )

            except Exception as exc:
                print(f"  ERROR [{section}] {topic} ({url}): {exc}")

    return new_items


def collect_all(seen: dict) -> list[dict]:
    new_items = []
    new_items.extend(collect_from_feed_group("competitors", COMPETITOR_FEEDS, seen))
    new_items.extend(collect_from_feed_group("business", BUSINESS_KEYWORD_FEEDS, seen))
    new_items.sort(key=lambda item: (item["section"], item["topic"]))
    return new_items
