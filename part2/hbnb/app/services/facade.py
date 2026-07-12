#!/usr/bin/python3
"""Facade module.

Implements the Facade pattern: a single entry point (HBnBFacade) that
the Presentation (API) layer talks to, hiding the details of how
business-logic objects are validated, related to each other, and
stored. This keeps the API layer thin and keeps persistence details
out of the models.
"""
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    """Single entry point coordinating models and repositories."""

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.get_user(user_id)
        if not user:
            return None
        return self.user_repo.update(user_id, user_data)

    # ------------------------------------------------------------------
    # Amenity
    # ------------------------------------------------------------------
    def create_amenity(self, amenity_data):
        amenity = Amenity(name=amenity_data.get("name"))
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        return self.amenity_repo.update(amenity_id, amenity_data)

    # ------------------------------------------------------------------
    # Place
    # ------------------------------------------------------------------
    def create_place(self, place_data):
        owner_id = place_data.get("owner_id")
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError(f"owner with id '{owner_id}' not found")

        place = Place(
            title=place_data.get("title"),
            description=place_data.get("description"),
            price=place_data.get("price"),
            latitude=place_data.get("latitude"),
            longitude=place_data.get("longitude"),
            owner=owner,
        )

        for amenity_id in place_data.get("amenities", []):
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                raise ValueError(
                    f"amenity with id '{amenity_id}' not found")
            place.add_amenity(amenity)

        return self.place_repo.add(place)

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.get_place(place_id)
        if not place:
            return None

        data = dict(place_data)
        amenity_ids = data.pop("amenities", None)
        owner_id = data.pop("owner_id", None)

        if owner_id is not None:
            owner = self.get_user(owner_id)
            if not owner:
                raise ValueError(f"owner with id '{owner_id}' not found")
            data["owner"] = owner

        updated_place = self.place_repo.update(place_id, data)

        if amenity_ids is not None:
            updated_place.amenities = []
            for amenity_id in amenity_ids:
                amenity = self.get_amenity(amenity_id)
                if not amenity:
                    raise ValueError(
                        f"amenity with id '{amenity_id}' not found")
                updated_place.add_amenity(amenity)

        return updated_place

    # ------------------------------------------------------------------
    # Review
    # ------------------------------------------------------------------
    def create_review(self, review_data):
        place = self.get_place(review_data.get("place_id"))
        if not place:
            raise ValueError(
                f"place with id '{review_data.get('place_id')}' not found")

        user = self.get_user(review_data.get("user_id"))
        if not user:
            raise ValueError(
                f"user with id '{review_data.get('user_id')}' not found")

        review = Review(
            text=review_data.get("text"),
            rating=review_data.get("rating"),
            place=place,
            user=user,
        )
        return self.review_repo.add(review)

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.get_place(place_id)
        if not place:
            raise ValueError(f"place with id '{place_id}' not found")
        return place.reviews

    def update_review(self, review_id, review_data):
        review = self.get_review(review_id)
        if not review:
            return None
        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        review = self.get_review(review_id)
        if not review:
            return False

        # Keep the related Place/User in sync
        if review in review.place.reviews:
            review.place.reviews.remove(review)
        if review in review.user.reviews:
            review.user.reviews.remove(review)

        return self.review_repo.delete(review_id)
