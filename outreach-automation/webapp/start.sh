#!/bin/bash

# Outreach Campaign Manager - Startup Script

echo "🚀 Starting Outreach Campaign Manager..."
echo ""

# Check if .env exists
if [ ! -f "../config/credentials.env" ]; then
    echo "❌ Error: credentials.env not found!"
    echo "Please copy config/credentials.example.env to config/credentials.env and fill in your credentials."
    exit 1
fi

# Load environment variables
export $(cat ../config/credentials.env | xargs)

echo "✅ Environment variables loaded"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running. Starting services locally..."
    echo ""

    # Start backend
    echo "🔧 Starting backend on http://localhost:8000..."
    cd backend
    pip install -r requirements.txt > /dev/null 2>&1
    python -m uvicorn main:app --reload &
    BACKEND_PID=$!
    cd ..

    # Start frontend
    echo "🎨 Starting frontend on http://localhost:3000..."
    cd frontend
    npm install > /dev/null 2>&1
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Backend API: http://localhost:8000"
    echo "🌐 Frontend App: http://localhost:3000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""

    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
else
    echo "🐳 Docker detected! Starting with Docker Compose..."
    echo ""
    docker-compose up --build
fi
