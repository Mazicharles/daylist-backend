# Daylist backend

The Daylist FastAPI service, prepared as a standalone `daylist-backend` repository. SQLite persists tasks and their order locally. It supports creating, editing, completing, deleting, listing, and reordering tasks for the matching `daylist-frontend` application.

## Install and run

Use Python 3.10 or newer. From this repository folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

On macOS/Linux, use `.venv/bin/python` instead of `.\.venv\Scripts\python`, and `cp .env.example .env` to copy the configuration.

The API runs at http://127.0.0.1:8000. Interactive API documentation is at http://127.0.0.1:8000/docs. Run the frontend separately on port 5173 with `VITE_API_URL=http://127.0.0.1:8000`.

## CORS configuration

Set `CORS_ORIGINS` in `.env` to a comma-separated list of allowed frontend origins, for example `http://127.0.0.1:5173,http://localhost:5173`. Use full origins including scheme and port, with no path. The local origins above are defaults when the variable is unset. For a future production environment, explicitly set the frontend's HTTPS origin instead. An explicitly empty value allows no cross-origin access. System environment variables take precedence over `.env`. Restart the server after changes.

## SQLite and tests

`tasks.db` is created beside `main.py` on first startup and persists between runs. Database files and local environment files are ignored by Git. This prepared copy starts with an empty database; the original project's database remains untouched. This is a local single-user application without authentication.

```powershell
.\.venv\Scripts\python -m unittest -v
```

Tests use isolated temporary SQLite databases to check task operations, persistence, ordering, and invalid requests.

API routes: `GET/POST /api/tasks`, `PATCH/DELETE /api/tasks/{id}`, and `PUT /api/tasks/reorder`. Reordering accepts `{"ids": [2, 1]}` containing every current task ID exactly once. No deployment is configured.
