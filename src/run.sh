#!/bin/bash
set -e

echo "========== Secure Flask App Setup =========="

# Step 1: Create virtual environment if not present
if [ ! -d "venv" ]; then
    echo "[1/6] Creating Python virtual environment..."
    python -m venv venv
else
    echo "[1/6] Virtual environment already exists."
fi

# Step 2: Activate the virtual environment (Windows or Unix)
echo "[2/6] Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Error: Could not find virtual environment activation script."
    exit 1
fi

# Step 3: Install requirements
echo "[3/6] Installing requirements..."
pip install -r requirements.txt

# Step 4: Copy .env.example to .env if not present
if [ ! -f ".env" ]; then
    echo "[4/6] Creating .env from .env.example..."
    cp .env.example .env
    echo "      Please update your .env file with correct database credentials before using the app."
else
    echo "[4/6] .env file already exists."
fi

# Step 5: Reminder for DB setup
echo "[5/6] (Reminder) Make sure your database is running and accessible with the credentials in your .env file."

# Step 6: Run the Flask app (self-signed HTTPS for dev)
echo "[6/6] Starting Flask app (development mode, HTTPS self-signed cert)..."
echo "--------------------------------------------"
python app.py
