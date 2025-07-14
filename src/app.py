import os
from flask import Flask, request, jsonify, abort
import psycopg2
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        abort(400, description="Missing username or password")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Safe parameterized query (prevents SQLi!)
        cur.execute("SELECT id FROM users WHERE username=%s AND password=crypt(%s, password)", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB error:", e)
        abort(500, description=str(e))

    if user:
        return jsonify({"status": "success", "user_id": user[0]})
    else:
        abort(401, description="Invalid credentials")

@app.route('/')
def home():
    return "Secure Flask App is running.", 200

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
