#!/bin/sh

# Wait for database and create tables
python init_db.py

# Start the application
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"
