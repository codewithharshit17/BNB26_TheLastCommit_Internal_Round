import sqlite3
from pathlib import Path

DB_PATH = Path("relearn.db")
def connect():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.executescript("create table if not exists sessions (session_id text primary key); create table if not exists attempts (session text, item text, answer text, conf int, posterior text); create table if not exists misconception_state (session text, misconception text, state text, posterior_history text, evidence text);")
    return connection
