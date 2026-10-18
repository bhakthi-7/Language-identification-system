"""Reusable helper functions."""

import unicodedata


def count_letters(text: str) -> int:
    """Return the number of alphabetic characters (any script) in ``text``.

    Combining marks (e.g. Devanagari/Kannada vowel signs) are counted too,
    because they are an integral part of the written word in those scripts.
    """
    return sum(
        1 for ch in text if ch.isalpha() or unicodedata.category(ch).startswith("M")
    )


def normalize_text(text: str) -> str:
    """Normalise Unicode (NFC), strip control characters and collapse spaces."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(
        ch for ch in text if ch in "\n\t " or unicodedata.category(ch)[0] != "C"
    )
    return " ".join(text.split())


def truncate(text: str, length: int = 60) -> str:
    """Shorten ``text`` for display, adding an ellipsis when cut."""
    text = text.strip().replace("\n", " ")
    return text if len(text) <= length else text[: length - 1] + "…"


def load_samples(path=None) -> dict:
    """Load example texts from ``sample_data/samples.json`` ({name: text})."""
    import json
    from pathlib import Path

    target = Path(path) if path else Path(__file__).parent / "sample_data" / "samples.json"
    with open(target, encoding="utf-8") as handle:
        return json.load(handle)
