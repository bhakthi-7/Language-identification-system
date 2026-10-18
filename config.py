"""Centralised configuration for the Language Identification System.

Values can be overridden with environment variables (see ``.env.example``).
"""

import os

APP_TITLE = "Language Identification System"
APP_SUBTITLE = "Detect the language of any text using Natural Language Processing"

# Input limits
MAX_INPUT_CHARS = int(os.getenv("LANGID_MAX_INPUT_CHARS", "5000"))

# Inputs with fewer letters than this are flagged as unreliable.
SHORT_TEXT_LETTERS = int(os.getenv("LANGID_SHORT_TEXT_LETTERS", "15"))

# Inputs with fewer letters than this are rejected as inconclusive.
MIN_LETTERS = int(os.getenv("LANGID_MIN_LETTERS", "2"))

# A top prediction below this confidence is reported as "inconclusive".
MIN_CONFIDENCE = float(os.getenv("LANGID_MIN_CONFIDENCE", "0.30"))

# Number of ranked candidates returned.
TOP_N = 3

# Session history size in the Streamlit UI.
HISTORY_LIMIT = 10

# API settings
API_HOST = os.getenv("LANGID_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("LANGID_API_PORT", "8000"))
