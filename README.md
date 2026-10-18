# Language Identification System

> **Language Identification System Using Natural Language Processing**: paste text, get the language.

A beginner-friendly Python project that detects which language a piece of text is written in. It has a Streamlit web interface, an optional FastAPI REST API, a pretrained NLP model and an automated pytest suite. It supports English, Kannada (ಕನ್ನಡ), Hindi (हिन्दी) and many more.

---

## Table of contents

1. [Overview](#overview)
2. [Objectives](#objectives)
3. [Features](#features)
4. [Technology stack](#technology-stack)
5. [How language identification works](#how-language-identification-works)
6. [Architecture and workflow](#architecture-and-workflow)
7. [Supported languages and limitations](#supported-languages-and-limitations)
8. [Project structure](#project-structure)
9. [Prerequisites](#prerequisites)
10. [Installation: Windows](#installation-windows)
11. [Installation: Linux / macOS](#installation-linux--macos)
12. [Running the application](#running-the-application)
13. [API usage](#api-usage)
14. [Sample input and output](#sample-input-and-output)
15. [Running the tests](#running-the-tests)
16. [Troubleshooting](#troubleshooting)
17. [Screenshots](#screenshots)
18. [Future enhancements](#future-enhancements)
19. [Credits and license](#credits-and-license)

## Overview

**Problem statement.** Text arrives in many languages, and software that processes it (translation, search, moderation, routing) first needs to know which language it is dealing with. This project accepts text from a user and identifies its language, without assuming the input is English, Kannada or Hindi.

## Objectives

- Build an application that identifies the language of user-supplied text.
- Reuse a pretrained language-identification model instead of training one from scratch.
- Handle Unicode scripts (Kannada, Devanagari and others), and be honest about uncertain results.
- Provide a clean UI, a REST API, automated tests and complete documentation.

## Features

- Large text area, example buttons (English, Kannada, Hindi), a selector for more languages, **Detect Language** and **Clear** buttons.
- Language name, ISO 639 code, detected script and a model confidence score.
- Top three candidate languages with scores.
- Input validation: empty, whitespace-only and over-long input (default limit 5000 characters).
- Graceful handling of numbers-only, punctuation-only, emoji-only, very short and mixed-script text.
- Per-session detection history.
- Optional REST API with interactive docs at `/docs`.
- 62 automated tests.

## Technology stack

| Purpose | Technology |
|---|---|
| Language | Python (developed and tested on 3.12; intended for 3.11+) |
| NLP model | [py3langid](https://pypi.org/project/py3langid/), a Python 3 port of *langid.py* with a bundled pretrained model |
| Frontend | [Streamlit](https://streamlit.io) |
| API | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn |
| Testing | pytest (+ httpx for API tests) |
| Docs | Markdown |

**Why not Lingua?** Lingua was the first library considered, but its current release (2.2.0, 75 languages) does not include **Kannada** or Malayalam, and Kannada is a core requirement. `py3langid` supports both, ships its model inside the package (no separate download) and installs with a single `pip` command.

## How language identification works

`py3langid` uses a **multinomial naive Bayes classifier** trained on labelled documents in many languages (the model bundled with the tested version, 0.4.0, can output 142 labels). Text is converted into a sparse vector of byte n-gram features (sequences of 1 to 4 bytes). The classifier scores every language and the highest-scoring one is the prediction. The scores are turned into a distribution with a softmax, which is what this project shows as the "model confidence score".

> **Important:** that score reflects how strongly the model prefers one language over the others. It is **not a calibrated probability**, and the application labels it accordingly.

Around the model, `detector.py` adds:

1. validation (empty / whitespace / too long),
2. Unicode normalisation and control-character removal,
3. letter counting, so inputs with no letters are reported as inconclusive,
4. an *inconclusive* result when the top score is below a threshold (default 0.30),
5. warnings for very short or mixed-script text.

## Architecture and workflow

```
          +-------------------+        +------------------+
 User --> | Streamlit (app.py)| -----> |                  |
          +-------------------+        |   detector.py    | --> py3langid model
 Client-> | FastAPI  (api.py) | -----> |  (shared logic)  |
          +-------------------+        +------------------+
```

**Design decision:** the Streamlit app imports `detector.py` directly instead of calling the API over HTTP. This keeps the demo to a single process and removes a failure point (a second server that must be running). The FastAPI service wraps the *same* detector, so both interfaces behave identically. Details are in [docs/architecture.md](docs/architecture.md).

## Supported languages and limitations

The model can output 142 labels. All of the following were checked with real sentences in the test suite:

English, Kannada, Hindi, Tamil, Telugu, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Urdu, French, German, Spanish.

The model can also output many others (for example Arabic, Russian, Japanese, Chinese, Korean, Portuguese, Italian, Dutch and Thai). These were **not** individually tested. The full list is returned by `GET /languages`.

**Known limitations**

- **Short text is unreliable.** A single word may be misclassified, for example the Hindi word "नमस्ते" is reported as Sanskrit in testing. The UI shows a warning for short inputs, and the app reports *inconclusive* when confidence is very low.
- **Mixed-language text** yields one language only. In testing, an English sentence containing one Kannada word was reported as Kannada with a high score, because the model gives weight to rarer script features. Do not treat the result as "the dominant language".
- **Romanised text** (e.g. Hindi typed in Latin letters) is not reliably supported.
- **Closely related languages** (Hindi/Marathi/Nepali, Spanish/Galician, etc.) can be confused, mostly on short text.
- Results are not benchmarked here; no accuracy percentage is claimed.

## Project structure

```
language-identification-system/
├── app.py                 Streamlit user interface
├── detector.py            Language detection logic (core)
├── api.py                 FastAPI REST API
├── config.py              Central configuration
├── utils.py               Helper functions
├── requirements.txt       Dependencies (runtime + test)
├── pytest.ini             pytest configuration
├── run.sh / run.bat       Launch helpers (Linux/macOS, Windows)
├── .env.example           Optional configuration variables
├── .gitignore
├── LICENSE
├── MANIFEST.md            List of every file in the archive
├── GITHUB_SETUP.md        Step-by-step GitHub guide
├── .streamlit/config.toml Streamlit theme
├── sample_data/samples.json   Example sentences in 14 languages
├── scripts/detect_cli.py      Command-line detector
├── screenshots/               Placeholder (see its README)
├── docs/
│   ├── project_report.md
│   ├── architecture.md
│   └── testing.md
└── tests/
    ├── test_detector.py
    ├── test_api.py
    ├── test_app.py
    └── test_cli.py
```

## Prerequisites

- Python 3.11 or newer (3.12 was used for development)
- `pip` and the `venv` module
- Internet access once, to install the dependencies
- A modern web browser

## Installation: Windows

```bat
cd language-identification-system
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process RemoteSigned` first.

## Installation: Linux / macOS

```bash
cd language-identification-system
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the application

With the virtual environment active:

```bash
streamlit run app.py            # web interface  -> http://localhost:8501
uvicorn api:app --reload        # REST API       -> http://localhost:8000/docs
python scripts/detect_cli.py "Bonjour tout le monde"   # command line
```

Or use the helpers, which create the environment on first run: `./run.sh` (Linux/macOS) or `run.bat` (Windows). Add `api` or `test` as an argument to start the API or run the tests.

## API usage

`POST /identify`

```bash
curl -X POST http://127.0.0.1:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"text": "मैं दिल्ली में रहता हूँ और कंप्यूटर विज्ञान की पढ़ाई कर रहा हूँ।"}'
```

Response (actual output from a test run):

```json
{
  "status": "ok",
  "language": "Hindi",
  "code": "hi",
  "score": 0.9948,
  "script": "Devanagari",
  "letter_count": 51,
  "candidates": [
    {"code": "hi", "language": "Hindi", "score": 0.9948},
    {"code": "ne", "language": "Nepali", "score": 0.0037},
    {"code": "mr", "language": "Marathi", "score": 0.0009}
  ],
  "warnings": []
}
```

| Endpoint | Description |
|---|---|
| `POST /identify` | Body: `{"text": "...", "top_n": 3}`. Returns 422 for empty, whitespace-only or over-long text. |
| `GET /languages` | Map of language codes to names. |
| `GET /health` | Liveness check. |
| `GET /docs` | Interactive Swagger documentation. |

`status` is `ok`, `low_confidence` (very short text) or `inconclusive` (no language returned; `language` and `code` are `null`).

## Sample input and output

Scores below were produced by running the code in this repository (`sample_data/samples.json`).

| Input | Detected | Code | Score |
|---|---|---|---|
| Artificial intelligence is changing the way we learn, work and communicate every day. | English | en | 0.9952 |
| ನಾನು ಬೆಂಗಳೂರಿನಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ ಮತ್ತು ಕಂಪ್ಯೂಟರ್ ವಿಜ್ಞಾನವನ್ನು ಓದುತ್ತಿದ್ದೇನೆ. | Kannada | kn | 1.0000 |
| मैं दिल्ली में रहता हूँ और कंप्यूटर विज्ञान की पढ़ाई कर रहा हूँ। | Hindi | hi | 0.9948 |
| `12345 67890` | Inconclusive (no letters) | n/a | n/a |

## Running the tests

```bash
pytest
```

Last recorded run (Python 3.12.3, pytest 9.1.1): **62 passed**. See [docs/testing.md](docs/testing.md).

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt`. |
| `streamlit` not recognised | Use `python -m streamlit run app.py`. |
| `./run.sh`: permission denied | Run `bash run.sh` or `chmod +x run.sh`. |
| Port 8501 or 8000 is busy | Add `--server.port 8502` (Streamlit) or `--port 8001` (Uvicorn). |
| Kannada/Hindi shows as boxes | Install a font with Kannada/Devanagari support (e.g. Noto Sans Kannada / Noto Sans Devanagari), or use an up-to-date browser. |
| Tests fail with an `httpx` error | Reinstall with `pip install -r requirements.txt`. |
| Garbled characters in a Windows terminal | Run `chcp 65001` or use the web interface. |
| "Inconclusive" for a short text | Enter a full sentence; short inputs are inherently ambiguous. |

## Screenshots

No screenshots are bundled because the build environment had no browser. See [screenshots/README.md](screenshots/README.md) for how to add your own.

## Future enhancements

- Per-sentence detection of mixed-language text.
- Romanised Indic text (transliteration) support.
- CSV/file batch upload with a downloadable report.
- Calibrated confidence and a benchmark against a labelled dataset.
- Docker packaging.

## Credits and license

- [py3langid](https://github.com/adbar/py3langid) by Adrien Barbaresi, derived from [langid.py](https://github.com/saffsd/langid.py) by Marco Lui and Timothy Baldwin.
- [Streamlit](https://streamlit.io), [FastAPI](https://fastapi.tiangolo.com), [pytest](https://pytest.org).

Released under the [MIT License](LICENSE). Replace `<YOUR NAME>` in the license with your name. After publishing, the repository will be at `https://github.com/<your-username>/language-identification-system`.
