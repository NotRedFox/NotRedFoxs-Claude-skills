# notesapp

A small notes service. Users register, log in, write notes and search their own notes.

Run it with `python -m app.server 8000`. Run the tests with `python -m pytest`.

## Architecture

| Path | What it does |
|---|---|
| `app/auth.py` | Registers users, checks passwords, issues login tokens |
| `app/notes.py` | Stores notes per user |
| `app/search.py` | Searches a user's notes |
| `app/server.py` | HTTP JSON API: `POST /register`, `POST /login`, `POST /notes`, `GET /notes`, `GET /search?q=` |

Passwords are case-sensitive. Each note has a unique id.
