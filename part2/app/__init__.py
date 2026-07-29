#!/usr/bin/python3
"""Flask application factory."""

from flask import Flask
from app.api.v1 import blueprint as api_v1


def create_app(config_class=None):
    """Create the Flask application and register the versioned API."""
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)

    app.register_blueprint(api_v1)

    return app
