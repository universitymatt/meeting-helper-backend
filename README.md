# Meeting Helper System

This application is the backend for the meeting helper system<br><br>
It uses FastAPI to interact with an sqlite database through sqlalchemy

## To create the virtual environment

```bash
python -m venv .venv
```

## To activate the virtual environment

```bash
# windows
source .venv/scripts/activate
# macos/linux
source .venv/bin/activate
```

## To install the dependencies

```bash
pip install -r requirements.txt
```

## To run the application

```bash
uvicorn app.main:app --reload
```
