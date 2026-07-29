#!/usr/bin/python3
"""Mapped Place model, relationships, and validation rules."""
from sqlalchemy.orm import validates

from app import db
from app.models.base_model import BaseModel

place_amenity = db.Table(
    "place_amenity",
    db.Column(
        "place_id",
        db.String(36),
        db.ForeignKey("places.id"),
        primary_key=True,
    ),
    db.Column(
        "amenity_id",
        db.String(36),
        db.ForeignKey("amenities.id"),
        primary_key=True,
    ),
)


class Place(BaseModel):
    """Represent a rentable place and its related domain objects."""

    __tablename__ = "places"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), default="", nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False
    )

    owner = db.relationship("User", back_populates="places")
    reviews = db.relationship(
        "Review",
        back_populates="place",
        cascade="all, delete-orphan",
    )
    amenities = db.relationship(
        "Amenity",
        secondary=place_amenity,
        backref=db.backref("places", lazy=True),
    )

    def __init__(self, title, description, price, latitude, longitude, owner):
        """Initialize a validated place and synchronize its relationships."""
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner

    @validates("title")
    def validate_title(self, key, value):
        """Validate and normalize the place title."""
        if not isinstance(value, str):
            raise ValueError("title is required and must be a non-empty string")
        value = value.strip()
        if not value:
            raise ValueError("title is required and must be a non-empty string")
        if len(value) > 100:
            raise ValueError("title must be at most 100 characters")
        return value

    @validates("description")
    def validate_description(self, key, value):
        """Normalize and validate the optional description."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        return value

    @validates("price")
    def validate_price(self, key, value):
        """Require a positive numeric nightly price."""
        if isinstance(value, bool):
            raise ValueError("Price must be a valid number.")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Price must be a valid number.") from exc
        if value <= 0:
            raise ValueError("Price must be greater than zero.")
        return value

    @validates("latitude")
    def validate_latitude(self, key, value):
        """Require a numeric latitude in the valid range."""
        if isinstance(value, bool):
            raise ValueError("Latitude must be a valid number.")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Latitude must be a valid number.") from exc
        if not -90.0 <= value <= 90.0:
            raise ValueError("Latitude must be between -90.0 and 90.0.")
        return value

    @validates("longitude")
    def validate_longitude(self, key, value):
        """Require a numeric longitude in the valid range."""
        if isinstance(value, bool):
            raise ValueError("Longitude must be a valid number.")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Longitude must be a valid number.") from exc
        if not -180.0 <= value <= 180.0:
            raise ValueError("Longitude must be between -180.0 and 180.0.")
        return value

    @validates("owner")
    def validate_owner(self, key, value):
        """Require a mapped User owner."""
        from app.models.user import User

        if not isinstance(value, User):
            raise TypeError("owner must be a User instance")
        return value

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
