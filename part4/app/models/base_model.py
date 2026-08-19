#!/usr/bin/python3
"""Common mapped identity and timestamp behavior for domain models."""
import uuid
from datetime import datetime, timezone

from app import db


def utcnow():
    """Return the current UTC time without a timezone attached.

    ``datetime.utcnow`` is deprecated, but the mapped columns are naive,
    so the offset is stripped again to keep stored values comparable.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseModel(db.Model):
    """Provide identity, timestamps, and controlled attribute updates."""

    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=utcnow,
                           nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow,
                           onupdate=utcnow, nullable=False)

    def __init__(self):
        """Initialize a new instance with a unique id and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = utcnow()
        self.updated_at = utcnow()

    def save(self):
        """Refresh the modification timestamp."""
        self.updated_at = utcnow()

    def __eq__(self, other):
        """Compare mapped domain objects by concrete type and identity."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        """Hash mapped domain objects by concrete type and identity."""
        return hash((self.__class__, self.id))

    def update(self, data):
        """Update mutable attributes from a dictionary.

        Unknown, private, identity, and relationship attributes are ignored so
        that validation and relationship management cannot be bypassed.
        """
        if not isinstance(data, dict):
            raise TypeError("update data must be a dictionary")

        protected = {
            "id", "created_at", "owner_id", "place_id", "user_id"
        }
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
        """Return mapped scalar fields without ORM internals or relationships."""
        result = {}
        for attribute in self.__mapper__.column_attrs:
            key = attribute.key
            if key in {"password", "_password"}:
                continue
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        result["__class__"] = self.__class__.__name__
        return result
