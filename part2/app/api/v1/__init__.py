#!/usr/bin/python3
"""Initialization module for API version 1.

This module establishes the Flask Blueprint for version 1 of the application API,
initializes the Flask-RESTx Api object wrapper, and registers all active
namespaces (Users, Reviews, Amenities, and Places) to expose their endpoints under
the corresponding unified prefixes.
"""

from flask import Blueprint
from flask_restx import Api

from app.api.v1.users import api as users_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns

blueprint = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api = Api(
    blueprint,
    title="HBnB API",
    version="1.0",
    description="Core Presentation Layer exposing RESTful services for the HBnB Application.",
    doc="/doc"
)

api.add_namespace(users_ns, path="/users")
api.add_namespace(reviews_ns, path="/reviews")
api.add_namespace(amenities_ns, path="/amenities")
api.add_namespace(places_ns, path="/places")
