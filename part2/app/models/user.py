#!/usr/bin/python3
"""User module.

Defines the User class, representing an application user who can own
places and write reviews.
"""
import re

from app.models.base_model import BaseModel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represents a user of the HBnB application."""

    # Tracks emails already in use so we can enforce uniqueness without
    # a persistence layer. A real implementation would delegate this
    # check to the repository/database instead.
    _emails_in_use = set()

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """Initialize a new User instance.

        Args:
            first_name (str): Required first name of the user (max 50 chars).
            last_name (str): Required last name of the user (max 50 chars).
            email (str): Required, must be a unique and valid email format.
            password (str): Required, plaintext password to be validated.
            is_admin (bool, optional): Administrative privilege flag. Defaults to False.
        """
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password  # Invokes the password setter for validation
        self.is_admin = is_admin

        # Navigation properties for established relationships
        self.places = []
        self.reviews = []

    # -- Validated properties -------------------------------------------
    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("first_name is required and must be a string")
        if len(value) > 50:
            raise ValueError("first_name must be at most 50 characters")
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("last_name is required and must be a string")
        if len(value) > 50:
            raise ValueError("last_name must be at most 50 characters")
        self._last_name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("email is required and must be a string")
        if not EMAIL_REGEX.match(value):
            raise ValueError("email must be a valid email address")
        existing = getattr(self, "_email", None)
        if value != existing:
            if value in User._emails_in_use:
                raise ValueError(f"email '{value}' is already in use")
            if existing is not None:
                User._emails_in_use.discard(existing)
            User._emails_in_use.add(value)
        self._email = value

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        self._is_admin = value

    @property
    def password(self):
        """str: Secure credentials for user authentication."""
        return self._password

    @password.setter
    def password(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("password is required and must be a string")
        # NOTE: Cryptographic hashing (e.g., bcrypt) will be integrated in Part 3.
        self._password = value

    def verify_password(self, pwd):
        """Verify if the provided plaintext password matches the stored credential.

        Args:
            pwd (str): The plaintext password submitted during login.

        Returns:
            bool: True if the verification succeeds, False otherwise.
        """
        return self._password == pwd

    # -- Relationship helpers ---------------------------------------------
    def add_place(self, place):
        """Associate a Place owned by this user."""
        self.places.append(place)

    def add_review(self, review):
        """Associate a Review written by this user."""
        self.reviews.append(review)
