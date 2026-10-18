# Architecture

## Components

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit UI: input widgets, buttons, result card, history. Contains no detection logic. |
| `api.py` | FastAPI app: request/response schemas, HTTP error mapping. |
| `detector.py` | All detection logic: validation, normalisation, model call, reliability checks, result object. |
| `config.py` | Limits and thresholds, overridable by environment variables. |
| `utils.py` | Text helpers (letter counting, Unicode normalisation, truncation) and sample loader. |
| `sample_data/samples.json` | Example sentences used by the UI buttons. |

## Why Streamlit calls the detector directly

The brief allowed a separate backend only if it could be integrated cleanly. A Streamlit app that makes HTTP calls to a second server needs two processes running, a port, and error handling for "backend not reachable". For a single-user demo this adds fragility without benefit. Instead:

- `app.py` and `api.py` both import `detector.py`, so behaviour is identical.
- The API remains available for programmatic use and is tested separately.

## Data flow

```
text  ->  validate  ->  normalise  ->  count letters  ->  model  ->  checks  ->  result
```

1. **Validate** (`LanguageDetector.detect`): non-string, empty/whitespace-only and over-long text raise `InvalidInputError`.
2. **Normalise** (`utils.normalize_text`): Unicode NFC, control characters removed, whitespace collapsed.
3. **Count letters** (`utils.count_letters`): alphabetic characters plus combining marks. If fewer than `MIN_LETTERS` (default 2), the result is `inconclusive`. This catches numbers, punctuation and emoji-only input.
4. **Model call**: `py3langid` returns every language ranked by a normalised score.
5. **Checks**:
   - top label is the model's "no linguistic content" label, or top score is below `MIN_CONFIDENCE` (0.30) -> `inconclusive`, and no language is reported;
   - fewer than `SHORT_TEXT_LETTERS` (15) letters -> status `low_confidence` plus a warning;
   - a second Unicode script covering at least 10% of letters -> mixed-text warning.
6. **Result**: a `DetectionResult` dataclass (status, language, ISO code, score, script, letter count, top-N candidates, warnings).

## Error handling

| Situation | Streamlit | API |
|---|---|---|
| Empty / whitespace | Red error message | HTTP 422 with `detail` |
| Over 5000 characters | Red error message | HTTP 422 |
| No letters / low confidence | Yellow "Inconclusive" warning, candidates shown if available | HTTP 200, `status: "inconclusive"` |
| Very short text | Result plus warning | HTTP 200, `status: "low_confidence"` |

## Model loading

The model file is bundled inside the `py3langid` package, so no download step exists. `get_detector()` creates one shared detector (thread-safe, lazy). Streamlit additionally wraps it in `st.cache_resource`.
