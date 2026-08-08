import sqlite3
import os
from datetime import datetime
from config import Config

class Database:
    """SQLite Database manager for saving email history."""

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    hr_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    status TEXT NOT NULL,
                    resume_filename TEXT,
                    error_message TEXT,
                    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_email(self, company_name: str, role: str, hr_email: str, subject: str, status: str = 'sent', resume_filename: str = None, error_message: str = None) -> int:
        """Insert email log record into database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emails (company_name, role, hr_email, subject, status, resume_filename, error_message, sent_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name,
                role,
                hr_email,
                subject,
                status,
                resume_filename,
                error_message,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return cursor.lastrowid

    def get_email_history(self) -> list:
        """Fetch all email history records as a list of dicts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, company_name, role, hr_email, subject, status, resume_filename, error_message, sent_date
                FROM emails
                ORDER BY id DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
