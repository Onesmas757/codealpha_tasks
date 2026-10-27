"""Small notes web app, fixed version of notes_app.py (secure code review lab)."""
import ipaddress
import json
import os
import sqlite3
import subprocess
from functools import wraps

from flask import Flask, abort, request, send_from_directory, session
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
DB = "notes.db"
UPLOAD_DIR = os.path.abspath("uploads")


def db():
    return sqlite3.connect(DB)


def init_db():
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    con.commit()
    con.close()


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            abort(401)
        return view(*args, **kwargs)
    return wrapper


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    password = generate_password_hash(request.form["password"])
    con = db()
    con.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
    con.commit()
    con.close()
    return "registered"


@app.route("/login", methods=["POST"])
def login():
    name = request.form["name"]
    row = db().execute("SELECT password FROM users WHERE name = ?", (name,)).fetchone()
    if row and check_password_hash(row[0], request.form["password"]):
        session.clear()
        session["user"] = name
        return "welcome"
    return "denied", 401


@app.route("/hello")
def hello():
    return "<h1>Hello " + str(escape(request.args.get("name", "guest"))) + "</h1>"


@app.route("/note/<int:note_id>")
@login_required
def get_note(note_id):
    row = db().execute(
        "SELECT body FROM notes WHERE id = ? AND owner = ?", (note_id, session["user"])
    ).fetchone()
    if row is None:
        abort(404)
    return row[0], 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/download")
def download():
    filename = request.args.get("file")
    if not filename:
        abort(400)
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        address = str(ipaddress.ip_address(host))
    except ValueError:
        abort(400)
    result = subprocess.run(
        ["ping", "-c", "1", address], capture_output=True, text=True, timeout=5, check=False
    )
    return result.stdout, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/restore", methods=["POST"])
def restore():
    try:
        data = json.loads(request.data)
    except ValueError:
        abort(400)
    if not isinstance(data, dict):
        abort(400)
    return json.dumps(data)


@app.route("/admin", methods=["POST"])
def admin():
    password = request.form.get("password", "")
    if ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, password):
        return "admin panel"
    return "denied", 403


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
