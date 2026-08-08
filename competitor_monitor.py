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

import csv
import gzip
import html
import json
import re
import ssl
import urllib.request
import zlib
from datetime import datetime, timezone
from pathlib import Path

import feedparser

# SSL bypass integrado en _fetch_feed (ver función abajo)


def _fetch_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch con SSL bypass, descompresión explícita, luego parsea con feedparser."""
    import re
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            "User-Agent": "feedparser/6.0 +https://feedparser.readthedocs.io/",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
            "Accept-Encoding": "gzip, deflate",
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            raw = resp.read()
            enc = resp.headers.get("Content-Encoding", "")
        if enc == "gzip":
            raw = gzip.decompress(raw)
        elif enc == "deflate":
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompress(raw, -15)
        raw = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", raw)
        return feedparser.parse(raw)
    except Exception as exc:
        result = feedparser.FeedParserDict()
        result["entries"] = []
        result["bozo"] = True
        result["bozo_exception"] = exc
        return result

COMPETITOR_FEEDS = {
    # Feeds directos de blog (RSS funcionando)
    "NVIDIA": [
        "https://blogs.nvidia.com/feed/",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCSKUoczbGAcMld7HjpCR8OA",   # NVIDIA Omniverse
    ],
    "RoboDK": [
        "https://robodk.com/blog/feed/",
        "https://www.youtube.com/feeds/videos.xml?user=RoboDK",
    ],
    # Google News RSS — para sitios con feeds rotos o sin RSS
    "Siemens Digital Industries": [
        "https://news.google.com/rss/search?q=siemens+digital+industries+simulation+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCYR5Kgzn6suihs56iJ8_vfw",   # Siemens Software
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCaEEm-0s0x3MHg9jzFcHuQQ",   # Siemens Knowledge Hub
    ],
    "Visual Components": [
        "https://news.google.com/rss/search?q=%22visual+components%22+simulation+manufacturing&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC-mCG6o3M7-U-INitjtLCXg",   # Visual Components
    ],
    "Rockwell Automation": [
        "https://news.google.com/rss/search?q=rockwell+automation+emulate3d+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?user=ROKAutomation",
        "https://www.emulate3d.com/feed/",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCIdH_v1UnEmeqA5Gl2zs7kA",   # Emulate3D
    ],
    "AnyLogic": [
        "https://news.google.com/rss/search?q=anylogic+simulation+digital+twin&hl=en&gl=US&ceid=US:en",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCdH-e29FvfphfWmI2EMZPhg",
    ],
    # F.EE: sin blog RSS ni Google News — solo YouTube
    "F.EE / fescreen-sim": [
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCEUDfVb3q1VVyQubsAmwTPw",
    ],
}

BUSINESS_KEYWORD_FEEDS = {
    "Virtual Commissioning": [
        "https://news.google.com/rss/search?q=%22virtual+commissioning%22+manufacturing+automation&hl=en&gl=US&ceid=US:en",
    ],
    "Digital Twin Manufacturing": [
        "https://news.google.com/rss/search?q=%22digital+twin%22+manufacturing+simulation&hl=en&gl=US&ceid=US:en",
    ],
    "PLC Simulation": [
        "https://news.google.com/rss/search?q=plc+simulation+industrial+automation&hl=en&gl=US&ceid=US:en",
    ],
    "Robot Simulation": [
        "https://news.google.com/rss/search?q=robot+simulation+offline+programming+factory&hl=en&gl=US&ceid=US:en",
    ],
    "Intralogistics Simulation": [
        "https://news.google.com/rss/search?q=intralogistics+simulation+warehouse+automation&hl=en&gl=US&ceid=US:en",
    ],
}

KEYWORDS = [
    "virtual commissioning",
    "digital twin",
    "simulation",
    "factory",
    "robot",
    "robotics",
    "plc",
    "automation",
    "opc ua",
    "industrial",
    "intralogistics",
    "material handling",
    "tia portal",
    "omniverse",
]

DATA_DIR = Path("data")
SEEN_FILE = DATA_DIR / "seen.json"
PAGES_DIR = Path("docs")


def load_seen():
    DATA_DIR.mkdir(exist_ok=True)
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text(encoding="utf-8-sig"))
    return {}


def save_seen(data):
    SEEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def relevant(text):
    text = (text or "").lower()
    return any(k in text for k in KEYWORDS)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _truncate(text: str, limit: int = 500) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def extract_entry_description(entry) -> str:
    # Intenta primero campos largos (content), luego summary/description.
    content_list = getattr(entry, "content", None)
    if content_list:
        for block in content_list:
            value = block.get("value", "") if isinstance(block, dict) else ""
            cleaned = _clean_text(value)
            if cleaned:
                return _truncate(cleaned)

    for field in ("summary", "description"):
        cleaned = _clean_text(getattr(entry, field, ""))
        if cleaned:
            return _truncate(cleaned)

    return ""


seen = load_seen()
new_items = []

def collect_from_feed_group(section: str, feeds_by_topic: dict):
    for topic, urls in feeds_by_topic.items():
        seen_key = f"{section}:{topic}"
        seen.setdefault(seen_key, [])

        for url in urls:
            try:
                feed = _fetch_feed(url)

                # feedparser no lanza excepciones en errores de red/parseo
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

                    if not relevant(title + " " + summary):
                        not_relevant += 1
                        continue

                    new_items.append({
                        "section": section,
                        "topic": topic,
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": getattr(entry, "published", ""),
                        "source_url": url,
                    })

                    seen[seen_key].append(link)

                print(
                    f"  [{section}] {topic}: {total} entradas | "
                    f"{already_seen} ya vistas | {not_relevant} sin keywords | "
                    f"{total - already_seen - not_relevant} nuevas"
                )

            except Exception as exc:
                print(f"  ERROR [{section}] {topic} ({url}): {exc}")


collect_from_feed_group("competitors", COMPETITOR_FEEDS)
collect_from_feed_group("business", BUSINESS_KEYWORD_FEEDS)

save_seen(seen)

new_items.sort(key=lambda x: (x["section"], x["topic"]))
generated_at = datetime.now(timezone.utc).isoformat()

sections = [
    ("business", "Business Keywords"),
    ("competitors", "Competitors"),
]

with open("business_intelligence_brief.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "section",
            "topic",
            "title",
            "summary",
            "published",
            "link",
            "source_url",
        ]
    )
    writer.writeheader()
    writer.writerows(new_items)

with open("business_intelligence_brief.md", "w", encoding="utf-8") as f:
    f.write("# Industrial Automation Business Intelligence Brief\n\n")
    f.write(f"Generated: {generated_at}\n\n")

    if not new_items:
        f.write("No new relevant articles found.\n")
    else:
        for section_key, section_title in sections:
            section_items = [x for x in new_items if x["section"] == section_key]
            f.write(f"## {section_title}\n\n")

            if not section_items:
                f.write("No new relevant articles found.\n\n")
                continue

            current_topic = None

            for item in section_items:
                if item["topic"] != current_topic:
                    current_topic = item["topic"]
                    f.write(f"### {current_topic}\n\n")

                f.write(
                    f"- [{item['title']}]({item['link']})"
                    f" ({item['published']})\n"
                )

                if item["summary"]:
                    f.write(f"  Summary: {item['summary']}\n")

                if item["source_url"]:
                    f.write(f"  Feed source: {item['source_url']}\n")

            f.write("\n")

PAGES_DIR.mkdir(exist_ok=True)

with open(PAGES_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write("<!doctype html>\n")
    f.write("<html lang=\"en\">\n")
    f.write("<head>\n")
    f.write("  <meta charset=\"utf-8\">\n")
    f.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n")
    f.write("  <title>Industrial Automation Business Intelligence Brief</title>\n")
    f.write("  <style>\n")
    f.write("    :root { color-scheme: dark; }\n")
    f.write("    body { font-family: Segoe UI, Tahoma, sans-serif; margin: 0; background: radial-gradient(circle at 20% 0%, #1e2f4f 0%, #101827 45%, #0a111e 100%); color: #eaf2ff; }\n")
    f.write("    .wrap { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }\n")
    f.write("    .hero { background: linear-gradient(120deg, #274777, #3d6aa5); color: #f6fbff; border: 1px solid #5f87bc; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(8, 14, 24, 0.35); }\n")
    f.write("    h1 { margin: 0 0 8px; font-size: 1.8rem; }\n")
    f.write("    h2 { margin-top: 28px; border-bottom: 2px solid #2c3e5c; padding-bottom: 6px; color: #d9e7ff; }\n")
    f.write("    h3 { margin-top: 20px; color: #b8cef4; }\n")
    f.write("    .card { background: rgba(22, 33, 54, 0.82); border: 1px solid #314767; border-radius: 12px; padding: 14px; margin-bottom: 12px; backdrop-filter: blur(2px); }\n")
    f.write("    .meta { color: #9fb3d6; font-size: 0.92rem; margin: 6px 0 10px; }\n")
    f.write("    a { color: #7ec8ff; text-decoration: none; }\n")
    f.write("    a:hover { color: #a8dcff; text-decoration: underline; }\n")
    f.write("    .summary { line-height: 1.45; margin: 8px 0; color: #e5edfa; }\n")
    f.write("    .footer { margin-top: 28px; font-size: 0.9rem; color: #9ab2d8; }\n")
    f.write("  </style>\n")
    f.write("</head>\n")
    f.write("<body>\n")
    f.write("  <div class=\"wrap\">\n")
    f.write("    <div class=\"hero\">\n")
    f.write("      <h1>Industrial Automation Business Intelligence Brief</h1>\n")
    f.write(f"      <div>Generated (UTC): {html.escape(generated_at)}</div>\n")
    f.write("    </div>\n")

    if not new_items:
        f.write("    <p>No new relevant articles found.</p>\n")
    else:
        for section_key, section_title in sections:
            section_items = [x for x in new_items if x["section"] == section_key]
            f.write(f"    <h2>{html.escape(section_title)}</h2>\n")

            if not section_items:
                f.write("    <p>No new relevant articles found.</p>\n")
                continue

            current_topic = None

            for item in section_items:
                if item["topic"] != current_topic:
                    current_topic = item["topic"]
                    f.write(f"    <h3>{html.escape(current_topic)}</h3>\n")

                f.write("    <article class=\"card\">\n")
                f.write(
                    "      <div><a href=\""
                    + html.escape(item["link"], quote=True)
                    + "\" target=\"_blank\" rel=\"noopener noreferrer\">"
                    + html.escape(item["title"])
                    + "</a></div>\n"
                )

                if item["published"]:
                    f.write(
                        "      <div class=\"meta\">Published: "
                        + html.escape(item["published"])
                        + "</div>\n"
                    )

                if item["summary"]:
                    f.write(
                        "      <div class=\"summary\">"
                        + html.escape(item["summary"])
                        + "</div>\n"
                    )

                if item["source_url"]:
                    f.write(
                        "      <div class=\"meta\">Feed source: <a href=\""
                        + html.escape(item["source_url"], quote=True)
                        + "\" target=\"_blank\" rel=\"noopener noreferrer\">"
                        + html.escape(item["source_url"])
                        + "</a></div>\n"
                    )

                f.write("    </article>\n")

    f.write("    <div class=\"footer\">Source files: <a href=\"../business_intelligence_brief.md\">Markdown</a> | <a href=\"../business_intelligence_brief.csv\">CSV</a></div>\n")
    f.write("  </div>\n")
    f.write("</body>\n")
    f.write("</html>\n")

print(f"Found {len(new_items)} new posts")
