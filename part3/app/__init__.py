#!/usr/bin/python3
"""Flask application factory."""

from flask import Flask
from app.api.v1 import blueprint as api_v1
from config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(api_v1)

    return app
