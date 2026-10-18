"""Language detection logic.

This module wraps the pretrained ``py3langid`` model (a maintained Python 3
port of the *langid.py* naive-Bayes language identifier) and adds input
validation, reliability checks and human-readable output.

The model is bundled inside the ``py3langid`` package, so no separate model
download is required.
"""

from __future__ import annotations

import threading
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from py3langid.langid import MODEL_FILE, LanguageIdentifier

import config
from utils import count_letters, normalize_text

# Pseudo-label used by the model for text with no linguistic content.
NO_LANGUAGE_CODE = "zxx"

# ISO 639 code -> English language name for every label the model can emit.
# Two-letter codes are ISO 639-1; three-letter codes are ISO 639-2/3.
LANGUAGE_NAMES: Dict[str, str] = {
    "ace": "Acehnese", "af": "Afrikaans", "am": "Amharic", "an": "Aragonese",
    "ar": "Arabic", "ary": "Moroccan Arabic", "arz": "Egyptian Arabic",
    "as": "Assamese", "az": "Azerbaijani", "ba": "Bashkir",
    "bcl": "Central Bikol", "be": "Belarusian", "bg": "Bulgarian",
    "bn": "Bengali", "br": "Breton", "bs": "Bosnian", "ca": "Catalan",
    "crh": "Crimean Tatar", "cs": "Czech", "cy": "Welsh", "da": "Danish",
    "de": "German", "dz": "Dzongkha", "el": "Greek", "en": "English",
    "eo": "Esperanto", "es": "Spanish", "et": "Estonian", "eu": "Basque",
    "ext": "Extremaduran", "fa": "Persian", "fi": "Finnish", "fo": "Faroese",
    "fr": "French", "fuv": "Nigerian Fulfulde", "fy": "Western Frisian",
    "ga": "Irish", "gcf": "Guadeloupean Creole", "gcr": "Guianese Creole",
    "gd": "Scottish Gaelic", "gl": "Galician", "gom": "Goan Konkani",
    "grc": "Ancient Greek", "gu": "Gujarati", "gug": "Paraguayan Guarani",
    "guw": "Gun", "ha": "Hausa", "hbo": "Ancient Hebrew", "he": "Hebrew",
    "hi": "Hindi", "hr": "Croatian", "ht": "Haitian Creole", "hu": "Hungarian",
    "hy": "Armenian", "id": "Indonesian", "ig": "Igbo", "is": "Icelandic",
    "it": "Italian", "ja": "Japanese", "jv": "Javanese", "ka": "Georgian",
    "kab": "Kabyle", "kik": "Kikuyu", "kk": "Kazakh", "km": "Khmer",
    "kn": "Kannada", "ko": "Korean", "ku": "Kurdish", "ky": "Kyrgyz",
    "la": "Latin", "lb": "Luxembourgish", "lg": "Ganda", "lij": "Ligurian",
    "ln": "Lingala", "lo": "Lao", "lt": "Lithuanian", "ltg": "Latgalian",
    "lv": "Latvian", "mg": "Malagasy", "mk": "Macedonian", "ml": "Malayalam",
    "mn": "Mongolian", "mr": "Marathi", "ms": "Malay", "mt": "Maltese",
    "my": "Burmese", "ne": "Nepali", "nl": "Dutch", "nn": "Norwegian Nynorsk",
    "no": "Norwegian", "nso": "Northern Sotho", "oc": "Occitan", "om": "Oromo",
    "or": "Odia", "pa": "Punjabi", "pcm": "Nigerian Pidgin", "pl": "Polish",
    "ps": "Pashto", "pt": "Portuguese", "qu": "Quechua", "ro": "Romanian",
    "ru": "Russian", "rw": "Kinyarwanda", "sa": "Sanskrit",
    "sdh": "Southern Kurdish", "se": "Northern Sami", "si": "Sinhala",
    "sk": "Slovak", "sl": "Slovenian", "sn": "Shona", "so": "Somali",
    "sq": "Albanian", "sr": "Serbian", "st": "Southern Sotho", "sv": "Swedish",
    "sw": "Swahili", "ta": "Tamil", "te": "Telugu", "tg": "Tajik", "th": "Thai",
    "tk": "Turkmen", "tl": "Tagalog", "tr": "Turkish", "tt": "Tatar",
    "ug": "Uyghur", "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek",
    "uzs": "Southern Uzbek", "vec": "Venetian", "vi": "Vietnamese",
    "vo": "Volapuk", "wa": "Walloon", "wuu": "Wu Chinese", "xh": "Xhosa",
    "yo": "Yoruba", "yue": "Cantonese", "zh": "Chinese", "zu": "Zulu",
}

# Status values returned in ``DetectionResult.status``.
STATUS_OK = "ok"
STATUS_LOW_CONFIDENCE = "low_confidence"
STATUS_INCONCLUSIVE = "inconclusive"


class InvalidInputError(ValueError):
    """Raised when the input text cannot be processed (empty or too long)."""


@dataclass
class Candidate:
    """One ranked language prediction."""

    code: str
    language: str
    score: float


