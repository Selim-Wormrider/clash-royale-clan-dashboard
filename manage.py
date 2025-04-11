#!/bin/bash

cd /opt/dashboard
source venv/bin/activate

SCRIPT=$1

if [ -z "$SCRIPT" ]; then
  echo "Usage: ./manage.py <scriptname.py>"
  exit 1
fi

echo "🔁 Running $SCRIPT..."
python3 "$SCRIPT"
