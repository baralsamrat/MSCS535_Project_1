import os
from flask import Flask, request, jsonify, abort
import psycopg2
import threading
import time
import unittest
import requests
import concurrent.futures
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_HOST = "127.0.0.1"
DB_NAME = "yourdb"
DB_USER = "youruser"
DB_PASSWORD = "yourpassword"

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
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

class FlaskLoginTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_login_success(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.get_json().get('status', ''))

    def test_login_fail(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 401)

    def test_sql_injection(self):
        response = self.client.post('/login', json={
            'username': "testuser' --",
            'password': 'irrelevant'
        })
        self.assertEqual(response.status_code, 401)
        response2 = self.client.post('/login', json={
            'username': "testuser",
            'password': "anything' OR '1'='1"
        })
        self.assertEqual(response2.status_code, 401)

def concurrent_login_test(num_requests=10, print_summary=True):
    url = 'https://127.0.0.1:5000/login'
    data = {'username': 'testuser', 'password': 'testpass'}
    results = [None] * num_requests

    def do_login(i):
        try:
            resp = requests.post(url, json=data, verify=False, timeout=5)
            return (i, resp.status_code, resp.text.strip())
        except Exception as e:
            return (i, 'ERROR', str(e))

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, num_requests)) as executor:
        futs = {executor.submit(do_login, i): i for i in range(1, num_requests+1)}
        for fut in concurrent.futures.as_completed(futs):
            idx, code, text = fut.result()
            results[idx-1] = (idx, code, text)
    if print_summary:
        print(f"\n[Concurrent Test] Sent {num_requests} parallel login requests:")
        passed = 0
        for i, code, text in results:
            ok = str(code) == '200' and 'success' in text
            print(f"[{'✔' if ok else '✗'}] Request {i}: {code} {text}")
            if ok:
                passed += 1
        print(f"[Concurrent Test] {passed}/{num_requests} logins succeeded.\n")
    return results

if __name__ == '__main__':
    class CheckboxTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            print(f"[✔] {test}")

        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"[✗] {test}")

        def addError(self, test, err):
            super().addError(test, err)
            print(f"[✗] {test} (error)")

    print("Running automated tests:")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FlaskLoginTestCase)
    runner = unittest.TextTestRunner(resultclass=CheckboxTestResult, verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\nAll tests passed! Starting Flask app for concurrent login test...\n")
        flask_thread = threading.Thread(target=lambda: app.run(ssl_context='adhoc', use_reloader=False), daemon=True)
        flask_thread.start()
        time.sleep(2)
        try:
            concurrent_login_test(10)
        except Exception as e:
            print("Concurrent test error:", e)
        print("Now starting Flask app for manual use...\n")
        app.run(ssl_context='adhoc')
    else:
        print("\nSome tests failed. Please fix errors above before running the app.\n")
        import sys
        sys.exit(1)
