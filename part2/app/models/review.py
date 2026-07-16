#!/usr/bin/python3
"""Review module.

Defines the Review class, representing feedback a User leaves for a
Place.
"""
from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    """Represents a review left by a user for a place."""

    def __init__(self, text, rating, place, user):
        """Initialize a Review.

        Args:
            text (str): Required content of the review.
            rating (int): Must be between 1 and 5.
            place (Place): The Place instance being reviewed.
            user (User): The User instance who wrote the review.
        """
        super().__init__()
        self.place = place
        self.user = user
        self.text = text
        self.rating = rating

        # Keep the related Place and User in sync with this review
        self.place.add_review(self)
        self.user.add_review(self)

    # -- Validated properties -------------------------------------------
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("text is required and must be a string")
        self._text = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("rating must be an integer")
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        self._rating = value

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, value):
        if not isinstance(value, Place):
            raise ValueError("place must be a valid Place instance")
        self._place = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("user must be a valid User instance")
        self._user = value
