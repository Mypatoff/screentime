#!/usr/bin/env python3
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from flask import Flask, render_template

DB_PATH = Path.home() / ".local/share/screentime/data.db"
MAX_SERIES = 8

app = Flask(__name__)


def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def format_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m"
    return f"{seconds}s" if seconds else "0m"


def build_bars(rows):
    total = sum(r["seconds"] for r in rows)
    entries = [{"app": r["app"], "seconds": r["seconds"]} for r in rows[:MAX_SERIES]]
    other_seconds = sum(r["seconds"] for r in rows[MAX_SERIES:])
    if other_seconds:
        entries.append({"app": "Other", "seconds": other_seconds})

    max_seconds = max((e["seconds"] for e in entries), default=1)
    bars = [
        {
            "app": e["app"],
            "label": format_duration(e["seconds"]),
            "exact": format_duration(e["seconds"]),
            "pct": round(e["seconds"] / max_seconds * 100, 1) if max_seconds else 0,
        }
        for e in entries
    ]
    return bars, total


@app.route("/")
def today():
    today_str = date.today().isoformat()
    rows = query(
        "SELECT app, seconds FROM app_time WHERE date = ? ORDER BY seconds DESC",
        (today_str,),
    )
    bars, total = build_bars(rows)
    return render_template(
        "dashboard.html",
        title="Today",
        bars=bars,
        total_label=format_duration(total),
        active="today",
    )


@app.route("/week")
def week():
    start = (date.today() - timedelta(days=6)).isoformat()
    rows = query(
        """
        SELECT app, SUM(seconds) AS seconds FROM app_time
        WHERE date >= ?
        GROUP BY app
        ORDER BY seconds DESC
        """,
        (start,),
    )
    bars, total = build_bars(rows)
    return render_template(
        "dashboard.html",
        title="Last 7 days",
        bars=bars,
        total_label=format_duration(total),
        active="week",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