@dataclass
class DetectionResult:
    """Outcome of a detection request.

    ``language`` and ``code`` are ``None`` when ``status`` is ``inconclusive``.
    ``score`` is the model's normalised score for the top candidate. It is
    *not* a calibrated probability.
    """

    status: str
    language: Optional[str] = None
    code: Optional[str] = None
    score: Optional[float] = None
    script: Optional[str] = None
    letter_count: int = 0
    candidates: List[Candidate] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


def language_name(code: str) -> str:
    """Return a readable name for an ISO 639 ``code`` (code itself if unknown)."""
    return LANGUAGE_NAMES.get(code, code)


def dominant_script(text: str) -> Optional[str]:
    """Return the most common Unicode script among letters in ``text``.

    The script is the first word of the Unicode character name, e.g.
    ``KANNADA``, ``DEVANAGARI`` or ``LATIN``. Returns ``None`` if no letters.
    """
    counts: Dict[str, int] = {}
    for ch in text:
        if not ch.isalpha():
            continue
        try:
            script = unicodedata.name(ch).split()[0]
        except ValueError:
            continue
        counts[script] = counts.get(script, 0) + 1
    if not counts:
        return None
    return max(counts, key=counts.get).title()


class LanguageDetector:
    """Detects the language of text with validation and reliability checks."""

    def __init__(self) -> None:
        self._identifier = LanguageIdentifier.from_model_file(
            MODEL_FILE, norm_probs=True
        )

    @staticmethod
    def supported_languages() -> Dict[str, str]:
        """Return a ``{code: name}`` mapping of detectable languages."""
        return {c: n for c, n in sorted(LANGUAGE_NAMES.items(), key=lambda i: i[1])}

    def detect(self, text: str, top_n: int = config.TOP_N) -> DetectionResult:
        """Identify the language of ``text``.

        Raises:
            InvalidInputError: if the text is not a string, is empty or only
                whitespace, or exceeds ``config.MAX_INPUT_CHARS``.
        """
        if not isinstance(text, str):
            raise InvalidInputError("Input must be text.")
        if not text.strip():
            raise InvalidInputError("Please enter some text to analyse.")
        if len(text) > config.MAX_INPUT_CHARS:
            raise InvalidInputError(
                f"Text is too long ({len(text)} characters). "
                f"The maximum is {config.MAX_INPUT_CHARS}."
            )

        cleaned = normalize_text(text)
        letters = count_letters(cleaned)
        script = dominant_script(cleaned)

        if letters < config.MIN_LETTERS:
            return DetectionResult(
                status=STATUS_INCONCLUSIVE,
                script=script,
                letter_count=letters,
                warnings=[
                    "The text contains no (or almost no) letters, for example only "
                    "numbers, punctuation or emojis, so no language can be identified."
                ],
            )

        ranked = self._identifier.rank(cleaned)
        candidates = [
            Candidate(code=c, language=language_name(c), score=round(float(p), 4))
            for c, p in ranked
            if c != NO_LANGUAGE_CODE
        ][: max(1, top_n)]

        best_code_overall = ranked[0][0]
        best = candidates[0]

        if best_code_overall == NO_LANGUAGE_CODE or best.score < config.MIN_CONFIDENCE:
            return DetectionResult(
                status=STATUS_INCONCLUSIVE,
                script=script,
                letter_count=letters,
                candidates=candidates,
                warnings=[
                    "The language could not be determined reliably. "
                    "Try a longer, complete sentence."
                ],
            )

        warnings: List[str] = []
        status = STATUS_OK
        if letters < config.SHORT_TEXT_LETTERS:
            status = STATUS_LOW_CONFIDENCE
            warnings.append(
                "Very short input: the result may be unreliable. "
                "Use a full sentence for better accuracy."
            )
        if self._looks_mixed_script(cleaned):
            warnings.append(
                "The text appears to mix scripts or languages. "
                "Only one language is reported, and it may not be the one "
                "you consider dominant."
            )

        return DetectionResult(
            status=status,
            language=best.language,
            code=best.code,
            score=best.score,
            script=script,
            letter_count=letters,
            candidates=candidates,
            warnings=warnings,
        )

    @staticmethod
    def _looks_mixed_script(text: str) -> bool:
        """True if a second script makes up a noticeable share of the letters."""
        counts: Dict[str, int] = {}
        for ch in text:
            if ch.isalpha():
                try:
                    key = unicodedata.name(ch).split()[0]
                except ValueError:
                    continue
                counts[key] = counts.get(key, 0) + 1
        total = sum(counts.values())
        if len(counts) < 2 or total == 0:
            return False
        second = sorted(counts.values(), reverse=True)[1]
        return second / total >= 0.10


_detector: Optional[LanguageDetector] = None
_lock = threading.Lock()


def get_detector() -> LanguageDetector:
    """Return a process-wide shared detector (the model loads only once)."""
    global _detector
    if _detector is None:
        with _lock:
            if _detector is None:
                _detector = LanguageDetector()
    return _detector


def detect_language(text: str, top_n: int = config.TOP_N) -> DetectionResult:
    """Convenience wrapper around the shared detector."""
    return get_detector().detect(text, top_n=top_n)
