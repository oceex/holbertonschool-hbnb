# !/usr/bin/python3
"""Place module.

Defines the Place class, representing a listing owned by a User that
can be reviewed and can offer a set of Amenities.
"""
from sqlalchemy.orm import validates
from app import db
from app.models.Base_model import BaseModel

# Association table for the many-to-many relationship between
# Place and Amenity. This is a plain table (no model class needed)
# since it carries no extra data of its own beyond the two foreign keys.
place_amenity = db.Table(
    'place_amenity',
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
)


class Place(BaseModel):
    """Represents a place listed within the HBnB application."""

    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # -- Relationships -------------------------------------------------
    owner = db.relationship('User', backref=db.backref('places', lazy=True))
    reviews = db.relationship('Review', backref='place', lazy=True,
                               cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary=place_amenity,
                                 backref=db.backref('places', lazy=True),
                                 lazy=True)

    def __init__(self, title, description, price, latitude, longitude, owner):
        """Initialize a new Place instance.

        Args:
            title (str): Required title of the place (max 100 chars).
            description (str): Optional detailed description of the place.
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

    # -- Column validation -------------------------------------------
    # Runs automatically on assignment because these are real
    # db.Column attributes, not shadowed by a second set of
    # @property definitions.
    @validates('title')
    def validate_title(self, key, value):
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("title is required and must be a non-empty string")
        if len(value) > 100:
            raise ValueError("title must be at most 100 characters")
        return value

    @validates('price')
    def validate_price(self, key, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("price must be a valid number")
        if val < 0:
            raise ValueError("price cannot be negative")
        return val

    @validates('latitude')
    def validate_latitude(self, key, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("latitude must be a valid number")
        if not (-90.0 <= val <= 90.0):
            raise ValueError("latitude must be between -90.0 and 90.0")
        return val

    @validates('longitude')
    def validate_longitude(self, key, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("longitude must be a valid number")
        if not (-180.0 <= val <= 180.0):
            raise ValueError("longitude must be between -180.0 and 180.0")
        return val

    # -- Relationship helpers -------------------------------------------
    def add_review(self, review):
        """Associate a Review left for this place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Associate an Amenity offered by this place."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)
