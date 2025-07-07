from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secret key for session handling

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()  # Run database initialization

# Route for Homepage (Netflix landing page)
@app.route("/")
def index():
    return render_template("index.html")

# Route for Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, password))
            conn.commit()
            conn.close()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists. Try again!", "danger")

    return render_template("register.html")

# Route for Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "danger")

    return render_template("login.html")

# Route for Dashboard Page (Only accessible after login)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    else:
        flash("You need to log in first!", "danger")
        return redirect(url_for("login"))

# Route for Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
