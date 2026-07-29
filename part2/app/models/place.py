#!/usr/bin/python3
"""Place model and validation rules."""

from app.models.base_model import BaseModel
from app.models.user import User


class Place(BaseModel):
    """Represent a rentable place and its related domain objects."""

    def __init__(self, title, description, price, latitude, longitude, owner):
        """Initialize a validated place and synchronize its owner relationship."""
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
        if not isinstance(value, str):
            raise ValueError("title is required and must be a non-empty string")
        value = value.strip()
        if not value:
            raise ValueError("title is required and must be a non-empty string")
        if len(value) > 100:
            raise ValueError("title must be at most 100 characters")
        self._title = value

    @property
    def description(self):
        """str: Optional detailed description of the place."""
        return self._description

    @description.setter
    def description(self, value):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        self._description = value

    @property
    def price(self):
        """float: The nightly price of the place."""
        return self._price

    @price.setter
    def price(self, value):
        # bool is numeric in Python but is not a valid monetary value.
        if isinstance(value, bool):
            raise ValueError("Price must be a valid number.")
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number.")
        if val <= 0:
            raise ValueError("Price must be greater than zero.")
        self._price = val

    @property
    def latitude(self):
        """float: The geographical latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        # bool is numeric in Python but is not a valid coordinate.
        if isinstance(value, bool):
            raise ValueError("Latitude must be a valid number.")
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
        # bool is numeric in Python but is not a valid coordinate.
        if isinstance(value, bool):
            raise ValueError("Longitude must be a valid number.")
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Longitude must be a valid number.")
        if not (-180.0 <= val <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0.")
        self._longitude = val

    @property
    def owner(self):
        """User: The place owner."""
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, User):
            raise TypeError("owner must be a User instance")
        self._owner = value
        # Keep both sides of the ownership relationship navigable.
        value.add_place(self)

    def add_review(self, review):
        """Associate a review that belongs to this place."""
        from app.models.review import Review
        if not isinstance(review, Review):
            raise TypeError("review must be a Review instance")
        if review.place is not self:
            raise ValueError("review must belong to this place")
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()

    def add_amenity(self, amenity):
        """Associate an amenity and refresh the modification timestamp."""
        from app.models.amenity import Amenity
        if not isinstance(amenity, Amenity):
            raise TypeError("amenity must be an Amenity instance")
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.save()
