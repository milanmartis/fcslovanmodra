#!/bin/sh
set -e

echo "Running DB migrations..."
# FLASK_APP je nastavené v Dockerfile (run.py), takže stačí:
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn -b 0.0.0.0:5000 run:app