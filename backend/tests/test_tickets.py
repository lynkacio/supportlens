import asyncio
import io
import os
import unittest
from xmlrpc import client

from app.main import app
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://test:test@localhost/test",
)

from app import database
from app.database import Base, create_tables
from app.models import Ticket
from app.routers.tickets import list_tickets, upload_tickets


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.engine = test_engine
database.SessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)
client = TestClient(app)


def make_upload(filename: str, content: str) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content.encode("utf-8")),
    )


class UploadTicketsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        create_tables()

    def setUp(self):
        self.db = database.SessionLocal()
        self.db.query(Ticket).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_upload_returns_count_and_preview(self):
        content = (
            "ticket_id,customer_message,created_at\n"
            "T001,First issue,2026-09-10T09:15:00\n"
            "T002,Second issue,2026-09-10T10:30:00\n"
        )

        response = asyncio.run(
            upload_tickets(make_upload("tickets.csv", content), self.db)
        )

        self.assertEqual(response["filename"], "tickets.csv")
        self.assertEqual(response["tickets_processed"], 2)
        self.assertEqual(len(response["preview"]), 2)
        self.assertEqual(response["preview"][0]["ticket_id"], "T001")

    def test_upload_rejects_empty_file(self):
        with self.assertRaisesRegex(HTTPException, "CSV file is empty"):
            asyncio.run(upload_tickets(make_upload("tickets.csv", "")))

    def test_upload_limits_preview_to_five_tickets(self):
        rows = "\n".join(
            f"T00{number},Issue {number},2026-09-10T09:15:00"
            for number in range(1, 7)
        )
        content = f"ticket_id,customer_message,created_at\n{rows}\n"

        response = asyncio.run(
            upload_tickets(make_upload("tickets.csv", content), self.db)
        )

        self.assertEqual(response["tickets_processed"], 6)
        self.assertEqual(len(response["preview"]), 5)

    def test_upload_persists_ticket_and_get_tickets_returns_it(self):
        content = (
            "ticket_id,customer_message,created_at\n"
            "T001,First issue,2026-09-10T09:15:00\n"
        )

        asyncio.run(upload_tickets(make_upload("tickets.csv", content), self.db))

        saved_tickets = list_tickets(self.db)

        self.assertEqual(len(saved_tickets), 1)
        self.assertEqual(saved_tickets[0].ticket_id, "T001")
        self.assertEqual(saved_tickets[0].created_at.year, 2026)
        self.assertIsNotNone(saved_tickets[0].processed_at)
        self.assertIsNone(saved_tickets[0].category)

    def test_upload_rejects_invalid_timestamp_without_partial_write(self):
        content = (
            "ticket_id,customer_message,created_at\n"
            "T001,Valid issue,2026-09-10T09:15:00\n"
            "T002,Invalid issue,not-a-timestamp\n"
        )

        with self.assertRaisesRegex(
            HTTPException,
            "created_at must be a valid ISO timestamp",
        ):
            asyncio.run(upload_tickets(make_upload("tickets.csv", content), self.db))

        self.assertEqual(self.db.query(Ticket).count(), 0)

    def test_upload_rejects_missing_required_columns(self):
        content = "ticket_id,customer_message\nT001,Missing date\n"

        with self.assertRaisesRegex(HTTPException, "Missing required columns"):
            asyncio.run(upload_tickets(make_upload("tickets.csv", content)))


def test_get_stats():
    # Setup: create some tickets with different categories and priorities
    response = client.get("/api/tickets/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unanalyzed" in data
    assert "by_category" in data
    assert "by_priority" in data

if __name__ == "__main__":
    unittest.main()