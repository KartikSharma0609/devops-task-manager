#!/bin/sh
set -e

echo "========================================"
echo "Running database migrations..."
echo "========================================"

flask db upgrade

echo "========================================"
echo "Starting Gunicorn..."
echo "========================================"

exec gunicorn \
  --bind 0.0.0.0:${PORT:-5000} \
  --workers 2 \
  --threads 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  "app:create_app()"
