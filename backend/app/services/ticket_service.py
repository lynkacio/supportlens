from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Ticket


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


def get_tickets(db: Session) -> list[Ticket]:
    return list(db.scalars(select(Ticket).order_by(Ticket.id)))
