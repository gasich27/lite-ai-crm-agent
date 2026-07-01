"""SQLite connection and schema initialization helpers."""

import sqlite3
from contextlib import closing


DB_PATH = "email_agent.db"


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection configured to return named rows."""
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the email analysis table when it does not exist."""
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                client_name TEXT NULL,
                company TEXT NULL,
                summary TEXT NOT NULL,
                budget TEXT NULL,
                deadline TEXT NULL,
                needs_reply INTEGER NOT NULL,
                reply_draft TEXT NOT NULL,
                tags TEXT NOT NULL,
                recommended_action TEXT NOT NULL
            )
            """
        )
        connection.commit()
