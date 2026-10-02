import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Ticket
from app.schemas import AnalysisReportResponse
from app.services.llm_service import LLMServiceError, analyze_ticket

logger = logging.getLogger(__name__)
TICKET_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"



class TicketPersistenceError(Exception):
    pass


class TicketValidationError(Exception):
    pass


def save_tickets(db: Session, tickets: list[dict[str, str]]) -> list[Ticket]:
    records = []

    try:
        for ticket in tickets:
            created_at = datetime.fromisoformat(ticket["created_at"])
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            records.append(
                Ticket(
                    ticket_id=ticket["ticket_id"],
                    customer_message=ticket["customer_message"],
                    created_at=created_at,
                    processed_at=datetime.now(timezone.utc),
                )
            )

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)
    except ValueError as exc:
        db.rollback()
        raise TicketValidationError("Ticket timestamp is invalid") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise TicketPersistenceError("Tickets could not be saved") from exc

    return records


def create_analyzed_ticket_from_message(
    db: Session,
    customer_message: str,
) -> Ticket:
    try:
        analysis = analyze_ticket(customer_message)
    except Exception as exc:
        logger.exception("LLM analysis failed for audio transcript")
        if isinstance(exc, LLMServiceError):
            raise
        raise LLMServiceError("Ticket analysis failed") from exc

    created_at = datetime.now(timezone.utc)

    suffix = "".join(
        secrets.choice(TICKET_ID_ALPHABET)
        for _ in range(4)
    )

    ticket = Ticket(
        ticket_id=f"AUD-{created_at.strftime('%Y%m%d')}-{suffix}",
        customer_message=customer_message,
        created_at=created_at,
        processed_at=created_at,
        category=analysis.category.value,
        priority=analysis.priority.value,
        summary=analysis.summary,
        suggested_response=analysis.suggested_response,
    )

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to persist audio ticket ticket_id=%s", ticket.ticket_id)
        raise TicketPersistenceError("Ticket could not be saved") from exc

    return ticket


def get_tickets(db: Session) -> list[Ticket]:
    return list(db.scalars(select(Ticket).order_by(Ticket.id)))


def analyze_pending_tickets(db: Session) -> AnalysisReportResponse:
    """Analyze tickets that have no category yet, one at a time, writing back per ticket.

    Per-ticket isolation: any single failure neither blocks nor rolls back the others.
    """
    pending = (
        db.query(Ticket)
        .filter(Ticket.category.is_(None))
        .order_by(Ticket.id)
        .all()
    )

    analyzed = 0
    failed: list[str] = []

    for ticket in pending:
        # ── LLM call: failure affects only this ticket ──────────
        try:
            result = analyze_ticket(ticket.customer_message)
        except LLMServiceError as exc:
            logger.warning("LLM analysis failed ticket_id=%s: %s", ticket.ticket_id, exc)
            failed.append(ticket.ticket_id)
            continue

        ticket.category = result.category.value
        ticket.priority = result.priority.value
        ticket.summary = result.summary
        ticket.suggested_response = result.suggested_response

        # ── Write-back: one commit per ticket ───────────────────
        try:
            db.commit()
            analyzed += 1
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Failed to persist analysis ticket_id=%s", ticket.ticket_id)
            failed.append(ticket.ticket_id)

    return AnalysisReportResponse(analyzed=analyzed, failed=failed)