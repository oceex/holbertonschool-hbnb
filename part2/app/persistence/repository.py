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
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)
        return obj

    def delete(self, obj_id):
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


