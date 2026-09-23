from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["System"]
)


@router.get("")
def health_check():

    return {

        "status": "online",

        "service": "NER-SAFE Backend",

        "version": "1.0.0"
    }