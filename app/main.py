from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.database.connection import (
    Base,
    engine
)

from app.api import (
    auth,
    routes,
    hazards,
    safe_zones,
    voice,
    health
)

from app.models import (
    user,
    hazard,
    safe_zone
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION,

    description=(
        "Backend Orchestrator for "
        "the NER-SAFE logistics and "
        "route intelligence platform."
    )
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://nex-safe.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)

app.include_router(routes.router)

app.include_router(hazards.router)

app.include_router(safe_zones.router)

app.include_router(voice.router)

app.include_router(health.router)


@app.get("/")
def root():

    return {

        "service": "NER-SAFE Backend",

        "status": "online",

        "docs": "/docs"
    }