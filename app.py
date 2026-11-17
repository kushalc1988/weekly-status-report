from datetime import date, timedelta
from pathlib import Path
import sqlite3

from flask import Flask, abort, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "weekly_status.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-local-app-secret"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_date TEXT NOT NULL,
                category TEXT NOT NULL,
                reference TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT '',
                hours REAL NOT NULL DEFAULT 0,
                team TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS weekly_notes (
                week_start TEXT PRIMARY KEY,
                achievements TEXT NOT NULL DEFAULT '',
                not_achieved TEXT NOT NULL DEFAULT '',
                measures TEXT NOT NULL DEFAULT '',
                risks TEXT NOT NULL DEFAULT '',
                followups TEXT NOT NULL DEFAULT '',
                deployment_plan TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def get_week_dates(week_value):
    """Return Monday, Sunday, and normalized YYYY-Www value for an ISO week."""
    try:
        year_text, week_text = week_value.split("-W")
        monday = date.fromisocalendar(int(year_text), int(week_text), 1)
    except (ValueError, TypeError):
        today = date.today()
        monday = today - timedelta(days=today.weekday())

    sunday = monday + timedelta(days=6)
    normalized_week = f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}"
    return monday, sunday, normalized_week


@app.get("/")
def index():
    monday, sunday, week_value = get_week_dates(
        request.args.get("week", date.today().strftime("%G-W%V"))
    )

    with get_db() as db:
        items = db.execute(
            """
            SELECT * FROM work_items
            WHERE work_date BETWEEN ? AND ?
            ORDER BY work_date DESC, id DESC
            """,
            (monday.isoformat(), sunday.isoformat()),
        ).fetchall()

        notes = db.execute(
            "SELECT * FROM weekly_notes WHERE week_start = ?",
            (monday.isoformat(),),
        ).fetchone()

    categories = ["Incident", "RITM", "Task", "Other"]
    statuses = ["Completed", "In Progress", "Blocked", "Pending"]

    category_counts = {
        category: sum(1 for item in items if item["category"] == category)
        for category in categories
    }
    status_counts = {
        status: sum(1 for item in items if item["status"] == status)
        for status in statuses
    }

    return render_template(
        "index.html",
        items=items,
        notes=notes,
        week_value=week_value,
        monday=monday,
        sunday=sunday,
        categories=categories,
        statuses=statuses,
        category_counts=category_counts,
        status_counts=status_counts,
        total_hours=sum(item["hours"] for item in items),
    )


@app.post("/entries")
def create_entry():
    work_date = request.form.get("work_date", "").strip()
    category = request.form.get("category", "").strip()
    reference = request.form.get("reference", "").strip()
    title = request.form.get("title", "").strip()
    details = request.form.get("details", "").strip()
    status = request.form.get("status", "").strip()
    priority = request.form.get("priority", "").strip()
    team = request.form.get("team", "").strip()

    if not work_date or not title:
        abort(400, "Work date and title are required.")

    try:
        date.fromisoformat(work_date)
        hours = float(request.form.get("hours", "0") or 0)
    except ValueError:
        abort(400, "Enter a valid date and number of hours.")

    if hours < 0:
        abort(400, "Hours cannot be negative.")

    if category not in {"Incident", "RITM", "Task", "Other"}:
        abort(400, "Choose a valid work category.")

    if status not in {"Completed", "In Progress", "Blocked", "Pending"}:
        abort(400, "Choose a valid status.")

    with get_db() as db:
        db.execute(
            """
            INSERT INTO work_items
                (work_date, category, reference, title, details, status,
                 priority, hours, team)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                work_date,
                category,
                reference,
                title,
                details,
                status,
                priority,
                hours,
                team,
            ),
        )

    monday, _, week_value = get_week_dates(
        date.fromisoformat(work_date).strftime("%G-W%V")
    )
    return redirect(url_for("index", week=week_value))


@app.post("/report")
def save_report():
    _, _, week_value = get_week_dates(request.form.get("week", ""))
    monday, _, _ = get_week_dates(week_value)

    with get_db() as db:
        db.execute(
            """
            INSERT INTO weekly_notes
                (week_start, achievements, not_achieved, measures, risks,
                 followups, deployment_plan, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(week_start) DO UPDATE SET
                achievements = excluded.achievements,
                not_achieved = excluded.not_achieved,
                measures = excluded.measures,
                risks = excluded.risks,
                followups = excluded.followups,
                deployment_plan = excluded.deployment_plan,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                monday.isoformat(),
                request.form.get("achievements", "").strip(),
                request.form.get("not_achieved", "").strip(),
                request.form.get("measures", "").strip(),
                request.form.get("risks", "").strip(),
                request.form.get("followups", "").strip(),
                request.form.get("deployment_plan", "").strip(),
            ),
        )

    return redirect(url_for("index", week=week_value) + "#weekly-report")


@app.post("/entries/<int:item_id>/delete")
def delete_entry(item_id):
    with get_db() as db:
        item = db.execute(
            "SELECT work_date FROM work_items WHERE id = ?", (item_id,)
        ).fetchone()
        if item is None:
            abort(404)

        db.execute("DELETE FROM work_items WHERE id = ?", (item_id,))

    monday, _, week_value = get_week_dates(
        date.fromisoformat(item["work_date"]).strftime("%G-W%V")
    )
    return redirect(url_for("index", week=week_value))


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)
