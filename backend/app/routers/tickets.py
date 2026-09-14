from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Ticket
from app.schemas import TicketPreview, TicketResponse, UploadTicketsResponse, AnalysisReportResponse, TicketStatsResponse
from app.services.csv_service import parse_ticket_csv
from app.services.ticket_service import (
    TicketPersistenceError,
    TicketValidationError,
    get_tickets,
    save_tickets,
    analyze_pending_tickets
    )

import logging


PREVIEW_LIMIT = 5

logger = logging.getLogger(__name__)

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

    try:
        saved_tickets = save_tickets(db, tickets)
    except TicketValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail="created_at must be a valid ISO timestamp",
        ) from exc
    except TicketPersistenceError as exc:
        raise HTTPException(
            status_code=500,
            detail="Tickets could not be saved",
        ) from exc

    return {
        "filename": file.filename,
        "tickets_processed": len(saved_tickets),
        "preview": [
            TicketPreview(
                ticket_id=ticket.ticket_id,
                customer_message=ticket.customer_message,
                created_at=ticket.created_at.isoformat(),
            ).model_dump()
            for ticket in saved_tickets[:PREVIEW_LIMIT]
        ],
    }


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return get_tickets(db)


@router.post("/analyze", response_model=AnalysisReportResponse)
def analyze_tickets(db: Session = Depends(get_db)) -> AnalysisReportResponse:
    """Analyze all not-yet-analyzed tickets. Idempotent — safe to call repeatedly."""
    return analyze_pending_tickets(db)


@router.get("/stats", response_model=TicketStatsResponse)
def get_stats(db: Session = Depends(get_db)) -> TicketStatsResponse:
    # Return all statistics: idempotent, cacheable
    total = db.query(Ticket).count()
    unanalyzed = db.query(Ticket).filter(Ticket.category.is_(None)).count()

    by_category = {
        str(k): v for k, v in db.query(
            Ticket.category,
            func.count(Ticket.id)
        )
        .group_by(Ticket.category)
        .all()
        if k is not None
    }

    by_priority = {
        str(k): v for k, v in db.query(
            Ticket.priority,
            func.count(Ticket.id)
        )
        .group_by(Ticket.priority)
        .all()
        if k is not None
    }

    return TicketStatsResponse(
        total=total,
        unanalyzed=unanalyzed,
        by_category=by_category,
        by_priority=by_priority,
    )
    
    
@router.post("/query")
def query_tickets(payload: dict, db: Session = Depends(get_db)):
    question = payload.get("question", "")

    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="question is required")

    # 1. Retrieve relevant tickets: prefer analyzed + high priority + most recent
    tickets = (
        db.query(Ticket)
        .filter(Ticket.category.isnot(None))
        .order_by(
            Ticket.priority.desc(),   # urgent > high etc. (psycopg sorts alphabetically, not perfect but usable)
            Ticket.created_at.desc()
        )
        .limit(10)
        .all()
    )

    if not tickets:
        return {"answer": "There are no analyzed tickets in the database. Please upload a CSV and call the analysis endpoint first.", "tickets": []}

    # 2. Build the context to send to the LLM
    ticket_context = "\n".join(
        f"- [{t.ticket_id}] (priority={t.priority}, category={t.category}) "
        f"{t.customer_message[:200]}"
        for t in tickets
    )

    # 3. Call the LLM to answer
    try:
        from app.services.llm_service import answer_question, LLMServiceError
        answer = answer_question(question, ticket_context)
    except LLMServiceError as exc:
        logger.exception("LLM query failed")
        return {"answer": f"AI is temporarily unable to answer this question: {exc}", "tickets": []}

    return {
        "answer": answer,
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "priority": t.priority,
                "category": t.category,
                "message": t.customer_message[:100],
            }
            for t in tickets[:5]
        ],
    }