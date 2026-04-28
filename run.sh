#!/bin/bash

# Quick Win Generator - Start Script
# Automatically sets up and runs the demo

set -e

echo "🚀 Quick Win Generator - Python Demo"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "💡 Tip: Set ANTHROPIC_API_KEY for live AI chat"
    echo "   export ANTHROPIC_API_KEY='your-key'"
    echo "   Demo works great without it too!"
    echo ""
fi

echo "🌐 Starting demo..."
echo "   Opening browser to http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run app.py
