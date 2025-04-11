#!/bin/bash

cd /opt/dashboard
source venv/bin/activate

echo "🚀 Starting Bravo Six with Uvicorn production settings..."
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --proxy-headers \
  --log-level info
