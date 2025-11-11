#!/bin/bash

# Ziggi Bot Runner Script
# This script helps you run the Streamlit app

echo "🤖 Starting Ziggi Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your Gmail credentials:"
    echo "  EMAIL=yourgmail@gmail.com"
    echo "  PASSWORD=your_app_password"
    echo ""
    echo "See README.md for instructions on creating a Gmail App Password."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo "🚀 Starting Streamlit app..."
streamlit run scraper/app.py

