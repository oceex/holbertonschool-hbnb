#!/usr/bin/python3
"""Amenity module.

Defines the Amenity class, representing a feature that a Place can offer
(e.g., "Wi-Fi", "Parking").
"""
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represents an amenity that can be linked to places."""

    def __init__(self, name):
        """Initialize an Amenity.

        Args:
            name (str): Required, max length 50.
        """
        super().__init__()
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("name is required and must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters")
        self._name = value
