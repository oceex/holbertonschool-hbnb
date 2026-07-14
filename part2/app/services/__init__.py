#!/usr/bin/python3
"""Services package.

Exposes a single shared HBnBFacade instance so that every API module
talks to the same in-memory repositories.
"""
from app.services.facade import HBnBFacade

facade = HBnBFacade()
