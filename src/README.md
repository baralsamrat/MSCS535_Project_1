# Secure Flask App Example

## Features
- Secure, parameterized DB access (prevents SQL injection)
- Accepts HTTPS (for dev via self-signed; use Nginx/Apache for real deployment)
- Uses environment variables for DB credentials

## Setup

1. **Create a Python virtual environment**:
    ```bash
    python -m venv venv
    ```

2. **Activate the virtual environment**:  
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure DB credentials**:  
   Copy `.env.example` to `.env` and update values.

5. **Run the app (dev mode with self-signed HTTPS)**:
    ```bash
    python app.py
    ```
    - For production: run behind Nginx/Apache configured for HTTPS.

6. **Example request** (use curl or Postman):
    ```bash
    curl -k -X POST https://localhost:5000/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser", "password":"testpass"}'
    ```

## Nginx Example

See `nginx.conf.example` for a sample reverse proxy configuration.

## References

- OWASP Foundation. (2024). [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).
