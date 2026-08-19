"""Application configuration profiles."""

import os
from datetime import timedelta


class Config:
    """Settings shared by every environment."""

    # Checked-in placeholder. A deployment must supply SECRET_KEY through the
    # environment, since this value is public and therefore not secret.
    SECRET_KEY = os.getenv(
        'SECRET_KEY', 'dev-only-insecure-default-key-do-not-use-in-prod'
    )
    # Kept separate from SECRET_KEY so rotating one key does not invalidate
    # what the other signs.
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    # The library default is 15 minutes, which expires mid-visit while the
    # browser still holds the cookie and the interface still looks signed in.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
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
    """Run against a throwaway in-memory database."""

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
