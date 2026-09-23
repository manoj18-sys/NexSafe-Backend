from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from app.database.connection import Base


class Hazard(Base):

    __tablename__ = "hazards"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hazard_type = Column(
        String(50),
        nullable=False
    )

    title = Column(
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

    severity = Column(
        String(30),
        default="warning"
    )

    description = Column(
        String(500)
    )

    status = Column(
        String(30),
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )