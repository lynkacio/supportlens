from datetime import datetime

from pydantic import BaseModel


class TicketPreview(BaseModel):
    ticket_id: str
    customer_message: str
    created_at: str


class TicketResponse(BaseModel):
    id: int
    ticket_id: str
    customer_message: str
    created_at: datetime
    category: str | None
    priority: str | None
    summary: str | None
    suggested_response: str | None
    processed_at: datetime

    model_config = {"from_attributes": True}


class UploadTicketsResponse(BaseModel):
    filename: str
    tickets_processed: int
    preview: list[TicketPreview]
