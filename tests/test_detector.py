"""Tests for detector.py (core language-identification logic)."""

import pytest

import config
from detector import (
    STATUS_INCONCLUSIVE,
    STATUS_LOW_CONFIDENCE,
    STATUS_OK,
    InvalidInputError,
    LanguageDetector,
    detect_language,
    dominant_script,
    language_name,
)

# Representative full sentences: (expected ISO code, expected name, text)
SENTENCES = [
    ("en", "English", "The weather is lovely today, so we decided to walk to the market."),
    ("kn", "Kannada", "ನಾನು ಬೆಂಗಳೂರಿನಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ ಮತ್ತು ಕಂಪ್ಯೂಟರ್ ವಿಜ್ಞಾನವನ್ನು ಓದುತ್ತಿದ್ದೇನೆ."),
    ("hi", "Hindi", "मैं दिल्ली में रहता हूँ और कंप्यूटर विज्ञान की पढ़ाई कर रहा हूँ।"),
    ("ta", "Tamil", "நான் சென்னையில் வசிக்கிறேன், கணினி அறிவியல் படிக்கிறேன்."),
    ("te", "Telugu", "నేను హైదరాబాద్‌లో నివసిస్తున్నాను మరియు కంప్యూటర్ సైన్స్ చదువుతున్నాను."),
    ("ml", "Malayalam", "ഞാൻ കൊച്ചിയിൽ താമസിക്കുന്നു, കമ്പ്യൂട്ടർ സയൻസ് പഠിക്കുന്നു."),
    ("fr", "French", "Je vis à Paris et j'étudie l'informatique à l'université."),
    ("de", "German", "Ich wohne in Berlin und studiere Informatik an der Universität."),
    ("es", "Spanish", "Vivo en Madrid y estudio informática en la universidad."),
    ("bn", "Bengali", "আমি কলকাতায় থাকি এবং কম্পিউটার বিজ্ঞান পড়ি।"),
    ("gu", "Gujarati", "હું અમદાવાદમાં રહું છું અને કમ્પ્યુટર વિજ્ઞાન ભણું છું."),
    ("pa", "Punjabi", "ਮੈਂ ਅੰਮ੍ਰਿਤਸਰ ਵਿੱਚ ਰਹਿੰਦਾ ਹਾਂ ਅਤੇ ਕੰਪਿਊਟਰ ਵਿਗਿਆਨ ਪੜ੍ਹਦਾ ਹਾਂ।"),
    ("ur", "Urdu", "میں کراچی میں رہتا ہوں اور کمپیوٹر سائنس پڑھتا ہوں۔"),
]


@pytest.fixture(scope="module")
def detector():
    return LanguageDetector()


def test_english(detector):
    result = detector.detect(SENTENCES[0][2])
    assert (result.code, result.language, result.status) == ("en", "English", STATUS_OK)
    assert result.script == "Latin"


def test_kannada(detector):
    result = detector.detect(SENTENCES[1][2])
    assert (result.code, result.language) == ("kn", "Kannada")
    assert result.script == "Kannada"


def test_hindi(detector):
    result = detector.detect(SENTENCES[2][2])
    assert (result.code, result.language) == ("hi", "Hindi")
    assert result.script == "Devanagari"


@pytest.mark.parametrize("code,name,text", SENTENCES)
def test_all_representative_sentences(detector, code, name, text):
    """Covers English, Kannada, Hindi and 9+ additional languages."""
    result = detector.detect(text)
    assert result.code == code
    assert result.language == name
    assert 0.0 < result.score <= 1.0


def test_top_candidates_are_ranked_and_limited(detector):
    result = detector.detect(SENTENCES[0][2], top_n=3)
    assert 1 <= len(result.candidates) <= 3
    scores = [c.score for c in result.candidates]
    assert scores == sorted(scores, reverse=True)
    assert result.candidates[0].code == result.code


def test_empty_input_raises(detector):
    with pytest.raises(InvalidInputError):
        detector.detect("")


@pytest.mark.parametrize("text", [" ", "   \n\t  ", "\n\n"])
def test_whitespace_only_raises(detector, text):
    with pytest.raises(InvalidInputError):
        detector.detect(text)


def test_non_string_raises(detector):
    with pytest.raises(InvalidInputError):
        detector.detect(None)  # type: ignore[arg-type]


def test_too_long_input_raises(detector):
    with pytest.raises(InvalidInputError):
        detector.detect("a" * (config.MAX_INPUT_CHARS + 1))


@pytest.mark.parametrize("text", ["12345 67890", "3.14159", "2026"])
def test_numeric_only_is_inconclusive(detector, text):
    result = detector.detect(text)
    assert result.status == STATUS_INCONCLUSIVE
    assert result.language is None and result.code is None


@pytest.mark.parametrize("text", ["!!!", "?!., ;:", "---***---", "😀😀😀"])
def test_punctuation_and_emoji_only_is_inconclusive(detector, text):
    result = detector.detect(text)
    assert result.status == STATUS_INCONCLUSIVE
    assert result.language is None
    assert result.warnings


def test_very_short_ambiguous_text_is_never_presented_as_confident(detector):
    """A short ambiguous word must be inconclusive or carry a warning."""
    result = detector.detect("ok")
    assert result.status in (STATUS_INCONCLUSIVE, STATUS_LOW_CONFIDENCE)
    assert result.warnings


def test_short_non_latin_word_gets_low_reliability_warning(detector):
    result = detector.detect("ನಮಸ್ಕಾರ")
    assert result.status == STATUS_LOW_CONFIDENCE
    assert any("short" in w.lower() for w in result.warnings)


def test_inconclusive_result_does_not_invent_a_language(detector):
    result = detector.detect("hello")
    if result.status == STATUS_INCONCLUSIVE:
        assert result.language is None and result.score is None


def test_unicode_with_punctuation_numbers_and_emoji(detector):
    text = "ನಾನು ಬೆಂಗಳೂರಿನಲ್ಲಿ 2026 ರಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ!!! 😀 ಮತ್ತು ಓದುತ್ತಿದ್ದೇನೆ."
    result = detector.detect(text)
    assert result.code == "kn"


def test_multiple_sentences(detector):
    text = ("I went to the market this morning. The vegetables were fresh. "
            "Afterwards I met a friend and we had some tea together.")
    assert detector.detect(text).code == "en"


def test_extra_whitespace_and_newlines_are_handled(detector):
    text = "\n\n   The   weather   is   lovely   today,\n so we decided to walk.   \n"
    assert detector.detect(text).code == "en"


def test_mixed_script_text_triggers_warning(detector):
    result = detector.detect("I really love ಬೆಂಗಳೂರು and ಕರ್ನಾಟಕ very much indeed")
    assert any("mix" in w.lower() for w in result.warnings)


def test_dominant_script_helper():
    assert dominant_script("hello") == "Latin"
    assert dominant_script("ನಮಸ್ಕಾರ") == "Kannada"
    assert dominant_script("नमस्ते") == "Devanagari"
    assert dominant_script("1234") is None


def test_language_name_fallback():
    assert language_name("kn") == "Kannada"
    assert language_name("qq") == "qq"


def test_supported_languages_include_required_ones(detector):
    supported = detector.supported_languages()
    for code in ("en", "kn", "hi", "ta", "te", "ml", "mr", "bn", "gu", "pa", "ur", "fr", "de", "es"):
        assert code in supported


def test_module_level_helper_and_to_dict():
    data = detect_language(SENTENCES[0][2]).to_dict()
    assert data["code"] == "en"
    assert isinstance(data["candidates"], list)
