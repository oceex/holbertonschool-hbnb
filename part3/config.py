"""Application configuration profiles."""

import os


class Config:
    """Define settings shared by all environments."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    """Enable development diagnostics."""

    DEBUG = True


class TestingConfig(Config):
    """Enable Flask testing behavior and diagnostics."""

    TESTING = True
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
