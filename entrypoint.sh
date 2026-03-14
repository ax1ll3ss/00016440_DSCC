#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'confessions_db'),
        user=os.environ.get('POSTGRES_USER', 'confessions_user'),
        password=os.environ.get('POSTGRES_PASSWORD', 'confessions_pass'),
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
    )
    conn.close()
except Exception:
    exit(1)
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# If arguments are provided, execute them. Otherwise, start Gunicorn.
if [ $# -gt 0 ]; then
    exec "$@"
else
    echo "Starting Gunicorn..."
    exec gunicorn confessions_project.wsgi:application -c /home/appuser/gunicorn.conf.py
fi
