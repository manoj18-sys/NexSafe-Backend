from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(20),
        unique=True,
        index=True
    )

    place = Column(
        String(150)
    )

    role = Column(
        String(50),
        default="driver"
    )