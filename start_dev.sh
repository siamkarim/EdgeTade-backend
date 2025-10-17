#!/bin/bash
# Development startup script for EdgeTrade FastAPI

echo "Starting EdgeTrade FastAPI Server (Development Mode)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the server with auto-reload
echo "Starting FastAPI server with auto-reload..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
