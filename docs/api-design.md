# SupportLens API Design

Base URL:

http://localhost:8000

## 1. Health Check

GET /health

Response:

{
  "status": "ok",
  "service": "supportlens-api"
}

Purpose:

Verify that the backend service is running.

---

## 2. Upload Tickets

POST /api/tickets/upload

Input (`multipart/form-data`):

`file`: CSV file

Required columns:

- ticket_id
- customer_message
- created_at

Purpose:

Upload customer support tickets for processing.

Response:

{
  "filename": "tickets.csv",
  "tickets_processed": 2,
  "preview": [
    {
      "ticket_id": "T001",
      "customer_message": "I was charged twice",
      "created_at": "2026-09-10T09:15:00"
    }
  ]
}

The preview contains at most the first five parsed tickets. Empty files,
invalid UTF-8 files, files without ticket data, and files missing required
columns return HTTP 400.

---

## 3. Get Tickets

GET /api/tickets

Purpose:

Return processed tickets.

Status:

Planned

---

## 4. Analytics

GET /api/analytics

Purpose:

Return dashboard statistics such as:

- total tickets
- category counts
- high priority tickets
- common pain points

Status:

Planned

---

## 5. AI Query

POST /api/query

Purpose:

Allow users to ask questions about support tickets.

Example:

"What are the top customer complaints this week?"

Status:

Planned