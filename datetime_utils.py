import calendar
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MEXICO_TZ = ZoneInfo("America/Mexico_City")
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def now_mexico() -> datetime:
    return datetime.now(MEXICO_TZ)


def format_mexico_datetime(dt: datetime) -> str:
    return dt.astimezone(MEXICO_TZ).strftime(DATETIME_FORMAT)


def format_mexico_now() -> str:
    return format_mexico_datetime(now_mexico())


def format_entry_published(entry) -> str:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if not parsed:
            continue
        try:
            timestamp = calendar.timegm(parsed)
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return format_mexico_datetime(dt)
        except (ValueError, OverflowError, OSError):
            continue

    return getattr(entry, "published", "") or getattr(entry, "updated", "")
