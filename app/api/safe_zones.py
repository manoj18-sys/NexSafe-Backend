from fastapi import APIRouter


router = APIRouter(
    prefix="/safe-zones",
    tags=["Safe Zones"]
)


@router.get("")
def get_safe_zones():

    return [

        {
            "id": 1,
            "name": "Gangtok Safe Zone",
            "location": "Gangtok, Sikkim",
            "latitude": 27.3389,
            "longitude": 88.6065,
            "elevation": 1650,
            "capacity": 120,
            "status": "available"
        },

        {
            "id": 2,
            "name": "Shillong Safe Zone",
            "location": "Shillong, Meghalaya",
            "latitude": 25.5788,
            "longitude": 91.8933,
            "elevation": 1496,
            "capacity": 90,
            "status": "available"
        }

    ]


@router.get("/nearest")
def nearest_safe_zone(
    latitude: float,
    longitude: float
):

    return {

        "name": "Nearest Safe Zone",

        "latitude": 27.3389,

        "longitude": 88.6065,

        "distance_km": 12.4
    }