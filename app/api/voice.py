from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)


router = APIRouter(
    prefix="/voice",
    tags=["AI Voice"]
)


@router.post("/process")
async def process_voice(

    audio: UploadFile = File(...),

    language: str = Form("en")
):

    contents = await audio.read()

    return {

        "status": "received",

        "filename": audio.filename,

        "language": language,

        "audio_size": len(contents),

        "message": (
            "Voice processing pipeline "
            "received the audio."
        ),

        "transcript": None,

        "response_text": (
            "Voice request received. "
            "AI processing will be connected next."
        ),

        "audio_url": None
    }