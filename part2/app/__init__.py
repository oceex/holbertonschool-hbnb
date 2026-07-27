#!/usr/bin/python3
"""Application factory module.

Initializes the Flask application and registers the API Blueprint
to connect all functional endpoints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

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
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db.init_app(app)
    bcrypt.init_app(app)

    # Imported inside the factory, not at module level: by the time
    # this line runs, db/bcrypt above already exist, so anything this
    # import pulls in (routes -> models) can safely do
    # `from app import db, bcrypt`.

    from app.api.v1 import blueprint as api_v1
    app.register_blueprint(api_v1)

    return app