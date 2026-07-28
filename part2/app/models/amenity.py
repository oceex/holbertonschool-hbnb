#!/usr/bin/python3
"""Amenity module.

Defines the Amenity class, representing a feature that a Place can offer
(e.g., "Wi-Fi", "Parking").
"""
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """Represents an amenity that can be linked to places."""

    def __init__(self, name, description=""):
        """Initialize an Amenity.

        Args:
            name (str): Required, max length 50.
        """
        super().__init__()
        self.name = name
        # The old model missed the optional description required by Task 1.
        # A validated default keeps amenities complete without forcing input.
        self.description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("name is required and must be a string")
        # The old validation accepted whitespace-only amenity names.
        # Trimming before storage prevents names from becoming empty.
        value = value.strip()
        if not value:
            raise ValueError("name is required and must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters")
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        # The previous class had no description validation at all.
        # This keeps the optional field string-based for future serializers.
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        self._description = value
