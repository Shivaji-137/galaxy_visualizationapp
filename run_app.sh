#!/bin/bash
# Quick start script for Galaxy & AGN Explorer

echo "🌌 Starting Galaxies & AGN Multi-Survey Explorer..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Launching application..."
echo ""
echo "The app will open in your default web browser at:"
echo "http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
