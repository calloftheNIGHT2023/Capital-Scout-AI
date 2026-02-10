import re
from typing import Dict
from .schemas import MessagePack


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _has_emoji(text: str) -> bool:
    # Simple ASCII check to keep outputs emoji-free
    for ch in text:
        if ord(ch) > 126:
            return True
    return False


def _has_buzzwords(text: str, buzzwords) -> bool:
    lower = text.lower()
    return any(b in lower for b in buzzwords)


def validate_message_pack(pack: MessagePack, settings: Dict) -> None:
    # Enforce required keys, word limits, and banned buzzwords
    required = [
        "subject_A",
        "body_A",
        "subject_B",
        "body_B",
        "followup_1",
        "followup_2",
    ]
    for key in required:
        if not getattr(pack, key):
            raise ValueError(f"Missing value for {key}")

    word_limit = int(settings.get("word_limit", 120))
    buzzwords = settings.get("buzzwords", [])

    if _word_count(pack.body_A) > word_limit:
        raise ValueError("body_A exceeds word limit")
    if _word_count(pack.body_B) > word_limit:
        raise ValueError("body_B exceeds word limit")

    all_text = " ".join(
        [
            pack.subject_A,
            pack.body_A,
            pack.subject_B,
            pack.body_B,
            pack.followup_1,
            pack.followup_2,
        ]
    )

    if _has_emoji(all_text):
        raise ValueError("Emoji detected")
    if _has_buzzwords(all_text, buzzwords):
        raise ValueError("Buzzword detected")
