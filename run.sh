#!/bin/bash
# Smart-Encrypt launcher script for Linux

echo "◉ Smart-Encrypt Launcher ◉"
echo "=========================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    ./venv/bin/python -m pip install -r requirements.txt
fi

# Create data directory with proper permissions
mkdir -p ~/.smart_encrypt
chmod 700 ~/.smart_encrypt

echo "Launching Smart-Encrypt..."
./venv/bin/python app.py