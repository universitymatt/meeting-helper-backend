# Meeting Helper System

This application is the backend for the meeting helper system

It uses FastAPI to interact with an sqlite database through sqlalchemy

# Tests

The tests cover all api endpoints by mocking out the responses from methods

Pydantic schema validation is tested for custom schema validation

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
# app dependencies
pip install -r requirements.txt
# dev dependencies
pip install -r requirements-dev.txt
```

## To run the application

```bash
uvicorn app.main:app --reload
```

## To seed the database

```bash
python -m app.db.seed_db
```

## To lint the code

```bash
pylint app/
```

## To run the tests

```bash
pytest
```
