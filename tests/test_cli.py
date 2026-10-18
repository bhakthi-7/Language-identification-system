"""Tests for scripts/detect_cli.py."""

import subprocess
import sys
from pathlib import Path

CLI = str(Path(__file__).resolve().parent.parent / "scripts" / "detect_cli.py")


def _run(*args):
    return subprocess.run(
        [sys.executable, CLI, *args],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )


def test_cli_detects_hindi():
    proc = _run("मैं दिल्ली में रहता हूँ और कंप्यूटर विज्ञान की पढ़ाई कर रहा हूँ।")
    assert proc.returncode == 0
    assert "Hindi (hi)" in proc.stdout


def test_cli_rejects_blank_input():
    proc = _run("   ")
    assert proc.returncode == 1
    assert "Error" in proc.stderr
