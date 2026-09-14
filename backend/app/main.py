import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.tickets import router as tickets_router

app = FastAPI(
    title="SupportLens API",
    version="0.1.0",
)

# Allow CORS for local development + frontend after deployment
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Optional: Override with environment variable (set in Render during deployment)
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "supportlens-api",
    }


app.include_router(tickets_router)