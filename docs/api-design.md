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

## 2. Transcribe Audio

POST /api/transcribe

Input (`multipart/form-data`):

`file`: MP3 or 16-bit PCM WAV audio at 8 kHz or 16 kHz; maximum size 25 MB

Purpose:

Transcribe a local audio upload using DashScope Paraformer realtime ASR.
The temporary upload is removed after the request. The transcript is returned
to the client and is not analyzed by DeepSeek or stored in the database.

Response:

```json
{"transcript": "I need help with my account."}
```

Unsupported or invalid audio returns HTTP 400, oversized uploads return HTTP
413, and transcription-provider failures return HTTP 502.

---

## 3. Upload Tickets

POST /api/tickets/upload

Input (`multipart/form-data`):

`file`: CSV file

Required columns:

- ticket_id
- customer_message
- created_at

Purpose:

Upload customer support tickets for processing.

Parsed tickets are stored in the configured database.

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

## 4. Get Tickets

GET /api/tickets

Purpose:

Return processed tickets.

Returns the tickets saved by the upload endpoint.

---

## 5. Analytics

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

## 6. AI Query

POST /api/query

Purpose:

Allow users to ask questions about support tickets.

Example:

"What are the top customer complaints this week?"

Status:

Planned

---

## Audio Ticket Creation

POST /api/tickets/audio-upload

Input (`multipart/form-data`):

`file`: MP3 or 16-bit PCM WAV audio at 8 kHz or 16 kHz; maximum size 25 MB

Purpose:

Transcribe the local upload, analyze the transcript with the existing DeepSeek
ticket analysis service, and save the fully analyzed ticket in PostgreSQL. The
response uses the existing `TicketResponse` fields; `customer_message` contains
the transcript. The temporary audio file is deleted after the request.

Transcription or analysis failures return HTTP 502. Database persistence
failures return HTTP 500. Invalid uploads return HTTP 400 and oversized uploads
return HTTP 413.