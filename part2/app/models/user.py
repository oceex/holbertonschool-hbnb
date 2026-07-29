#!/usr/bin/python3
"""User model and validation rules."""
import re

from app.models.base_model import BaseModel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represent a user who can own places and write reviews."""

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """Initialize a validated user and empty relationship collections."""
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin

        self.places = []
        self.reviews = []

    @property
    def first_name(self):
        """str: The user's first name."""
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str):
            raise ValueError("first_name is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("first_name is required and must be a string")
        if len(value) > 50:
            raise ValueError("first_name must be at most 50 characters")
        self._first_name = value

    @property
    def last_name(self):
        """str: The user's last name."""
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str):
            raise ValueError("last_name is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("last_name is required and must be a string")
        if len(value) > 50:
            raise ValueError("last_name must be at most 50 characters")
        self._last_name = value

    @property
    def email(self):
        """str: The normalized email address."""
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise ValueError("email is required and must be a string")
        # Repository-level uniqueness checks rely on the normalized value.
        value = value.strip()
        if not value:
            raise ValueError("email is required and must be a string")
        if not EMAIL_REGEX.match(value):
            raise ValueError("email must be a valid email address")
        self._email = value

    @property
    def is_admin(self):
        """bool: Whether the user has administrative privileges."""
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        self._is_admin = value

    @property
    def password(self):
        """str: The stored plaintext credential."""
        return self._password

    @password.setter
    def password(self, value):
        if not isinstance(value, str):
            raise ValueError("password is required and must be a string")
        # Validate trimmed content without altering the caller-provided credential.
        if not value.strip():
            raise ValueError("password is required and must be a string")
        # This layer currently stores passwords verbatim; hashing is not implemented.
        self._password = value

    def verify_password(self, pwd):
        """Return whether a plaintext password matches the stored credential."""
        return self._password == pwd

    def add_place(self, place):
        """Associate an owned place, preserving relationship integrity."""
        from app.models.place import Place

        if not isinstance(place, Place):
            raise TypeError("place must be a Place instance")
        if place.owner is not self:
            raise ValueError("place must be owned by this user")
        if place not in self.places:
            self.places.append(place)
            self.save()

    def add_review(self, review):
        """Associate an authored review, preserving relationship integrity."""
        from app.models.review import Review

        if not isinstance(review, Review):
            raise TypeError("review must be a Review instance")
        if review.user is not self:
            raise ValueError("review must be authored by this user")
        if review not in self.reviews:
            self.reviews.append(review)
            self.save()
