from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(255), index=True)
    customer_message: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String(255))
