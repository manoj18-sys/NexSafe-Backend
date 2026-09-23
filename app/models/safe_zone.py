from sqlalchemy import (
    Column,
    Integer,
    String,
    Float
)

from app.database.connection import Base


class SafeZone(Base):

    __tablename__ = "safe_zones"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(200)
    )

    latitude = Column(
        Float
    )

    longitude = Column(
        Float
    )

    elevation = Column(
        Float
    )

    capacity = Column(
        Integer
    )

    status = Column(
        String(30),
        default="available"
    )