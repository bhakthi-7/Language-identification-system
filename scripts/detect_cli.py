"""Command-line helper: identify the language of text.

Usage:
    python scripts/detect_cli.py "Some text to analyse"
    echo "Some text" | python scripts/detect_cli.py
"""

import sys
from pathlib import Path

# Allow running from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from detector import InvalidInputError, detect_language  # noqa: E402


def main() -> int:
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    try:
        result = detect_language(text)
    except InvalidInputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if result.language is None:
        print("Inconclusive: no language could be identified reliably.")
    else:
        print(f"{result.language} ({result.code})  score={result.score:.4f}")
    for candidate in result.candidates:
        print(f"  {candidate.language:<22} {candidate.code:<5} {candidate.score:.4f}")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
