#!/usr/bin/python3
"""Expose the shared facade used by all API namespaces."""
from app.services.facade import HBnBFacade

facade = HBnBFacade()
