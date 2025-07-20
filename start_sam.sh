#!/bin/bash

# SAM Startup Script
# This script activates the virtual environment and starts SAM

echo "🤖 Starting SAM - Your Personal AI Assistant"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "sam_env" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv sam_env
    source sam_env/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment and start SAM
echo "🚀 Launching SAM..."
source sam_env/bin/activate
python main.py 