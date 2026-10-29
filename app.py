"""Q1 + Q3 + Q5 backend: Task Management REST API (Flask + SQLite)."""
import logging
import os
import sqlite3
import time

from flask import Flask, g, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Q5: allow the HTML page to call this API from the browser

DB = os.environ.get("TASKS_DB", "tasks.db")
VALID_STATUS = ("pending", "completed")

# Q3: observability - structured request log with timing
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("task-api")


def connect_db():
    return sqlite3.connect(DB)


def initialize_db():
    with connect_db() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'completed'))
            )
            """
        )


# Create the table on import so gunicorn (Docker) also works
initialize_db()


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def log_request(response):
    ms = (time.perf_counter() - g.get("start", time.perf_counter())) * 1000
    log.info("%s %s -> %s (%.2f ms)", request.method, request.path, response.status_code, ms)
    response.headers["X-Response-Time-ms"] = f"{ms:.2f}"
    return response


def row_to_dict(r):
    return {"id": r[0], "title": r[1], "status": r[2]}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400
    with connect_db() as con:
        cur = con.execute("INSERT INTO tasks (title) VALUES (?)", (title.strip(),))
        task_id = cur.lastrowid
    return jsonify({"id": task_id, "title": title.strip(), "status": "pending"}), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    with connect_db() as con:
        rows = con.execute("SELECT id, title, status FROM tasks ORDER BY id").fetchall()
    return jsonify([row_to_dict(r) for r in rows]), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with connect_db() as con:
        row = con.execute(
            "SELECT id, title, status FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(row_to_dict(row)), 200


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    title, status = data.get("title"), data.get("status")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Valid title is required"}), 400
    if status not in VALID_STATUS:
        return jsonify({"error": "Invalid status"}), 400
    with connect_db() as con:
        cur = con.execute(
            "UPDATE tasks SET title = ?, status = ? WHERE id = ?",
            (title.strip(), status, task_id),
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
    return jsonify({"id": task_id, "title": title.strip(), "status": status}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with connect_db() as con:
        cur = con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
