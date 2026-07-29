#!/usr/bin/python3
"""Persistence contracts and an in-memory repository implementation."""
from abc import ABC, abstractmethod


class Repository(ABC):
    """Abstract interface every persistence backend must implement."""

    @abstractmethod
    def add(self, obj):
        """Store a new object."""
        pass

    @abstractmethod
    def get(self, obj_id):
        """Return an object by ID, or ``None`` when it does not exist."""
        pass

    @abstractmethod
    def get_all(self):
        """Retrieve all stored objects."""
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """Update an object by ID and return the updated object."""
        pass

    @abstractmethod
    def delete(self, obj_id):
        """Delete an object by ID and report whether it existed."""
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """Return the first object whose named attribute matches a value."""
        pass


class InMemoryRepository(Repository):
    """Store objects in memory, keyed by object ID."""

    def __init__(self):
        """Initialize an empty repository."""
        self._storage = {}

    def add(self, obj):
        """Store an object, rejecting duplicate IDs."""
        if obj.id in self._storage:
            raise ValueError(f"object with id '{obj.id}' already exists")
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        """Return an object by ID, or ``None`` when it does not exist."""
        return self._storage.get(obj_id)

    def get_all(self):
        """Return a snapshot list of all stored objects."""
        return list(self._storage.values())

    def update(self, obj_id, data):
        """Update an object, or return ``None`` when its ID is absent."""
        obj = self.get(obj_id)
        if not obj:
            return None
        obj.update(data)
        return obj

    def delete(self, obj_id):
        """Delete an object and report whether it existed."""
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        """Return the first object with a matching attribute value."""
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name, None) == attr_value),
            None
        )


