from config import KEYWORDS


def is_relevant(text: str) -> bool:
    text = (text or "").lower()
    return any(keyword in text for keyword in KEYWORDS)
