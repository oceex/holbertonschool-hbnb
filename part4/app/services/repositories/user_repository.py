"""User-specific SQLAlchemy repository."""
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """Persist users and expose user-focused queries."""

    def __init__(self):
        super().__init__(User, (
            selectinload(User.places),
            selectinload(User.reviews),
        ))

    def get_user_by_email(self, email):
        return self.get_by_attribute("email", email)
