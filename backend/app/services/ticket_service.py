from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ticket


def save_tickets(db: Session, tickets: list[dict[str, str]]) -> list[Ticket]:
    records = [Ticket(**ticket) for ticket in tickets]
    db.add_all(records)
    db.commit()

    for record in records:
        db.refresh(record)

    return records


def get_tickets(db: Session) -> list[Ticket]:
    return list(db.scalars(select(Ticket).order_by(Ticket.id)))
