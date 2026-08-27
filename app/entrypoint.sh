#!/bin/sh
echo "Starting application..."
gunicorn --bind 0.0.0.0:5000 app:app
