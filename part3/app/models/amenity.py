#!/usr/bin/python3
"""Amenity model and validation rules."""
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represents an amenity that can be linked to places."""

    def __init__(self, name, description=""):
        """Initialize an amenity with an optional description."""
        super().__init__()
        self.name = name
        self.description = description

    @property
    def name(self):
        """str: The normalized amenity name."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("name is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("name is required and must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters")
        self._name = value

    @property
    def description(self):
        """str: The optional amenity description."""
        return self._description

    @description.setter
    def description(self, value):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        self._description = value
