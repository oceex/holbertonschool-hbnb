#!/usr/bin/python3
"""Place model module.

Defines the Place entity and its domain-specific validation rules.
"""

from app.models.base_model import BaseModel


class Place(BaseModel):
    """Represents a Place entity within the HBnB domain."""

    def __init__(self, title, description, price, latitude, longitude, owner):
        """Initialize a new Place instance.

        Args:
            title (str): The title of the place.
            description (str): Detailed description of the place.
            price (float): The nightly price (must be >= 0).
            latitude (float): Geographical latitude (-90.0 to 90.0).
            longitude (float): Geographical longitude (-180.0 to 180.0).
            owner (User): The User instance representing the owner.
        """
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.reviews = []
        self.amenities = []

    @property
    def title(self):
        """str: The title of the place."""
        return self._title

    @title.setter
    def title(self, value):
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("title is required and must be a non-empty string")
        if len(value) > 100:
            raise ValueError("title must be at most 100 characters")
        self._title = value

    @property
    def price(self):
        """float: The nightly price of the place."""
        return self._price

    @price.setter
    def price(self, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number.")
        if val < 0:
            raise ValueError("Price cannot be negative.")
        self._price = val

    @property
    def latitude(self):
        """float: The geographical latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Latitude must be a valid number.")
        if not (-90.0 <= val <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0.")
        self._latitude = val

    @property
    def longitude(self):
        """float: The geographical longitude."""
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Longitude must be a valid number.")
        if not (-180.0 <= val <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0.")
        self._longitude = val

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place if not already present."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)
