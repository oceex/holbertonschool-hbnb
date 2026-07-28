#!/usr/bin/python3
"""Repository module.

Defines the Repository interface (the persistence contract used by the
Facade / API layers) and an in-memory implementation backed by a plain
dict. Swapping this out for a database-backed repository later should
not require any changes to the Facade or API code, since they only
depend on this interface.
"""
from abc import ABC, abstractmethod


class Repository(ABC):
    """Abstract interface every persistence backend must implement."""

    @abstractmethod
    def add(self, obj):
        """Store a new object."""
        pass

    @abstractmethod
    def get(self, obj_id):
        """Retrieve an object by id, or None if not found."""
        pass

    @abstractmethod
    def get_all(self):
        """Retrieve all stored objects."""
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """Update an object identified by obj_id with a dict of data."""
        pass

    @abstractmethod
    def delete(self, obj_id):
        """Delete an object identified by obj_id."""
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """Retrieve the first object whose attr_name equals attr_value."""
        pass


class InMemoryRepository(Repository):
    """Simple dict-backed repository, keyed by object id."""

    def __init__(self):
        self._storage = {}

    def add(self, obj):
        # The old repository silently overwrote objects with the same id.
        # Rejecting duplicates keeps ids unique and exposes bad insertions early.
        if obj.id in self._storage:
            raise ValueError(f"object with id '{obj.id}' already exists")
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        # Missing ids should be handled cleanly without leaking KeyError.
        # dict.get returns None, matching the repository contract.
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        # The previous logic was correct for found objects but implicit for missing ones.
        # Returning None clearly communicates that no update occurred.
        if not obj:
            return None
        obj.update(data)
        return obj

    def delete(self, obj_id):
        # The old delete behavior already avoided KeyError; keep it explicit.
        # Returning a boolean lets the facade distinguish missing objects.
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name, None) == attr_value),
            None
        )


