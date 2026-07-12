#!/usr/bin/python3
"""Place module.

Defines the Place class, representing a rentable location owned by a
User, which can have Reviews and Amenities associated with it.
"""
from app.models.base_model import BaseModel
from app.models.user import User


class Place(BaseModel):
    """Represents a place that can be listed and reviewed."""

    def __init__(self, title, description, price, latitude, longitude,
                 owner):
        """Initialize a Place.

        Args:
            title (str): Required, max length 100.
            description (str): Optional.
            price (float): Must be positive.
            latitude (float): Must be within -90.0 to 90.0.
            longitude (float): Must be within -180.0 to 180.0.
            owner (User): The User instance who owns this place.
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

        # Keep the owning User's list of places in sync
        self.owner.add_place(self)

    # -- Validated properties -------------------------------------------
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("title is required and must be a string")
        if len(value) > 100:
            raise ValueError("title must be at most 100 characters")
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("description must be a string")
        self._description = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("price must be a number")
        if value <= 0:
            raise ValueError("price must be a positive value")
        self._price = float(value)

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("latitude must be a number")
        if not (-90.0 <= value <= 90.0):
            raise ValueError("latitude must be between -90.0 and 90.0")
        self._latitude = float(value)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("longitude must be a number")
        if not (-180.0 <= value <= 180.0):
            raise ValueError("longitude must be between -180.0 and 180.0")
        self._longitude = float(value)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, User):
            raise ValueError("owner must be a valid User instance")
        self._owner = value

    # -- Relationship helpers ---------------------------------------------
    def add_review(self, review):
        """Add a review to the place."""
        from app.models.review import Review
        if not isinstance(review, Review):
            raise ValueError("review must be a valid Review instance")
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place (many-to-many relationship)."""
        from app.models.amenity import Amenity
        if not isinstance(amenity, Amenity):
            raise ValueError("amenity must be a valid Amenity instance")
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def list_amenities(self):
        """Return the list of amenities associated with this place."""
        return self.amenities
