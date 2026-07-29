#!/usr/bin/python3
"""BaseModel module.

Defines the BaseModel class, which provides common attributes
(id, created_at, updated_at) and common behavior (save, update, to_dict)
shared by all business logic entities (User, Place, Review, Amenity).
"""
from app import db
import uuid
from datetime import datetime

class BaseModel(db.Model):
    """Base class that all business logic entities inherit from."""
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self):
        """Initialize a new instance with a unique id and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Update the updated_at timestamp whenever the object is modified."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update the attributes of the object from a dictionary.

        Args:
            data (dict): Dictionary of attribute names/values to update.
                Keys that do not correspond to an existing attribute are
                ignored, and the 'id' and 'created_at' attributes are
                protected from being overwritten.
        """
        protected = {"id", "created_at"}
        for key, value in data.items():
            if key in protected:
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
