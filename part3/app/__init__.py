#!/usr/bin/python3
"""Flask application factory."""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy(session_options={"expire_on_commit": False})
bcrypt = Bcrypt()


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config.setdefault(
        'SQLALCHEMY_DATABASE_URI',
        Config.SQLALCHEMY_DATABASE_URI,
    )
    app.config.setdefault(
        'SQLALCHEMY_TRACK_MODIFICATIONS',
        Config.SQLALCHEMY_TRACK_MODIFICATIONS,
    )

    db.init_app(app)
    bcrypt.init_app(app)

    # Repositories use the first factory application only when legacy callers
    # invoke the Facade outside a Flask context. Requests still use their
    # current application context.
    if not hasattr(db, "_hbnb_default_app"):
        db._hbnb_default_app = app

    # Delay route/model imports until extensions are defined and configured.
    from app.api.v1 import blueprint as api_v1
    app.register_blueprint(api_v1)

    with app.app_context():
        db.create_all()

    return app
