"""Standalone validation models for users, places, and reviews."""

import re


class User:
    """Represent a user with validated names and email."""

    def __init__(self, first_name, last_name, email):
        """Initialize a user from validated, normalized values."""
        self.first_name = self.validate_name(first_name, "First name")
        self.last_name = self.validate_name(last_name, "Last name")
        self.email = self.validate_email(email)

    def validate_name(self, name, field_name):
        """Return a non-empty, normalized name."""
        if not name or name.strip() == "":
            raise ValueError(f"{field_name} cannot be empty")
        return name.strip()

    def validate_email(self, email):
        """Return a normalized email address with a valid basic format."""
        if not email or email.strip() == "":
            raise ValueError("Email cannot be empty")
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email.strip()):
            raise ValueError("Invalid email format")
        return email.strip()


class Place:
    """Represent a place with validated pricing and coordinates."""

    def __init__(self, title, price, latitude, longitude):
        """Initialize a place from validated values."""
        self.title = self.validate_title(title)
        self.price = self.validate_price(price)
        self.latitude = self.validate_latitude(latitude)
        self.longitude = self.validate_longitude(longitude)

    def validate_title(self, title):
        """Return a non-empty, normalized title."""
        if not title or title.strip() == "":
            raise ValueError("Title cannot be empty")
        return title.strip()

    def validate_price(self, price):
        """Return a strictly positive price."""
        if price <= 0:
            raise ValueError("Price must be a positive number")
        return price

    def validate_latitude(self, lat):
        """Return a latitude within the inclusive geographic range."""
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return lat

    def validate_longitude(self, lon):
        """Return a longitude within the inclusive geographic range."""
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return lon


class Review:
    """Represent review text linked to registered user and place IDs."""

    def __init__(self, text, user_id, place_id, valid_users, valid_places):
        """Initialize a review after validating its text and references."""
        self.text = self.validate_text(text)
        self.user_id = self.validate_entity(user_id, valid_users, "User")
        self.place_id = self.validate_entity(place_id, valid_places, "Place")

    def validate_text(self, text):
        """Return non-empty, normalized review text."""
        if not text or text.strip() == "":
            raise ValueError("Review text cannot be empty")
        return text.strip()

    def validate_entity(self, entity_id, valid_entities_dict, entity_name):
        """Return an ID that exists in the supplied entity mapping."""
        if entity_id not in valid_entities_dict:
            raise ValueError(f"{entity_name} ID must reference a valid registered entity")
        return entity_id
