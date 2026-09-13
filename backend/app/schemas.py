from pydantic import BaseModel


class TicketResponse(BaseModel):
    ticket_id: str
    customer_message: str
    created_at: str

    model_config = {"from_attributes": True}


class UploadTicketsResponse(BaseModel):
    filename: str
    tickets_processed: int
    preview: list[TicketResponse]
