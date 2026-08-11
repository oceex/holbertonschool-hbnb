#!/usr/bin/python3
"""Mapped Review model, relationships, and validation rules."""
from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel


class Review(BaseModel):
    """Represent a review left by a user for a place."""

    __tablename__ = "reviews"

    text = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(
        db.String(36), db.ForeignKey("places.id"), nullable=False
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )

    place = db.relationship("Place", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    def __init__(self, text, rating, place, user):
        """Initialize a validated review and synchronize relationships."""
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

    @validates("text")
    def validate_text(self, key, value):
        """Validate and normalize review text."""
        if not isinstance(value, str):
            raise ValueError("text is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("text is required and must be a string")
        return value

    @validates("rating")
    def validate_rating(self, key, value):
        """Require an integer rating from one through five."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("rating must be an integer")
        if not 1 <= value <= 5:
            raise ValueError("rating must be between 1 and 5")
        return value

    @validates("place")
    def validate_place(self, key, value):
        """Require a mapped Place relationship."""
        from app.models.place import Place

        if not isinstance(value, Place):
            raise ValueError("place must be a valid Place instance")
        return value

    @validates("user")
    def validate_user(self, key, value):
        """Require a mapped User relationship."""
        from app.models.user import User

        if not isinstance(value, User):
            raise ValueError("user must be a valid User instance")
        return value
