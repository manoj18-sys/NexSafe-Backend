from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.phone == data.phone)
        .first()
    )

    if not user:

        user = User(
            name=data.name,
            phone=data.phone,
            place=data.place,
            role="driver"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return LoginResponse(
        user_id=user.id,
        name=user.name,
        phone=user.phone,
        place=user.place,
        role=user.role
    )