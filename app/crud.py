"""CRUD operations for persisted email analyses."""

import json
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from app.database import get_connection


def _row_to_dict(row: Any) -> dict[str, Any]:
    record = dict(row)
    record["needs_reply"] = bool(record["needs_reply"])
    record["tags"] = json.loads(record["tags"])
    return record


def save_email_analysis(subject: str, body: str, analysis: dict) -> int:
    """Persist an analyzed email and return the new database id."""
    created_at = datetime.now(timezone.utc).isoformat()
    tags_json = json.dumps(analysis.get("tags", []), ensure_ascii=False)

    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO email_analyses (
                created_at,
                subject,
                body,
                category,
                priority,
                client_name,
                company,
                summary,
                budget,
                deadline,
                needs_reply,
                reply_draft,
                tags,
                recommended_action
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                subject,
                body,
                analysis["category"],
                analysis["priority"],
                analysis.get("client_name"),
                analysis.get("company"),
                analysis["summary"],
                analysis.get("budget"),
                analysis.get("deadline"),
                int(analysis["needs_reply"]),
                analysis["reply_draft"],
                tags_json,
                analysis["recommended_action"],
            ),
        )
        connection.commit()
        analysis_id = cursor.lastrowid

    if analysis_id is None:
        raise RuntimeError("SQLite did not return an id for the saved analysis.")
    return analysis_id


def get_email_history(limit: int = 10) -> list[dict]:
    """Return the latest email analyses ordered from newest to oldest."""
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT * FROM email_analyses ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_email_analysis_by_id(analysis_id: int) -> dict | None:
    """Return one email analysis, or None when it does not exist."""
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM email_analyses WHERE id = ?",
            (analysis_id,),
        ).fetchone()
    return _row_to_dict(row) if row is not None else None

