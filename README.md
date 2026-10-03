# FitBuddy – AI Fitness Plan Generator using Gemini Models

Implementation based on the attached FitBuddy project document.

## Structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── schemas.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── static/
│   └── images/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Run on Windows

```powershell
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Gemini API key:

```text
GOOGLE_API_KEY=your_gemini_api_key_here
```

Then run:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The SQLite database `fitbuddy.db` is created automatically when the application starts.
