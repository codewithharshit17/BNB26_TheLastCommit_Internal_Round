import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("RELEARN_DB_PATH", Path(__file__).resolve().parents[2] / "relearn.db"))

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript("""
        create table if not exists sessions (
            session_id text primary key, posterior text not null default '{}',
            current_item text, created_at text not null default current_timestamp
        );
        create table if not exists attempts (
            id integer primary key autoincrement, session text not null,
            item text not null, answer text not null, conf integer not null,
            posterior text not null, created_at text not null default current_timestamp
        );
        create table if not exists misconception_state (
            session text not null, misconception text not null, state text not null,
            posterior_history text not null, evidence text not null,
            primary key (session, misconception)
        );
    """)
    # Upgrade databases created by the original scaffold without discarding learner data.
    columns = {row["name"] for row in connection.execute("pragma table_info(sessions)")}
    if "posterior" not in columns:
        connection.execute("alter table sessions add column posterior text not null default '{}'")
    if "current_item" not in columns:
        connection.execute("alter table sessions add column current_item text")
    return connection
