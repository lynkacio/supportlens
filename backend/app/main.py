from fastapi import FastAPI

from app.routers.tickets import router as tickets_router


app = FastAPI(
    title="SupportLens API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "supportlens-api",
    }


app.include_router(tickets_router)