import re

class User:
    def __init__(self, first_name, last_name, email):
        self.first_name = self.validate_name(first_name, "First name")
        self.last_name = self.validate_name(last_name, "Last name")
        self.email = self.validate_email(email)

    def validate_name(self, name, field_name):
        if not name or name.strip() == "":
            raise ValueError(f"{field_name} cannot be empty")
        return name.strip()

    def validate_email(self, email):
        if not email or email.strip() == "":
            raise ValueError("Email cannot be empty")
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email.strip()):
            raise ValueError("Invalid email format")
        return email.strip()


class Place:
    def __init__(self, title, price, latitude, longitude):
        self.title = self.validate_title(title)
        self.price = self.validate_price(price)
        self.latitude = self.validate_latitude(latitude)
        self.longitude = self.validate_longitude(longitude)

    def validate_title(self, title):
        if not title or title.strip() == "":
            raise ValueError("Title cannot be empty")
        return title.strip()

    def validate_price(self, price):
        if price <= 0:
            raise ValueError("Price must be a positive number")
        return price

    def validate_latitude(self, lat):
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return lat

    def validate_longitude(self, lon):
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return lon


class Review:
    def __init__(self, text, user_id, place_id, valid_users, valid_places):
        self.text = self.validate_text(text)
        self.user_id = self.validate_entity(user_id, valid_users, "User")
        self.place_id = self.validate_entity(place_id, valid_places, "Place")

    def validate_text(self, text):
        if not text or text.strip() == "":
            raise ValueError("Review text cannot be empty")
        return text.strip()

    def validate_entity(self, entity_id, valid_entities_dict, entity_name):
        if entity_id not in valid_entities_dict:
            raise ValueError(f"{entity_name} ID must reference a valid registered entity")
        return entity_id
