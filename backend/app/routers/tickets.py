from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.csv_service import parse_ticket_csv


PREVIEW_LIMIT = 5


router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)


@router.post("/upload")
async def upload_tickets(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted",
        )

    try:
        content = await file.read()
        tickets = parse_ticket_csv(content)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "filename": file.filename,
        "tickets_processed": len(tickets),
        "preview": tickets[:PREVIEW_LIMIT],
    }