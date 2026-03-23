# database.py
# This file sets up the SQLite database for our project
# Creates tables for users and predictions

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            is_admin   INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # create predictions table to store user prediction history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            annual_salary  REAL,
            other_income   REAL,
            investments    REAL,
            deductions     REAL,
            age            INTEGER,
            predicted_tax  REAL,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # add default admin user if not already there
    existing = cursor.execute("SELECT id FROM users WHERE email = 'admin@tax.com'").fetchone()
    if not existing:
        cursor.execute(
            "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
            ('admin@tax.com', generate_password_hash('admin123'), 1)
        )
        print("Admin user created: admin@tax.com / admin123")

    conn.commit()
    conn.close()
    print("Database ready:", DB_PATH)


if __name__ == '__main__':
    init_db()
