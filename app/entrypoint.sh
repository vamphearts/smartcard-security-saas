#!/bin/sh
set -e
echo "Initializing database schema..."
python -c "from security.audit import init_schema; init_schema()"
echo "Starting gunicorn..."
exec gunicorn -b 0.0.0.0:8000 -w 2 --timeout 120 app:app
