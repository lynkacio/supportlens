import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.tickets import router as tickets_router
from app.routers.transcription import router as transcription_router

app = FastAPI(
    title="SupportLens API",
    version="0.1.0",
)

origins = [
    "https://supportlens-gold.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "supportlens-api",
    }


app.include_router(tickets_router)
app.include_router(transcription_router)