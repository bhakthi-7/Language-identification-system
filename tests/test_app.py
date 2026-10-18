"""Headless tests of the Streamlit interface using streamlit.testing."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import config

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception
    return at


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def test_page_loads_with_title(app):
    assert any(config.APP_TITLE in t.value for t in app.title)


def test_empty_input_shows_error(app):
    _button(app, "Detect Language").click().run()
    assert any("enter some text" in e.value.lower() for e in app.error)


def test_example_button_fills_text_and_detects_kannada(app):
    _button(app, "Kannada").click().run()
    assert "ಬೆಂಗಳೂರಿನಲ್ಲಿ" in app.text_area[0].value
    _button(app, "Detect Language").click().run()
    assert any("Kannada" in m.value for m in app.markdown)
    assert not app.exception


def test_hindi_example_detects_hindi(app):
    _button(app, "Hindi").click().run()
    _button(app, "Detect Language").click().run()
    assert any("Hindi" in m.value for m in app.markdown)


def test_clear_button_resets_input(app):
    _button(app, "English").click().run()
    _button(app, "Clear").click().run()
    assert app.text_area[0].value == ""


def test_numeric_input_shows_inconclusive_warning(app):
    app.text_area[0].set_value("12345 67890").run()
    _button(app, "Detect Language").click().run()
    assert any("Inconclusive" in w.value for w in app.warning)
