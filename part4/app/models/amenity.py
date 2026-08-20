#!/usr/bin/python3
"""Mapped Amenity model and validation rules."""
from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity that can be linked to places."""

    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1000), default="", nullable=False)

    def __init__(self, name, description=""):
        """Initialize an amenity with an optional description."""
        super().__init__()
        self.name = name
        self.description = description

    @validates("name")
    def validate_name(self, key, value):
        """Validate and normalize the amenity name."""
        if not isinstance(value, str):
            raise ValueError("name is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("name is required and must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters")
        return value

    @validates("description")
    def validate_description(self, key, value):
        """Normalize and validate the optional description."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        return value
