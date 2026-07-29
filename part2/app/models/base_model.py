#!/usr/bin/python3
"""Common identity and timestamp behavior for domain models."""
import uuid
from datetime import datetime


class BaseModel:
    """Provide identity, timestamps, and controlled attribute updates."""

    def __init__(self):
        """Initialize a new instance with a unique id and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Refresh the modification timestamp."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update mutable attributes from a dictionary.

        Unknown, private, identity, and relationship attributes are ignored so
        that validation and relationship management cannot be bypassed.
        """
        if not isinstance(data, dict):
            raise TypeError("update data must be a dictionary")

        protected = {"id", "created_at"}
        for key, value in data.items():
            if key in protected:
                continue
            # Backing fields would bypass property validation.
            if key.startswith("_"):
                continue
            # Relationship changes are coordinated by the facade and model helpers.
            if key in {"owner", "user", "place", "reviews", "places"}:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def to_dict(self):
        """Return a dictionary representation of the instance."""
        result = self.__dict__.copy()
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        result["__class__"] = self.__class__.__name__
        return result
