from app.models.Place import Place
from app import db
from app.persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Place)

    def get_places_by_owner(self, owner_id):
        return self.model.query.filter_by(owner_id=owner_id).all()
