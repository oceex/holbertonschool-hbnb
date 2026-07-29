#!/usr/bin/python3
"""Review model and validation rules."""
from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    """Represents a review left by a user for a place."""

    def __init__(self, text, rating, place, user):
        """Initialize a review and synchronize its place and author."""
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

        # Keep both relationship collections synchronized.
        self.place.add_review(self)
        self.user.add_review(self)

    @property
    def text(self):
        """str: The normalized review text."""
        return self._text

    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise ValueError("text is required and must be a string")
        value = value.strip()
        if not value:
            raise ValueError("text is required and must be a string")
        self._text = value

    @property
    def rating(self):
        """int: The rating from 1 through 5."""
        return self._rating

    @rating.setter
    def rating(self, value):
        # bool is an int subclass but is not a meaningful rating.
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("rating must be an integer")
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        self._rating = value

    @property
    def place(self):
        """Place: The reviewed place."""
        return self._place

    @place.setter
    def place(self, value):
        if not isinstance(value, Place):
            raise ValueError("place must be a valid Place instance")
        self._place = value

    @property
    def user(self):
        """User: The review author."""
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("user must be a valid User instance")
        self._user = value
