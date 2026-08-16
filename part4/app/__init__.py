#!/usr/bin/python3
"""Flask application factory."""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager  # Import JWTManager

from config import Config

db = SQLAlchemy(session_options={"expire_on_commit": False})
bcrypt = Bcrypt()
jwt = JWTManager()  # Initialize JWTManager


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
    jwt.init_app(app)  # Initialize JWT with the app
    CORS(app)

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
        _seed_admin()

    return app


def _seed_admin():
    """Ensure the project's fixed administrator account exists.

    Part 3, Task 9 defines this exact account (fixed id, email, password)
    as the seed data for the raw-SQL demo database. The live SQLAlchemy
    app never seeded it, so there was no way to bootstrap the first
    account -- POST /users/ is admin-only per Part 3, Task 4/5. Safe to
    call on every startup: it only inserts when the fixed id is absent.
    """
    from app.models.user import User

    admin_id = "36c9050e-ddd3-4c3b-9731-9f487208bbc1"
    if User.query.get(admin_id) is not None:
        return

    admin = User(
        first_name="Admin",
        last_name="HBnB",
        email="admin@hbnb.io",
        password="admin1234",
        is_admin=True,
    )
    admin.id = admin_id
    db.session.add(admin)
    db.session.commit()
