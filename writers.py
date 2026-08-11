import csv
import html

from config import PAGES_DIR, SECTIONS


def write_csv(items: list[dict], path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "section",
                "topic",
                "title",
                "summary",
                "published",
                "link",
                "source_url",
            ],
        )
        writer.writeheader()
        writer.writerows(items)


def write_markdown(items: list[dict], generated_at: str, path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write("# Industrial Automation Business Intelligence Brief\n\n")
        file.write(f"Generated: {generated_at}\n\n")

        if not items:
            file.write("No new relevant articles found.\n")
            return

        for section_key, section_title in SECTIONS:
            section_items = [item for item in items if item["section"] == section_key]
            file.write(f"## {section_title}\n\n")

            if not section_items:
                file.write("No new relevant articles found.\n\n")
                continue

            current_topic = None

            for item in section_items:
                if item["topic"] != current_topic:
                    current_topic = item["topic"]
                    file.write(f"### {current_topic}\n\n")

                file.write(
                    f"- [{item['title']}]({item['link']})"
                    f" ({item['published']})\n"
                )

                if item["summary"]:
                    file.write(f"  Summary: {item['summary']}\n")

                if item["source_url"]:
                    file.write(f"  Feed source: {item['source_url']}\n")

            file.write("\n")


def write_html(items: list[dict], generated_at: str, path) -> None:
    PAGES_DIR.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write("<!doctype html>\n")
        file.write("<html lang=\"en\">\n")
        file.write("<head>\n")
        file.write("  <meta charset=\"utf-8\">\n")
        file.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n")
        file.write("  <title>Industrial Automation Business Intelligence Brief</title>\n")
        file.write("  <style>\n")
        file.write("    :root { color-scheme: dark; }\n")
        file.write("    body { font-family: Segoe UI, Tahoma, sans-serif; margin: 0; background: radial-gradient(circle at 20% 0%, #1e2f4f 0%, #101827 45%, #0a111e 100%); color: #eaf2ff; }\n")
        file.write("    .wrap { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }\n")
        file.write("    .hero { background: linear-gradient(120deg, #274777, #3d6aa5); color: #f6fbff; border: 1px solid #5f87bc; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(8, 14, 24, 0.35); }\n")
        file.write("    h1 { margin: 0 0 8px; font-size: 1.8rem; }\n")
        file.write("    h2 { margin-top: 28px; border-bottom: 2px solid #2c3e5c; padding-bottom: 6px; color: #d9e7ff; }\n")
        file.write("    h3 { margin-top: 20px; color: #b8cef4; }\n")
        file.write("    .card { background: rgba(22, 33, 54, 0.82); border: 1px solid #314767; border-radius: 12px; padding: 14px; margin-bottom: 12px; backdrop-filter: blur(2px); }\n")
        file.write("    .meta { color: #9fb3d6; font-size: 0.92rem; margin: 6px 0 10px; }\n")
        file.write("    a { color: #7ec8ff; text-decoration: none; }\n")
        file.write("    a:hover { color: #a8dcff; text-decoration: underline; }\n")
        file.write("    .summary { line-height: 1.45; margin: 8px 0; color: #e5edfa; }\n")
        file.write("    .footer { margin-top: 28px; font-size: 0.9rem; color: #9ab2d8; }\n")
        file.write("  </style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("  <div class=\"wrap\">\n")
        file.write("    <div class=\"hero\">\n")
        file.write("      <h1>Industrial Automation Business Intelligence Brief</h1>\n")
        file.write(f"      <div>Generated (UTC): {html.escape(generated_at)}</div>\n")
        file.write("    </div>\n")

        if not items:
            file.write("    <p>No new relevant articles found.</p>\n")
        else:
            for section_key, section_title in SECTIONS:
                section_items = [item for item in items if item["section"] == section_key]
                file.write(f"    <h2>{html.escape(section_title)}</h2>\n")

                if not section_items:
                    file.write("    <p>No new relevant articles found.</p>\n")
                    continue

                current_topic = None

                for item in section_items:
                    if item["topic"] != current_topic:
                        current_topic = item["topic"]
                        file.write(f"    <h3>{html.escape(current_topic)}</h3>\n")

                    file.write("    <article class=\"card\">\n")
                    file.write(
                        "      <div><a href=\""
                        + html.escape(item["link"], quote=True)
                        + "\" target=\"_blank\" rel=\"noopener noreferrer\">"
                        + html.escape(item["title"])
                        + "</a></div>\n"
                    )

                    if item["published"]:
                        file.write(
                            "      <div class=\"meta\">Published: "
                            + html.escape(item["published"])
                            + "</div>\n"
                        )

                    if item["summary"]:
                        file.write(
                            "      <div class=\"summary\">"
                            + html.escape(item["summary"])
                            + "</div>\n"
                        )

                    if item["source_url"]:
                        file.write(
                            "      <div class=\"meta\">Feed source: <a href=\""
                            + html.escape(item["source_url"], quote=True)
                            + "\" target=\"_blank\" rel=\"noopener noreferrer\">"
                            + html.escape(item["source_url"])
                            + "</a></div>\n"
                        )

                    file.write("    </article>\n")

        file.write("    <div class=\"footer\">Source files: <a href=\"../business_intelligence_brief.md\">Markdown</a> | <a href=\"../business_intelligence_brief.csv\">CSV</a></div>\n")
        file.write("  </div>\n")
        file.write("</body>\n")
        file.write("</html>\n")
