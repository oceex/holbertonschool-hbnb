# !/usr/bin/python3
"""Review module.

Defines the Review class, representing feedback a User leaves for a
Place.
"""
from sqlalchemy.orm import validates
from app import db
from app.models.Base_model import BaseModel


class Review(BaseModel):
    """Represents a review left by a user for a place."""

    __tablename__ = 'reviews'

    text = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __init__(self, text, rating, place, user):
        """Initialize a new Review instance.

        Args:
            text (str): Required content of the review.
            rating (int): Must be between 1 and 5.
            place (Place): The Place instance being reviewed.
            user (User): The User instance who wrote the review.
        """
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user


    @validates('text')
    def validate_text(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("text is required and must be a string")
        return value

    @validates('rating')
    def validate_rating(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("rating must be an integer")
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        return value
