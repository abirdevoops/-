import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "truthlens.db"

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence REAL NOT NULL,
            ai_probability REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        # First registered user can be promoted manually through the database.
        # For a demo, admin bootstrap uses ADMIN_EMAIL environment variable.
        import os
        admin_email = os.getenv("TRUTHLENS_ADMIN_EMAIL","").strip().lower()
        if admin_email:
            c.execute("UPDATE users SET is_admin=1 WHERE email=?", (admin_email,))

def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180000).hex()

def register_user(name, email, password):
    name, email = name.strip(), email.strip().lower()
    if not name or not email:
        return False, "Name and email are required."
    if "@" not in email:
        return False, "Please enter a valid email."
    salt = secrets.token_hex(16)
    ph = _hash(password, salt)
    try:
        with conn() as c:
            c.execute("INSERT INTO users(name,email,password_hash,salt,created_at) VALUES(?,?,?,?,?)",
                      (name,email,ph,salt,datetime.utcnow().isoformat()))
        return True, "Account created successfully. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "This email is already registered."

def authenticate_user(email, password):
    email = email.strip().lower()
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row:
        return None
    if secrets.compare_digest(_hash(password,row["salt"]),row["password_hash"]):
        return dict(row)
    return None

def get_user(user_id):
    with conn() as c:
        row = c.execute("SELECT id,name,email,is_admin,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None

def is_admin(user_id):
    u=get_user(user_id)
    return bool(u and u["is_admin"])

def save_scan(user_id, filename, result, confidence, ai_probability):
    with conn() as c:
        c.execute("""INSERT INTO scans(user_id,filename,result,confidence,ai_probability,created_at)
                     VALUES(?,?,?,?,?,?)""",
                  (user_id,filename,result,float(confidence),float(ai_probability),datetime.utcnow().isoformat()))

def get_stats():
    with conn() as c:
        users=c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        scans=c.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        ai=c.execute("SELECT COUNT(*) FROM scans WHERE result='LIKELY AI-GENERATED'").fetchone()[0]
    return {"users":users,"scans":scans,"ai_flagged":ai}

def get_recent_users(limit=50):
    with conn() as c:
        rows=c.execute("""SELECT id,name,email,is_admin,created_at FROM users
                          ORDER BY id DESC LIMIT ?""",(limit,)).fetchall()
    import pandas as pd
    return pd.DataFrame([dict(r) for r in rows])

def get_recent_scans(user_id=None, limit=50):
    with conn() as c:
        if user_id:
            rows=c.execute("""SELECT filename,result,confidence,ai_probability,created_at
                              FROM scans WHERE user_id=? ORDER BY id DESC LIMIT ?""",(user_id,limit)).fetchall()
        else:
            rows=c.execute("""SELECT s.id,u.email,s.filename,s.result,s.confidence,s.ai_probability,s.created_at
                              FROM scans s JOIN users u ON u.id=s.user_id
                              ORDER BY s.id DESC LIMIT ?""",(limit,)).fetchall()
    import pandas as pd
    return pd.DataFrame([dict(r) for r in rows])

def delete_user(user_id):
    with conn() as c:
        c.execute("DELETE FROM scans WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM users WHERE id=?", (user_id,))

def set_user_admin(user_id, value=True):
    with conn() as c:
        c.execute("UPDATE users SET is_admin=? WHERE id=?", (1 if value else 0,user_id))
