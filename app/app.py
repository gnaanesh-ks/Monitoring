from flask import Flask, request, render_template_string, redirect
import psycopg2
import os
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Prometheus metrics endpoint will be available at /metrics
metrics = PrometheusMetrics(app)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "flaskdb")
DB_USER = os.getenv("DB_USER", "flaskuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "flaskpassword")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Flask 2-Tier App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #1d976c, #93f9b9);
            padding: 40px;
        }
        .container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            width: 500px;
            margin: auto;
            box-shadow: 0px 0px 15px #333;
        }
        input, button {
            padding: 10px;
            width: 95%;
            margin: 8px 0;
        }
        button {
            background: #1d976c;
            color: white;
            border: none;
            cursor: pointer;
        }
        h1 {
            color: #1d976c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Registration</h1>

        /add
            <input type="text" name="name" placeholder="Enter your name" required>
            <input type="email" name="email" placeholder="Enter your email" required>
            <button type="submit">Register</button>
        </form>

        <h2>Registered Users</h2>
        <ul>
            {% for user in users %}
                <li>{{ user[1] }} - {{ user[2] }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id DESC;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(HTML_PAGE, users=users)

@app.route("/add", methods=["POST"])
def add_user():
    name = request.form["name"]
    email = request.form["email"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (%s, %s);", (name, email))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
