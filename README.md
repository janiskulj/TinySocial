# TinySocial

TinySocial is a simple social media website built with Flask and TinyDB.

## Features

- Create short text posts with a name and message
- View the latest posts first on a shared feed
- Persist posts in a TinyDB database file

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Run tests

```bash
python -m unittest discover -s tests -v
```
