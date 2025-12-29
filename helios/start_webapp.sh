#!/bin/bash
# HELIOS Web Application Startup Script

echo "🌞 Starting HELIOS Web Application..."

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
echo "="*60
echo "HELIOS Web App Starting"
echo "="*60
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo "="*60
echo ""

# Start Flask app
python3 app.py
