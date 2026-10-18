@echo off
REM Launch helper for Windows.
REM   run.bat        -> Streamlit web app  (http://localhost:8501)
REM   run.bat api    -> FastAPI server     (http://localhost:8000/docs)
REM   run.bat test   -> run the test suite
cd /d "%~dp0"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
  call .venv\Scripts\python.exe -m pip install --upgrade pip
  call .venv\Scripts\python.exe -m pip install -r requirements.txt
)

if /I "%1"=="api" (
  .venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
) else if /I "%1"=="test" (
  .venv\Scripts\python.exe -m pytest
) else (
  .venv\Scripts\python.exe -m streamlit run app.py
)
