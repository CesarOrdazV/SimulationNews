import gzip
import html
import re
import ssl
import urllib.request
import zlib

import feedparser


def fetch_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch with SSL bypass, explicit decompression, then parse with feedparser."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "feedparser/6.0 +https://feedparser.readthedocs.io/",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
                "Accept-Encoding": "gzip, deflate",
            },
        )
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
