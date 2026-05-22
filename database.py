
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(os.getenv("DATABASE_PATH", "database.db"))


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    try:
        yield connection
    finally:
        connection.close()


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS baby_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 12),
                weight REAL NOT NULL CHECK(weight > 0),
                height REAL NOT NULL CHECK(height > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def insert_data(name, age, weight, height):
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Baby name is required.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO baby_data(name, age, weight, height)
            VALUES (?, ?, ?, ?)
            """,
            (cleaned_name, int(age), float(weight), float(height)),
        )
        connection.commit()


def view_data():
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, name, age, weight, height
            FROM baby_data
            ORDER BY lower(name), age, id
            """
        )
        return cursor.fetchall()


def delete_baby_data(name):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM baby_data WHERE name = ?",
            (name,),
        )
        connection.commit()


init_db()

