"""
Database access layer for TicketFlow.
Uses SQLite for persistent storage of user credentials and classified tickets.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "tickets.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high performance concurrency
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password with PBKDF2-HMAC-SHA256 and a 16-byte random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return key, salt


def verify_password(stored_hash: str, salt: str, password_attempt: str) -> bool:
    """Verifies a password against the stored PBKDF2 hash."""
    test_hash, _ = hash_password(password_attempt, salt)
    return test_hash == stored_hash


def init_db():
    """Initializes tables and seeds default user and initial demo tickets if empty."""
    os.makedirs(DB_DIR, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_email TEXT NOT NULL,
                complaint TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                department TEXT NOT NULL
            );
        """)

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_timestamp ON tickets(timestamp);")

        conn.commit()

        # Seed default demo user if no users exist
        cursor.execute("SELECT COUNT(*) as cnt FROM users;")
        if cursor.fetchone()["cnt"] == 0:
            seed_hash, seed_salt = hash_password("demo123")
            cursor.execute(
                "INSERT INTO users (email, password_hash, salt, full_name, created_at) VALUES (?, ?, ?, ?, ?);",
                ("demo@ticketflow.io", seed_hash, seed_salt, "Alex Demo", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()

        # Seed initial tickets if database is empty so dashboard is informative out of the box
        cursor.execute("SELECT COUNT(*) as cnt FROM tickets;")
        if cursor.fetchone()["cnt"] == 0:
            sample_seeds = [
                ("TCK-101", "2026-10-12 10:15:22", "demo@ticketflow.io", "The database connection keeps timing out and crashing server on login.", "Technical", "High", "Technical Support"),
                ("TCK-102", "2026-10-12 11:42:05", "demo@ticketflow.io", "I was charged twice on my credit card this month and need an urgent refund.", "Billing", "High", "Billing Support"),
                ("TCK-103", "2026-10-12 14:20:11", "demo@ticketflow.io", "Cannot reset password because verification email is not received.", "Account", "Medium", "Account Support"),
                ("TCK-104", "2026-10-13 09:05:44", "demo@ticketflow.io", "How can I update my team's display name and preferred time zone?", "Service", "Low", "Customer Service"),
            ]
            cursor.executemany(
                "INSERT INTO tickets (ticket_id, timestamp, user_email, complaint, category, priority, department) VALUES (?, ?, ?, ?, ?, ?, ?);",
                sample_seeds
            )
            conn.commit()


def register_user(email: str, password: str, full_name: str = "User") -> Tuple[bool, str]:
    """Registers a new user into SQLite."""
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    pwd_hash, salt = hash_password(password)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password_hash, salt, full_name, created_at) VALUES (?, ?, ?, ?, ?);",
                (clean_email, pwd_hash, salt, full_name.strip() or "User", now_str)
            )
            conn.commit()
            return True, "Account registered successfully! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def authenticate_user(email: str, password: str) -> Tuple[bool, Any]:
    """Validates user credentials against SQLite."""
    clean_email = email.strip().lower()
    if not clean_email or not password:
        return False, "Please enter both email and password."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?;", (clean_email,))
            user = cursor.fetchone()

            if not user:
                return False, "No account found with this email."

            if verify_password(user["password_hash"], user["salt"], password):
                return True, {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "created_at": user["created_at"]
                }
            else:
                return False, "Incorrect password."
    except Exception as e:
        return False, f"Authentication error: {str(e)}"


def get_next_ticket_id() -> str:
    """Generates the next sequential ticket ID (e.g. TCK-105)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tickets ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        next_num = (row["id"] + 101) if row else 101
        return f"TCK-{next_num}"


def add_ticket(
    ticket_id: str,
    user_email: str,
    complaint: str,
    category: str,
    priority: str,
    department: str
) -> bool:
    """Inserts a newly classified ticket into SQLite."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tickets (ticket_id, timestamp, user_email, complaint, category, priority, department)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (ticket_id, now_str, user_email, complaint.strip(), category, priority, department)
            )
            conn.commit()
            return True
    except Exception:
        return False


def get_tickets(
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Retrieves tickets from SQLite with optional filtering and search."""
    query = "SELECT * FROM tickets WHERE 1=1"
    params: List[Any] = []

    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)

    if search_query and search_query.strip():
        term = f"%{search_query.strip().lower()}%"
        query += " AND (LOWER(ticket_id) LIKE ? OR LOWER(complaint) LIKE ? OR LOWER(department) LIKE ?)"
        params.extend([term, term, term])

    query += " ORDER BY id DESC"

    if limit and limit > 0:
        query += f" LIMIT {int(limit)}"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_metrics() -> Dict[str, int]:
    """Calculates ticket count metrics directly in SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN priority = 'Medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN priority = 'Low' THEN 1 ELSE 0 END) as low
            FROM tickets;
        """)
        row = cursor.fetchone()
        return {
            "total": row["total"] or 0,
            "high": row["high"] or 0,
            "medium": row["medium"] or 0,
            "low": row["low"] or 0
        }


# Automatically run schema migration on module load
init_db()
