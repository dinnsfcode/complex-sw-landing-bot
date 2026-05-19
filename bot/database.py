import sqlite3
from datetime import datetime

from config import DB_PATH


conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        city TEXT,
        message TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operators (
        chat_id TEXT PRIMARY KEY
    )
    """)
    conn.commit()


def add_lead(name=None, phone=None, email=None, city=None, message=None):
    cursor.execute(
        """
        INSERT INTO leads (name, phone, email, city, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            clean(name),
            clean(phone),
            clean(email),
            clean(city),
            clean(message),
            datetime.now().strftime("%d.%m.%Y %H:%M"),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_leads(status=None):
    if status:
        cursor.execute(
            """
            SELECT id, name, phone, email, city, message, status, created_at
            FROM leads
            WHERE status = ?
            ORDER BY id DESC
            """,
            (status,),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, phone, email, city, message, status, created_at
            FROM leads
            ORDER BY id DESC
            """
        )

    return cursor.fetchall()


def get_lead(lead_id):
    cursor.execute(
        """
        SELECT id, name, phone, email, city, message, status, created_at
        FROM leads
        WHERE id = ?
        """,
        (lead_id,),
    )
    return cursor.fetchone()


def update_lead_status(lead_id, status):
    cursor.execute(
        "UPDATE leads SET status = ? WHERE id = ?",
        (status, lead_id),
    )
    conn.commit()


def add_operator(chat_id):
    cursor.execute(
        "INSERT OR IGNORE INTO operators (chat_id) VALUES (?)",
        (str(chat_id),),
    )
    conn.commit()


def get_operators():
    cursor.execute("SELECT chat_id FROM operators")
    return [row[0] for row in cursor.fetchall()]


def clean(value):
    if value is None:
        return ""
    return str(value).strip()
