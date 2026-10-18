#!/usr/bin/env bash
# Launch helper for Linux/macOS.
#   ./run.sh        -> Streamlit web app  (http://localhost:8501)
#   ./run.sh api    -> FastAPI server     (http://localhost:8000/docs)
#   ./run.sh test   -> run the test suite
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

case "${1:-app}" in
  api)  .venv/bin/python -m uvicorn api:app --host 127.0.0.1 --port 8000 ;;
  test) .venv/bin/python -m pytest ;;
  *)    .venv/bin/python -m streamlit run app.py ;;
esac
