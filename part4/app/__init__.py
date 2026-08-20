#!/usr/bin/python3
"""Flask application factory and extension instances."""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Extensions are created unbound so that several applications -- the server and
# each test case -- can share these module-level objects.
db = SQLAlchemy(session_options={"expire_on_commit": False})
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class=Config):
    """Build a configured application instance."""
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
    jwt.init_app(app)
    # The web client is served as static files from a different origin than the
    # API, so the browser needs cross-origin requests to be allowed.
    CORS(app)

    # Fallback for facade calls made outside a request, such as test fixtures.
    # Requests themselves always use their own application context.
    if not hasattr(db, "_hbnb_default_app"):
        db._hbnb_default_app = app

    # Imported here so that models and routes load after the extensions exist.
    from app.api.v1 import blueprint as api_v1
    app.register_blueprint(api_v1)

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Insert the fixed administrator account when it is missing.

    Creating a user requires an administrator token, so without this account
    a brand new database would have no way to authenticate anyone. The same
    account is defined in sql/seed.sql. Re-running is harmless.
    """
    from app.models.user import User

    admin_id = "36c9050e-ddd3-4c3b-9731-9f487208bbc1"
    if db.session.get(User, admin_id) is not None:
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
