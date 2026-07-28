# !/usr/bin/python3
"""Amenity module.

Defines the Amenity class, representing a feature that a Place can offer
(e.g., "Wi-Fi", "Parking").
"""
from sqlalchemy.orm import validates
from app import db
from app.models.Base_model import BaseModel


class Amenity(BaseModel):
    """Represents an amenity that can be linked to places."""

    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        """Initialize a new Amenity instance.

        Args:
            name (str): Required name of the amenity (max 50 chars).
        """
        super().__init__()
        self.name = name

    @validates('name')
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("name is required and must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters")
        return value
