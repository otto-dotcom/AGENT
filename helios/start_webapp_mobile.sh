#!/bin/bash
# HELIOS Mobile Access Startup Script
# Allows access from mobile devices on the same network

echo "🌞 Starting HELIOS Web Application (Mobile Access)..."

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="0.0.0.0"
fi

# Navigate to webapp directory
cd "$(dirname "$0")/webapp"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not installed. Installing dependencies..."
    pip install -r ../requirements.txt
fi

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Generate secret key if not set
if [ -z "$FLASK_SECRET_KEY" ]; then
    export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

echo ""
echo "========================================="
echo "🌞 HELIOS Web App Starting"
echo "========================================="
echo ""
echo "📱 Access from this computer:"
echo "   http://localhost:5000"
echo ""
echo "📱 Access from mobile device:"
echo "   http://$LOCAL_IP:5000"
echo ""
echo "💡 Make sure your phone is on the same WiFi network!"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================="
echo ""

# Start Flask app on all interfaces
python3 -c "
from app import app
app.run(host='0.0.0.0', port=5000, debug=True)
"
