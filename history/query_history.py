import sqlite3
import os
from datetime import datetime

HISTORY_DB_PATH = os.path.join(os.path.dirname(__file__), "query_history.db")


def init_history_db():
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question    TEXT NOT NULL,
            sql         TEXT NOT NULL,
            answer      TEXT NOT NULL,
            timestamp   TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_to_history(question: str, sql: str, answer: str):
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO query_history (question, sql, answer, timestamp) VALUES (?, ?, ?, ?)",
        (question, sql, answer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 10) -> list:
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, sql, answer, timestamp FROM query_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"question": row[0], "sql": row[1], "answer": row[2], "timestamp": row[3]}
        for row in rows
    ]
