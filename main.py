from pathlib import Path
import os
import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))
DB_PATH = Path(os.getenv('DB_PATH', str(Path(__file__).with_name('tasks.db'))))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='Daylist API')
CORS_ORIGINS = [origin.strip().rstrip('/') for origin in os.getenv(
    'CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
).split(',') if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=['*'], allow_headers=['*'])

@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    try:
        connection.row_factory = sqlite3.Row
        with connection:
            yield connection
    finally:
        connection.close()

with database() as db:
    db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL)')

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    completed: bool | None = None

class Reorder(BaseModel):
    ids: list[int]

def serialize(row):
    return {**dict(row), 'completed': bool(row['completed'])}

def clean_title(title):
    title = title.strip()
    if not title:
        raise HTTPException(422, 'Task title cannot be blank')
    return title

@app.get('/api/tasks')
def list_tasks():
    with database() as db:
        return [serialize(row) for row in db.execute('SELECT * FROM tasks ORDER BY position, id')]

@app.post('/api/tasks', status_code=201)
def create_task(task: TaskCreate):
    title = clean_title(task.title)
    with database() as db:
        cursor = db.execute('INSERT INTO tasks (title, position) VALUES (?, (SELECT COALESCE(MAX(position), -1) + 1 FROM tasks))', (title,))
        return serialize(db.execute('SELECT * FROM tasks WHERE id = ?', (cursor.lastrowid,)).fetchone())

@app.put('/api/tasks/reorder')
def reorder_tasks(order: Reorder):
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        existing = {row['id'] for row in db.execute('SELECT id FROM tasks')}
        if len(order.ids) != len(existing) or set(order.ids) != existing:
            raise HTTPException(409, 'Task list changed. Refresh and try again.')
        db.executemany('UPDATE tasks SET position = ? WHERE id = ?', enumerate(order.ids))
    return {'ok': True}

@app.patch('/api/tasks/{task_id}')
def update_task(task_id: int, task: TaskUpdate):
    with database() as db:
        if db.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone() is None:
            raise HTTPException(404, 'Task not found')
        if task.title is not None:
            db.execute('UPDATE tasks SET title = ? WHERE id = ?', (clean_title(task.title), task_id))
        if task.completed is not None:
            db.execute('UPDATE tasks SET completed = ? WHERE id = ?', (task.completed, task_id))
        return serialize(db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone())

@app.delete('/api/tasks/{task_id}', status_code=204)
def delete_task(task_id: int):
    with database() as db:
        if db.execute('DELETE FROM tasks WHERE id = ?', (task_id,)).rowcount == 0:
            raise HTTPException(404, 'Task not found')
