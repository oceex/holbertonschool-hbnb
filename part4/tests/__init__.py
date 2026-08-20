"""Test package bound to a throwaway in-memory database.

Importing ``run`` would attach the suite to the development database file and
leave every fixture it creates behind in it, so the suite builds its own
application from ``TestingConfig`` instead.
"""
from app import create_app
from config import TestingConfig

app = create_app(TestingConfig)
