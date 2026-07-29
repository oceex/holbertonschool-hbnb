from app.models.Review import Review
from app import db
from app.persistence.repository import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Review)

    def get_reviews_by_place(self, place_id):
        return self.model.query.filter_by(place_id=place_id).all()

    def get_review_by_place_and_user(self, place_id, user_id):
        return self.model.query.filter_by(place_id=place_id, user_id=user_id).first()
