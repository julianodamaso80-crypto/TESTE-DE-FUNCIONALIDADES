#!/bin/bash
set -e
echo "Running migrations..."
python manage.py migrate --noinput
echo "Initializing Railway..."
python manage.py railway_init
echo "Release complete."
