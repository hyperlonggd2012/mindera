from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import datetime

app = Flask(__name__)
CORS(app)

DB = "mindera_server.db"

# ================= DATABASE =================

def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        author TEXT,
        created_at TEXT
    )
    """)

    # Tạo admin mặc định
    cur.execute("SELECT * FROM users WHERE role='admin'")
    if not cur.fetchone():
        pwd = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", pwd, "admin")
        )

    conn.commit()
    conn.close()

# ================= AUTH =================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user = data["username"]
    pwd = hashlib.sha256(data["password"].encode()).hexdigest()

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (user, pwd, "user")
        )
        conn.commit()
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error", "msg": "User exists"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data["username"]
    pwd = hashlib.sha256(data["password"].encode()).hexdigest()

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (user, pwd)
    )
    row = cur.fetchone()

    if row:
        return jsonify({"status": "ok", "role": row[0]})
    return jsonify({"status": "error"})

# ================= BLOG =================

@app.route("/blogs", methods=["GET"])
def get_blogs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT title, content, author, created_at FROM blogs")
    data = cur.fetchall()
    return jsonify(data)

@app.route("/blogs", methods=["POST"])
def create_blog():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO blogs (title, content, author, created_at) VALUES (?, ?, ?, ?)",
        (
            data["title"],
            data["content"],
            data["author"],
            datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        )
    )
    conn.commit()
    return jsonify({"status": "ok"})

# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)





































 

























