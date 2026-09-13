from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import TicketResponse, UploadTicketsResponse
from app.services.csv_service import parse_ticket_csv
from app.services.ticket_service import get_tickets, save_tickets


PREVIEW_LIMIT = 5


router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)


@router.post("/upload", response_model=UploadTicketsResponse)
async def upload_tickets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadTicketsResponse:
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

    saved_tickets = save_tickets(db, tickets)

    return {
        "filename": file.filename,
        "tickets_processed": len(saved_tickets),
        "preview": [
            TicketResponse.model_validate(ticket).model_dump()
            for ticket in saved_tickets[:PREVIEW_LIMIT]
        ],
    }


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return get_tickets(db)