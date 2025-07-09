#!/bin/bash

# Build the project
echo "Building the project..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
