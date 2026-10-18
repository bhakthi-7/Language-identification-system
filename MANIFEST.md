# Manifest

Every file in the archive and its purpose.

| File | Purpose |
|---|---|
| `.env.example` | Optional environment variables (placeholders only) |
| `.gitignore` | Files excluded from Git |
| `.streamlit/config.toml` | Streamlit theme and server settings |
| `GITHUB_SETUP.md` | Step-by-step GitHub publishing guide |
| `LICENSE` | MIT license (replace <YOUR NAME>) |
| `MANIFEST.md` | This file |
| `README.md` | Main project documentation |
| `api.py` | FastAPI REST API (/identify, /languages, /health) |
| `app.py` | Streamlit user interface |
| `config.py` | Centralised settings and thresholds |
| `detector.py` | Core language-detection logic, validation and result objects |
| `docs/architecture.md` | Architecture and data flow |
| `docs/project_report.md` | Academic project report |
| `docs/testing.md` | Test coverage and actual results |
| `pytest.ini` | pytest configuration |
| `requirements.txt` | Dependencies (runtime and testing) |
| `run.bat` | Launch helper for Windows |
| `run.sh` | Launch helper for Linux/macOS |
| `sample_data/samples.json` | Example sentences in 14 languages |
| `screenshots/README.md` | Explains why no screenshots are bundled and how to add them |
| `scripts/detect_cli.py` | Command-line language detector |
| `tests/test_api.py` | API tests |
| `tests/test_app.py` | Streamlit UI tests (headless) |
| `tests/test_cli.py` | CLI tests |
| `tests/test_detector.py` | Detector unit tests |
| `utils.py` | Text helpers and sample loader |
