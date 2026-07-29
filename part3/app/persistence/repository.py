#!/usr/bin/python3
"""Persistence contract and SQLAlchemy repository implementation."""
from abc import ABC, abstractmethod
from contextlib import nullcontext

from flask import has_app_context

from app import db


class Repository(ABC):
    """Abstract interface every persistence backend must implement."""

    @abstractmethod
    def add(self, obj):
        """Store a new object."""

    @abstractmethod
    def get(self, obj_id):
        """Return an object by ID, or None when it does not exist."""

    @abstractmethod
    def get_all(self):
        """Retrieve all stored objects."""

    @abstractmethod
    def update(self, obj_id, data):
        """Update an object by ID and return the updated object."""

    @abstractmethod
    def delete(self, obj_id):
        """Delete an object by ID and report whether it existed."""

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """Return the first object whose named attribute matches a value."""


class SQLAlchemyRepository(Repository):
    """Persist one mapped model type through the shared database session."""

    def __init__(self, model, load_options=()):
        self.model = model
        self.load_options = tuple(load_options)
        self.app = getattr(db, "_hbnb_default_app", None)

    def _app_context(self):
        """Use the active app, or the factory's app for legacy direct calls."""
        if has_app_context():
            return nullcontext()
        if self.app is None:
            raise RuntimeError("Repository operation requires an application")
        return self.app.app_context()

    def add(self, obj):
        """Add and commit an object, rolling back a failed transaction."""
        with self._app_context():
            try:
                db.session.add(obj)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return obj

    def get(self, obj_id):
        """Return an object by primary key, or None when absent."""
        with self._app_context():
            statement = db.select(self.model).where(self.model.id == obj_id)
            if self.load_options:
                statement = statement.options(*self.load_options)
            return db.session.execute(statement).scalars().first()

    def get_all(self):
        """Return every persisted object for this model."""
        with self._app_context():
            statement = db.select(self.model)
            if self.load_options:
                statement = statement.options(*self.load_options)
            return db.session.execute(statement).scalars().all()

    def update(self, obj_id, data):
        """Apply validated model updates and commit them atomically."""
        with self._app_context():
            obj = self.get(obj_id)
            if obj is None:
                return None
            try:
                obj.update(data)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
            return obj

    def delete(self, obj_id):
        """Delete and commit an object, rolling back on failure."""
        with self._app_context():
            obj = self.get(obj_id)
            if obj is None:
                return False
            try:
                db.session.delete(obj)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
            return True

    def get_by_attribute(self, attr_name, attr_value):
        """Return the first object with a matching mapped attribute."""
        if not hasattr(self.model, attr_name):
            return None
        with self._app_context():
            statement = db.select(self.model).filter_by(
                **{attr_name: attr_value}
            )
            if self.load_options:
                statement = statement.options(*self.load_options)
            return db.session.execute(statement).scalars().first()
