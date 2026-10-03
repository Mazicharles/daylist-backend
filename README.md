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

API routes: `GET/POST /api/tasks`, `PATCH/DELETE /api/tasks/{id}`, and `PUT /api/tasks/reorder`. Reordering accepts `{"ids": [2, 1]}` containing every current task ID exactly once.

## Hosting preparation (not deployed)

For a Python hosting service, use `pip install -r requirements.txt` as the build command and `python start.py` as the start command. The included `Procfile` declares the same command. The startup script binds Uvicorn to `0.0.0.0` and reads the platform's `PORT` variable (default `8000`), with one worker for this SQLite application. Existing requirements already include FastAPI, the Uvicorn ASGI server, and python-dotenv.

Set `CORS_ORIGINS` to the public frontend's exact HTTPS origin. Set `DB_PATH` to a writable file on a persistent disk, such as `/data/tasks.db`. The database, its parent directories, and the tasks table are created automatically. Without `DB_PATH`, local behavior is unchanged. Use one application instance with its SQLite disk; an ephemeral filesystem can lose tasks on restart or redeployment.

A Dockerfile is also included. It runs as a non-root user, defaults SQLite to `/data/tasks.db`, and copies only application source and requirements. Local databases, secrets, caches, and virtual environments are excluded from the Docker build context. To test locally with Docker installed:

```sh
docker build -t daylist-backend .
docker volume create daylist-data
docker run --rm -p 8000:8000 -v daylist-data:/data -e CORS_ORIGINS=http://127.0.0.1:5173 daylist-backend
```

The hosting platform may override `PORT`; ensure any attached disk is writable by container user UID `10001`. SQLite files remain excluded from Git. This preparation does not deploy the service or add authentication; anyone with access to a future public API can modify its shared tasks.
