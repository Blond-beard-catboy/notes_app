import sqlite3
from datetime import datetime

DB_NAME = "notes.db"

def init_db():
    """Создаёт таблицу notes, если её нет"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_all_notes():
    """Возвращает список всех заметок (id, title)"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM notes ORDER BY created_at DESC")
        return cur.fetchall()

def get_note_by_id(note_id):
    """Возвращает (title, content) для заданного id или None"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT title, content FROM notes WHERE id=?", (note_id,))
        return cur.fetchone()

def add_note(title, content):
    """Добавляет новую заметку"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()

def update_note(note_id, title, content):
    """Обновляет существующую заметку"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))
        conn.commit()

def delete_note(note_id):
    """Удаляет заметку по id"""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()

def title_exists(title, exclude_id=None):
    """
    Проверяет, существует ли заметка с заданным заголовком.
    Если указан exclude_id, этот ID исключается из проверки (для обновления).
    Возвращает True, если заголовок уже занят, иначе False.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        if exclude_id is None:
            cur.execute("SELECT 1 FROM notes WHERE title = ?", (title,))
        else:
            cur.execute("SELECT 1 FROM notes WHERE title = ? AND id != ?", (title, exclude_id))
        return cur.fetchone() is not None