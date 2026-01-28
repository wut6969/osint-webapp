#!/bin/bash

echo "🚀 Starting OSINT Web App..."
echo ""

cd ~/osint-webapp/backend
source venv/bin/activate
python run.py &
FLASK_PID=$!
echo "✅ Flask backend started (PID: $FLASK_PID)"

sleep 3

cd ~/osint-webapp/frontend
echo "✅ Starting React frontend..."
npm run dev -- --host

kill $FLASK_PID 2>/dev/null
echo "🛑 Shutting down..."
