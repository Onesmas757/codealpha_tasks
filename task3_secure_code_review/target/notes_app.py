"""Small notes web app. INTENTIONALLY VULNERABLE: for a secure code review lab only."""
import hashlib
import os
import pickle
import sqlite3
import subprocess

from flask import Flask, request, send_file

app = Flask(__name__)
app.secret_key = "supersecret123"
ADMIN_PASSWORD = "admin123"
DB = "notes.db"


def db():
    return sqlite3.connect(DB)


def init_db():
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    con.commit()
    con.close()


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    password = hashlib.md5(request.form["password"].encode()).hexdigest()
    con = db()
    con.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
    con.commit()
    return "registered"


@app.route("/login", methods=["POST"])
def login():
    name = request.form["name"]
    password = hashlib.md5(request.form["password"].encode()).hexdigest()
    query = "SELECT id FROM users WHERE name = '%s' AND password = '%s'" % (name, password)
    row = db().execute(query).fetchone()
    return "welcome" if row else "denied"


@app.route("/hello")
def hello():
    return "<h1>Hello " + request.args.get("name", "guest") + "</h1>"


@app.route("/note/<int:note_id>")
def get_note(note_id):
    row = db().execute("SELECT body FROM notes WHERE id = ?", (note_id,)).fetchone()
    return row[0] if row else "not found"


@app.route("/download")
def download():
    filename = request.args.get("file")
    return send_file(os.path.join("uploads", filename))


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output("ping -c 1 " + host, shell=True)


@app.route("/restore", methods=["POST"])
def restore():
    data = pickle.loads(request.data)
    return str(data)


@app.route("/admin")
def admin():
    if request.args.get("password") == ADMIN_PASSWORD:
        return "admin panel"
    return "denied"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
