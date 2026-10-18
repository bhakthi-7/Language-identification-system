"""Tests for the FastAPI endpoints in api.py."""

import pytest
from fastapi.testclient import TestClient

import config
from api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_identify_english_success():
    response = client.post(
        "/identify", json={"text": "The weather is lovely today, so we decided to walk."}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "en" and body["language"] == "English"
    assert body["status"] == "ok"
    assert 0 < body["score"] <= 1


def test_identify_kannada_and_hindi():
    kn = client.post("/identify", json={"text": "ನಾನು ಬೆಂಗಳೂರಿನಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ ಮತ್ತು ಓದುತ್ತಿದ್ದೇನೆ."}).json()
    hi = client.post("/identify", json={"text": "मैं दिल्ली में रहता हूँ और पढ़ाई कर रहा हूँ।"}).json()
    assert kn["code"] == "kn"
    assert hi["code"] == "hi"


def test_identify_respects_top_n():
    response = client.post(
        "/identify", json={"text": "Je vis à Paris et j'étudie l'informatique.", "top_n": 2}
    )
    assert response.status_code == 200
    assert len(response.json()["candidates"]) <= 2


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_identify_empty_or_whitespace_returns_422(text):
    response = client.post("/identify", json={"text": text})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_identify_too_long_returns_422():
    response = client.post("/identify", json={"text": "a" * (config.MAX_INPUT_CHARS + 1)})
    assert response.status_code == 422


def test_identify_missing_field_returns_422():
    assert client.post("/identify", json={}).status_code == 422


def test_identify_invalid_top_n_returns_422():
    assert client.post("/identify", json={"text": "hello world", "top_n": 0}).status_code == 422


def test_identify_numeric_input_is_inconclusive_not_error():
    response = client.post("/identify", json={"text": "12345 67890"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "inconclusive" and body["language"] is None


def test_languages_endpoint():
    body = client.get("/languages").json()
    assert body["kn"] == "Kannada" and body["hi"] == "Hindi"


def test_docs_page_available():
    assert client.get("/docs").status_code == 200
