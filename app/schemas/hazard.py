from pydantic import BaseModel


class HazardCreate(BaseModel):

    hazard_type: str
    title: str
    location: str
    latitude: float
    longitude: float
    severity: str = "warning"
    description: str = ""


class HazardResponse(HazardCreate):

    id: int
    status: str

    class Config:
        from_attributes = True