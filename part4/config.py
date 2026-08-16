"""Application configuration profiles."""

import os


class Config:
    """Define settings shared by all environments."""

    # Fallback only -- always set a real SECRET_KEY via the environment in
    # any deployment. This placeholder is deliberately long enough (32+
    # bytes) to meet HS256's minimum recommended key length, but it is
    # still a *public, checked-in* value and must never be used in
    # production.
    SECRET_KEY = os.getenv(
        'SECRET_KEY', 'dev-only-insecure-default-key-do-not-use-in-prod'
    )
    # Flask-JWT-Extended falls back to SECRET_KEY when this is unset; setting
    # it explicitly keeps the JWT signing key independent of Flask's own
    # session/cookie signing key (defense in depth).
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///development.db',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Enable development diagnostics."""

    DEBUG = True


class TestingConfig(Config):
    """Enable Flask testing behavior and diagnostics."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Disable development diagnostics for a real deployment."""


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
