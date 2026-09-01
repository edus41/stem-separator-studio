#!/bin/bash
set -e

echo "=================================================="
echo "  🎧 Starting Stem Separator Studio"
echo "=================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install Python 3.10+."
    exit 1
fi

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python3 main.py
