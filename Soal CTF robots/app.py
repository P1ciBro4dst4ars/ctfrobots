from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

DB_PATH = os.path.join(os.getcwd(), "database.db")

FAKE_FLAG = "CTF{s0rry_th1s_1s_n0t_th3_r34l_fl4g_l0l}"  

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )""")
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'S3cur3P4ssw0rd!')")
        conn.commit()
        conn.close()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            db = get_db()
            cur = db.execute(query)
            user = cur.fetchone()
            if user:
                session["user"] = user[1]
                return redirect(url_for("home"))
            else:
                error = "Username atau password salah!"
        except Exception as e:
            error = f"SQL Error: {e}"

    return render_template("login.html", error=error)

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", user=session["user"], fake_flag=FAKE_FLAG)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/robots.txt")
def robots():
    return send_from_directory(os.getcwd(), "robots.txt", mimetype="text/plain")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)