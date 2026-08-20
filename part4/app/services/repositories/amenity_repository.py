"""Amenity-specific SQLAlchemy repository."""
from app.models.amenity import Amenity
from app.persistence.repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):
    """Persist amenities and expose name queries."""

    def __init__(self):
        super().__init__(Amenity)

    def get_amenity_by_name(self, name):
        return self.get_by_attribute("name", name)
