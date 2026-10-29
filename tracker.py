#!/usr/bin/env python3
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".local/share/screentime/data.db"
POLL_SECONDS = 5
IDLE_THRESHOLD_MS = 120_000


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_time (
            date TEXT NOT NULL,
            app TEXT NOT NULL,
            seconds INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (date, app)
        )
        """
    )
    conn.commit()
    return conn


def get_idle_ms():
    try:
        out = subprocess.run(
            ["xprintidle"], capture_output=True, text=True, timeout=2, check=True
        )
        return int(out.stdout.strip())
    except Exception:
        return 0


def get_active_app():
    try:
        out = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowclassname"],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        )
        name = out.stdout.strip()
        return name or None
    except Exception:
        return None


def record(conn, app, seconds):
    today = datetime.now().strftime("%Y-%m-%d")
    conn.execute(
        """
        INSERT INTO app_time (date, app, seconds) VALUES (?, ?, ?)
        ON CONFLICT(date, app) DO UPDATE SET seconds = seconds + excluded.seconds
        """,
        (today, app, seconds),
    )
    conn.commit()


def main():
    conn = init_db()
    while True:
        time.sleep(POLL_SECONDS)
        if get_idle_ms() >= IDLE_THRESHOLD_MS:
            continue
        app = get_active_app()
        if app:
            record(conn, app, POLL_SECONDS)


if __name__ == "__main__":
    main()
