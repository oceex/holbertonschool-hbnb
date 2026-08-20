#!/usr/bin/python3
"""Tests for application factory configuration."""

import unittest

from app import create_app
from config import Config


class TestApplicationFactory(unittest.TestCase):
    """Exercise default and custom application configuration."""

    def test_create_app_loads_default_config(self):
        """Verify the base configuration is loaded by default."""
        app = create_app()

        self.assertEqual(app.config['SECRET_KEY'], Config.SECRET_KEY)
        self.assertEqual(app.config['DEBUG'], Config.DEBUG)

    def test_create_app_loads_custom_config(self):
        """Verify callers can supply an alternate configuration class."""
        class CustomConfig:
            TESTING = True
            SECRET_KEY = "test-secret"

        app = create_app(CustomConfig)

        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['SECRET_KEY'], "test-secret")

    def test_create_app_registers_api_blueprint(self):
        """Verify application creation preserves API registration."""
        app = create_app()

        self.assertIn('api_v1', app.blueprints)
        self.assertTrue(
            any(
                rule.rule.startswith('/api/v1')
                for rule in app.url_map.iter_rules()
            )
        )


if __name__ == '__main__':
    unittest.main()
