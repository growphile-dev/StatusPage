#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Initialize database tables
python3 -c "
from app import init_db
init_db()
print('Database initialized')
"

# Start gunicorn
exec gunicorn -w 2 -b 0.0.0.0:5000 app:app
