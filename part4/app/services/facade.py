#!/usr/bin/python3
"""Service facade coordinating domain models and persistence."""
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.services.repositories.amenity_repository import AmenityRepository
from app.services.repositories.place_repository import PlaceRepository
from app.services.repositories.review_repository import ReviewRepository
from app.services.repositories.user_repository import UserRepository


class HBnBFacade:
    """Coordinate domain validation, relationships, and repositories."""

    def __init__(self):
        """Initialize one SQLAlchemy repository per mapped entity type."""
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    def create_user(self, user_data):
        """Create a user, enforcing repository-scoped email uniqueness."""
        email = user_data.get("email")
        if isinstance(email, str) and self.get_user_by_email(email.strip()):
            raise ValueError("Email already registered")
        # Present construction errors through the facade's validation contract.
        try:
            user = User(**user_data)
        except TypeError as exc:
            raise ValueError(str(exc)) from exc
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Return a user by ID, or ``None`` when not found."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Return the user with a normalized email address, if any."""
        if isinstance(email, str):
            email = email.strip()
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        """Return all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Update a user while preserving email uniqueness."""
        user = self.get_user(user_id)
        if not user:
            return None
        new_email = user_data.get("email")
        if isinstance(new_email, str) and new_email.strip() != user.email:
            existing = self.get_user_by_email(new_email)
            if existing and existing.id != user_id:
                raise ValueError("Email already registered")
        return self.user_repo.update(user_id, user_data)

    def create_amenity(self, amenity_data):
        """Create an amenity with an optional description."""
        amenity = Amenity(
            name=amenity_data.get("name"),
            description=amenity_data.get("description", "")
        )
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        """Return an amenity by ID, or ``None`` when not found."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Return all amenities."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Update an amenity, or return ``None`` when not found."""
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        return self.amenity_repo.update(amenity_id, amenity_data)

    def create_place(self, place_data):
        """Create and persist a place.

        All amenity IDs are resolved before the owner relationship is mutated.
        Invalid owner or amenity IDs raise ``ValueError``.
        """
        owner_id = place_data.get("owner_id")
        owner = self.get_user(owner_id)
        if not owner:
            raise ValueError(f"User with id '{owner_id}' not found.")

        # Resolve all dependencies first to avoid partial relationship updates.
        resolved_amenities = []
        for amenity_id in place_data.get("amenities", []):
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                raise ValueError(f"Amenity with id '{amenity_id}' not found.")
            if amenity not in resolved_amenities:
                resolved_amenities.append(amenity)

        place = Place(
            title=place_data.get("title"),
            description=place_data.get("description", ""),
            price=place_data.get("price"),
            latitude=place_data.get("latitude"),
            longitude=place_data.get("longitude"),
            owner=owner
        )

        for amenity in resolved_amenities:
            place.add_amenity(amenity)

        return self.place_repo.add(place)

    def get_place(self, place_id):
        """Return a place by ID, or ``None`` when not found."""
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Return all places."""
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Update a place and optionally replace its amenities.

        Amenity IDs are validated before the place is mutated. The input mapping
        is copied so callers do not observe internal key removal.
        """
        place = self.get_place(place_id)
        if not place:
            return None

        data = place_data.copy()
        amenity_ids = data.pop("amenities", None)

        resolved_amenities = None
        if amenity_ids is not None:
            # Resolve the complete replacement before mutating the place.
            resolved_amenities = []
            for amenity_id in amenity_ids:
                amenity = self.get_amenity(amenity_id)
                if not amenity:
                    raise ValueError(
                        f"Amenity with id '{amenity_id}' not found.")
                if amenity not in resolved_amenities:
                    resolved_amenities.append(amenity)

        if resolved_amenities is not None:
            # The repository commits this relationship change with scalar data.
            place.amenities = resolved_amenities

        return self.place_repo.update(place_id, data)

    def delete_place(self, place_id):
        """Delete a place and let mapped relationships synchronize."""
        place = self.get_place(place_id)
        if not place:
            return False
        return self.place_repo.delete(place_id)

    def create_review(self, review_data):
        """Create and persist a review.

        The place and user must exist, a user may not review their own
        place, and a user may review each place only once. Violations raise
        ``ValueError``.
        """
        place = self.get_place(review_data.get("place_id"))
        if not place:
            raise ValueError(
                f"place with id '{review_data.get('place_id')}' not found")

        user = self.get_user(review_data.get("user_id"))
        if not user:
            raise ValueError(
                f"user with id '{review_data.get('user_id')}' not found")

        if place.owner and str(place.owner.id) == str(user.id):
            raise ValueError("You cannot review your own place")

        existing_review = self.review_repo.get_review_by_place_and_user(
            place.id,
            user.id,
        )
        if existing_review:
            raise ValueError("You have already reviewed this place")

        review = Review(
            text=review_data.get("text"),
            rating=review_data.get("rating"),
            place=place,
            user=user,
        )
        return self.review_repo.add(review)

    def get_review(self, review_id):
        """Return a review by ID, or ``None`` when not found."""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Return all reviews."""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """Return reviews for a place, raising ``ValueError`` if it is absent."""
        place = self.get_place(place_id)
        if not place:
            raise ValueError(f"place with id '{place_id}' not found")
        return self.review_repo.get_reviews_by_place(place_id)

    def update_review(self, review_id, review_data):
        """Update a review, or return ``None`` when not found."""
        review = self.get_review(review_id)
        if not review:
            return None
        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        """Delete a review and let mapped relationships synchronize."""
        review = self.get_review(review_id)
        if not review:
            return False

        return self.review_repo.delete(review_id)
