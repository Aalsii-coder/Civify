import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE = Path(__file__).with_name("civify.db")


def connect():
    return sqlite3.connect(DATABASE)


def create_table():
    with connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                decision TEXT NOT NULL,
                notes TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


def save_review(case_id, reviewer, decision, notes):
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with connect() as connection:
        connection.execute(
            """INSERT INTO reviews (case_id, reviewer, decision, notes, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (case_id, reviewer, decision, notes, timestamp),
        )


def get_reviews():
    with connect() as connection:
        rows = connection.execute(
            """SELECT case_id, reviewer, decision, notes, timestamp
               FROM reviews ORDER BY id DESC"""
        ).fetchall()
    columns = ["Case ID", "Reviewer", "Decision", "Notes", "Timestamp"]
    return [dict(zip(columns, row)) for row in rows]
