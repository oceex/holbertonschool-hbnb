# !/usr/bin/python3
"""User module.

Defines the User class, representing an application user who can own
places and write reviews.
"""
import re
from sqlalchemy.orm import validates
from app import db, bcrypt
from app.models.Base_model import BaseModel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """Represents a user of the HBnB application."""

    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """Initialize a new User instance.

        Args:
            first_name (str): Required first name of the user (max 50 chars).
            last_name (str): Required last name of the user (max 50 chars).
            email (str): Required, must be a unique, valid email format.
            password (str): Required, plaintext password. It is hashed
                before being stored — see hash_password().
            is_admin (bool, optional): Administrative privilege flag.
                Defaults to False.
        """
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.hash_password(password)


    @validates('first_name', 'last_name')
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError(f"{key} is required and must be a string")
        if len(value) > 50:
            raise ValueError(f"{key} must be at most 50 characters")
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("email is required and must be a string")
        if not EMAIL_REGEX.match(value):
            raise ValueError("email must be a valid email address")
        return value

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        return value

    # -- Password handling ---------------------------------------------
    def hash_password(self, password):
        """Hash a plaintext password and store it.

        Use this (not direct assignment to .password) whenever a user
        sets or changes their password, so it's never stored in plaintext.
        """
        if not password or not isinstance(password, str):
            raise ValueError("password is required and must be a string")
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verify a plaintext password against the stored hash.

        Args:
            password (str): The plaintext password submitted at login.

        Returns:
            bool: True if it matches the stored hash, False otherwise.
        """
        return bcrypt.check_password_hash(self.password, password)

