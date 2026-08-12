"""
LinAlgo Database Manager (SQLite)
Handles user accounts, authentication data, credit balances, and subscription plans.
"""

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'linalgo.db')


def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes database tables and migrates credit columns if missing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table with credits and subscription plan fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            credits INTEGER DEFAULT 50,
            plan_type TEXT DEFAULT 'free',
            is_unlimited INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Ensure columns exist if table was created earlier without them
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row['name'] for row in cursor.fetchall()]

    if 'credits' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 50")
    if 'plan_type' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN plan_type TEXT DEFAULT 'free'")
    if 'is_unlimited' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_unlimited INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


def create_user(username, email, password):
    """
    Creates a new user with 50 free starter credits.
    Returns (user_dict, None) on success, or (None, error_message) on failure.
    """
    username = username.strip()
    email = email.strip().lower()

    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long."

    if not email or '@' not in email:
        return None, "Please enter a valid email address."

    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, credits, plan_type, is_unlimited)
            VALUES (?, ?, ?, 50, 'free', 0)
        ''', (username, email, password_hash))
        conn.commit()

        user_id = cursor.lastrowid
        cursor.execute('SELECT id, username, email, credits, plan_type, is_unlimited, created_at FROM users WHERE id = ?', (user_id,))
        user = dict(cursor.fetchone())
        conn.close()
        return user, None
    except sqlite3.IntegrityError as e:
        conn.close()
        err_msg = str(e).lower()
        if 'username' in err_msg:
            return None, "Username is already taken. Please choose another."
        elif 'email' in err_msg:
            return None, "An account with this email already exists."
        return None, "Account creation failed. Username or Email already exists."
    except Exception as e:
        conn.close()
        return None, f"Database error: {str(e)}"


def get_user_by_username_or_email(identifier):
    """Fetches a user by username or email."""
    if not identifier:
        return None
    
    identifier = identifier.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE LOWER(username) = ? OR LOWER(email) = ?
    ''', (identifier, identifier))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_user_by_id(user_id):
    """Fetches a user by ID."""
    if not user_id:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, username, email, credits, plan_type, is_unlimited, created_at FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def verify_password(stored_password_hash, provided_password):
    """Verifies a password against the stored hash."""
    return check_password_hash(stored_password_hash, provided_password)


def deduct_credit(user_id):
    """
    Deducts 1 credit from the user's account for a calculation.
    Returns (success, remaining_credits, message).
    If user is_unlimited == 1, bypasses deduction.
    """
    user = get_user_by_id(user_id)
    if not user:
        return False, 0, "User not found."

    if user['is_unlimited'] == 1:
        return True, 'unlimited', "Lifetime Unlimited Plan Active."

    current_credits = user['credits'] or 0
    if current_credits <= 0:
        return False, 0, "Insufficient credits. Please top up your account."

    new_credits = current_credits - 1

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET credits = ? WHERE id = ?', (new_credits, user_id))
    conn.commit()
    conn.close()

    return True, new_credits, "1 credit deducted."


def add_credits_to_user(user_id, amount, plan_name='weekly'):
    """Adds credits to a user's balance and updates plan_type."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    current_credits = row['credits'] or 0
    new_credits = current_credits + amount

    cursor.execute('''
        UPDATE users
        SET credits = ?, plan_type = ?
        WHERE id = ?
    ''', (new_credits, plan_name, user_id))

    conn.commit()
    conn.close()

    return get_user_by_id(user_id)


def set_lifetime_unlimited_user(user_id):
    """Upgrades user to Lifetime Unlimited status (unlimited credits)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET is_unlimited = 1, plan_type = 'lifetime'
        WHERE id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()

    return get_user_by_id(user_id)


# Initialize DB and columns
init_db()
