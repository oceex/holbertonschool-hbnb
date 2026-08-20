#!/usr/bin/python3
"""Entry point for the HBnB Flask application."""
import os

from app import create_app
from config import config

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
