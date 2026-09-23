from pydantic import BaseModel


class RouteRequest(BaseModel):
    origin: str
    destination: str


class RouteAnalysis(BaseModel):
    origin: str
    destination: str
    path: list[str]
    distance_km: float
    estimated_minutes: int
    risk_level: str
    route_status: str
    alternate_available: bool
    recommended_action: str