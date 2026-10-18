# Testing

## How to run

```bash
pip install -r requirements.txt
pytest
```

## Actual results

Run in the build environment: Python 3.12.3, pytest 9.1.1, py3langid 0.4.0, streamlit 1.66.0, fastapi 0.143.5.

```
62 passed, 1 warning
```

The single warning comes from Starlette's test client and says that `httpx` usage is deprecated in favour of `httpx2`. It does not affect results.

| File | Tests | Scope |
|---|---|---|
| `tests/test_detector.py` | 41 | Detection logic |
| `tests/test_api.py` | 13 | REST API |
| `tests/test_app.py` | 6 | Streamlit UI, run headlessly with `streamlit.testing.v1.AppTest` |
| `tests/test_cli.py` | 2 | Command-line helper |

## Coverage of the required cases

| Required case | Where |
|---|---|
| English / Kannada / Hindi | `test_english`, `test_kannada`, `test_hindi` |
| 3+ additional languages | `test_all_representative_sentences` covers Tamil, Telugu, Malayalam, French, German, Spanish, Bengali, Gujarati, Punjabi, Urdu |
| Empty input | `test_empty_input_raises`, API 422 test |
| Whitespace-only | `test_whitespace_only_raises` |
| Numeric-only | `test_numeric_only_is_inconclusive` |
| Punctuation-only | `test_punctuation_and_emoji_only_is_inconclusive` |
| Very short / ambiguous | `test_very_short_ambiguous_text_is_never_presented_as_confident`, `test_short_non_latin_word_gets_low_reliability_warning` |
| Unicode handling | `test_unicode_with_punctuation_numbers_and_emoji`, script tests |
| Inconclusive detection | `test_inconclusive_result_does_not_invent_a_language` |
| API success and validation | `tests/test_api.py` |

## Design notes

- Tests use full sentences. Very short words are only tested for the *behaviour* (warning or inconclusive), never for a specific language, because such predictions are unreliable.
- `test_inconclusive_result_does_not_invent_a_language` is conditional by design: it checks that **if** "hello" is inconclusive, no language is returned.

## What is not covered

- No accuracy benchmark on a labelled corpus. The tests show correct behaviour on chosen examples, not a measured accuracy rate.
- Only the 14 languages listed in the README were tested individually.
- Visual rendering of fonts in a real browser was not tested (no browser was available).
- The `.bat` launcher was not executed (no Windows environment). `run.sh` was syntax-checked only.
