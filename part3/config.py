"""Application configuration profiles."""

import os


class Config:
    """Define settings shared by all environments."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
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


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
