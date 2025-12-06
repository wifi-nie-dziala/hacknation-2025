#!/bin/bash

echo "🚀 Starting Backend Locally"
echo "=========================="

export DB_HOST=${DB_HOST:-localhost}
export DB_PORT=${DB_PORT:-5432}
export DB_NAME=${DB_NAME:-hacknation}
export DB_USER=${DB_USER:-postgres}
export DB_PASSWORD=${DB_PASSWORD:-postgres}
export FLASK_DEBUG=True
export PORT=8080

echo "Installing dependencies..."
pip install -r requirements.txt


echo "Starting Flask server on http://localhost:8080"
python app.py

