from pydantic import BaseModel


class LoginRequest(BaseModel):

    name: str
    phone: str
    place: str


class LoginResponse(BaseModel):

    user_id: int
    name: str
    phone: str
    place: str
    role: str