#!/usr/bin/python3
"""Application factory module.

Initializes the Flask application and registers the API Blueprint
to connect all functional endpoints.
"""

from flask import Flask
from app.api.v1 import blueprint as api_v1


def create_app(config_class=None):
    """Create and configure the Flask application instance.

    Args:
        config_class: Optional configuration object/module.

    Returns:
        Flask: The initialized Flask application.
    """
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)

    app.register_blueprint(api_v1)

    return app
