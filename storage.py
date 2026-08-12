import json

from config import DATA_DIR, LATEST_BY_TOPIC_FILE, SEEN_FILE


def load_seen() -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text(encoding="utf-8-sig"))
    return {}


def save_seen(data: dict) -> None:
    SEEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_latest_by_topic() -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    if LATEST_BY_TOPIC_FILE.exists():
        return json.loads(LATEST_BY_TOPIC_FILE.read_text(encoding="utf-8-sig"))
    return {}


def save_latest_by_topic(data: dict) -> None:
    LATEST_BY_TOPIC_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
