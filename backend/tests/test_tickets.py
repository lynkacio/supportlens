import asyncio
import io
import unittest

from fastapi import HTTPException, UploadFile

from app.database import SessionLocal, create_tables
from app.models import Ticket
from app.routers.tickets import upload_tickets


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
        self.db = SessionLocal()
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

    def test_upload_rejects_missing_required_columns(self):
        content = "ticket_id,customer_message\nT001,Missing date\n"

        with self.assertRaisesRegex(HTTPException, "Missing required columns"):
            asyncio.run(upload_tickets(make_upload("tickets.csv", content)))


if __name__ == "__main__":
    unittest.main()