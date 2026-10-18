# GitHub Setup Guide

Replace `<your-username>` with your GitHub username everywhere below.

**Suggested repository description:** *Language identification web app and REST API (English, Kannada, Hindi and 100+ more) built with Python, Streamlit, FastAPI and py3langid.*

**Suggested topics:** `language-identification`, `language-detection`, `nlp`, `natural-language-processing`, `python`, `streamlit`, `fastapi`, `pytest`, `kannada`, `hindi`, `multilingual`

## 1. Extract the ZIP

- **Windows:** right-click `language-identification-system.zip` -> *Extract All...*
- **Linux/macOS:** `unzip language-identification-system.zip`

## 2. Open in VS Code

```bash
cd language-identification-system
code .
```

(or *File -> Open Folder...* in VS Code).

## 3. Create and activate a virtual environment

Windows (Command Prompt):
```bat
python -m venv .venv
.venv\Scripts\activate
```
Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
In VS Code, choose the `.venv` interpreter via *Ctrl+Shift+P -> Python: Select Interpreter*.

## 4. Install the dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Run the application

```bash
streamlit run app.py
```
Open http://localhost:8501. For the API: `uvicorn api:app --reload` and open http://localhost:8000/docs.

## 6. Run the tests

```bash
pytest
```

## 7. Initialise Git

```bash
git init
git branch -M main
```
If Git asks who you are:
```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

## 8. Commit the files

```bash
git add .
git status          # check that .venv/ and __pycache__/ are NOT listed
git commit -m "Initial commit: Language Identification System"
```

## 9. Create a GitHub repository

1. Sign in at https://github.com and click **New repository**.
2. Name: `language-identification-system`. Add the description above. Choose **Public**.
3. Do **not** tick "Add a README", ".gitignore" or "license" (the project already has them).
4. Click **Create repository**, then add the topics under *About -> settings*.

## 10. Push the project

```bash
git remote add origin https://github.com/<your-username>/language-identification-system.git
git push -u origin main
```
GitHub no longer accepts account passwords for pushes. Sign in through the browser prompt, use GitHub Desktop, or create a Personal Access Token and use it as the password.

## 11. Update the README with the final repository URL

Edit the last line of `README.md` (or add a "Repository" line) so it reads:

```
https://github.com/<your-username>/language-identification-system
```
Also replace `<YOUR NAME>` in `LICENSE`. Then:

```bash
git add README.md LICENSE
git commit -m "Update README and license with repository details"
git push
```
