#!/usr/bin/python3
"""Mapped User model, validation rules, and password handling."""
import re

from sqlalchemy.orm import validates

from app import bcrypt, db
from app.models.base_model import BaseModel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represent a user who can own places and write reviews."""

    __tablename__ = "users"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column("password", db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    places = db.relationship(
        "Place", back_populates="owner", cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """Initialize a validated user and hash its plaintext password once."""
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin

    @validates("first_name", "last_name")
    def validate_name(self, key, value):
        """Validate and normalize a user's name."""
        if not isinstance(value, str):
            raise ValueError(f"{key} is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{key} is required and must be a string")
        if len(value) > 50:
            raise ValueError(f"{key} must be at most 50 characters")
        return value

    @validates("email")
    def validate_email(self, key, value):
        """Validate and normalize an email address."""
        if not isinstance(value, str):
            raise ValueError("email is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("email is required and must be a string")
        if not EMAIL_REGEX.match(value):
            raise ValueError("email must be a valid email address")
        return value

    @validates("is_admin")
    def validate_is_admin(self, key, value):
        """Require an explicit boolean administrative flag."""
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        return value

    @property
    def password(self):
        """str: The stored bcrypt password hash."""
        return self._password

    @password.setter
    def password(self, value):
        self.hash_password(value)

    def hash_password(self, password):
        """Validate, hash, and store a plaintext password."""
        if not isinstance(password, str) or not password.strip():
            raise ValueError("password is required and must be a string")
        if len(password) < 8:
            raise ValueError("password must be at least 8 characters long")
        self._password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Return whether a plaintext password matches the stored hash."""
        return bcrypt.check_password_hash(self._password, password)

    def to_dict(self):
        """Return user data without password credentials."""
        data = super().to_dict()
        data.pop("password", None)
        data.pop("_password", None)
        return data

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
