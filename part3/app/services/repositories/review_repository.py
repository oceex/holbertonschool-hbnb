"""Review-specific SQLAlchemy repository."""
from app import db
from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository):
    """Persist reviews and expose relationship queries."""

    def __init__(self):
        super().__init__(Review)

    def get_reviews_by_place(self, place_id):
        statement = db.select(Review).filter_by(place_id=place_id)
        return db.session.execute(statement).scalars().all()

    def get_review_by_place_and_user(self, place_id, user_id):
        statement = db.select(Review).filter_by(
            place_id=place_id,
            user_id=user_id,
        )
        return db.session.execute(statement).scalars().first()
