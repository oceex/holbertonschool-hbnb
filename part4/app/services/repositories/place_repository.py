"""Place-specific SQLAlchemy repository."""
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.models.place import Place
from app.persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    """Persist places and expose ownership queries."""

    def __init__(self):
        super().__init__(Place, (
            joinedload(Place.owner),
            selectinload(Place.amenities),
            selectinload(Place.reviews),
        ))

    def get_places_by_owner(self, owner_id):
        statement = db.select(Place).filter_by(owner_id=owner_id)
        return db.session.execute(statement).scalars().all()
