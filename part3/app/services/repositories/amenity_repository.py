from app.models.Amenity import Amenity
from app import db
from app.persistence.repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Amenity)

    def get_amenity_by_name(self, name):
        return self.model.query.filter_by(name=name).first()

