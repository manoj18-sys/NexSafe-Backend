from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.hazard import Hazard
from app.schemas.hazard import HazardResponse


router = APIRouter(
    prefix="/hazards",
    tags=["Hazards"]
)


@router.get(
    "",
    response_model=list[HazardResponse]
)
def get_hazards(
    db: Session = Depends(get_db)
):

    return (
        db.query(Hazard)
        .order_by(Hazard.created_at.desc())
        .all()
    )


@router.post("/report")
async def report_hazard(

    hazard_type: str = Form(...),
    title: str = Form(...),
    location: str = Form(...),

    latitude: float = Form(...),
    longitude: float = Form(...),

    severity: str = Form("warning"),

    description: str = Form(""),

    photo: UploadFile | None = File(None),

    voice: UploadFile | None = File(None),

    db: Session = Depends(get_db)
):

    hazard = Hazard(

        hazard_type=hazard_type,

        title=title,

        location=location,

        latitude=latitude,

        longitude=longitude,

        severity=severity,

        description=description,

        status="active"
    )

    db.add(hazard)

    db.commit()

    db.refresh(hazard)

    return {

        "message": "Hazard report received",

        "hazard_id": hazard.id,

        "photo_received": photo is not None,

        "voice_received": voice is not None,

        "location": {
            "latitude": latitude,
            "longitude": longitude
        }
    }