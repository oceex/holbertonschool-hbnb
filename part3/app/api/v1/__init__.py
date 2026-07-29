#!/usr/bin/python3
"""Configure and register the version 1 API namespaces."""

from flask import Blueprint
from flask_restx import Api

from app.api.v1.users import api as users_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.auth import api as auth_ns  # Import auth namespace

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
api.add_namespace(auth_ns, path="/auth")  # Register auth namespace under /auth path
