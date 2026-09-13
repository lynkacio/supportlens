## Database Persistence Architecture

### Goal

The next development milestone is to persist validated customer-support tickets in PostgreSQL.

The existing CSV upload and validation behavior must continue to work.

The scope of this milestone is database persistence only.

LLM analysis, dashboard analytics, AI query functionality, authentication, and cloud deployment are not part of this milestone.

### Technology

The backend database layer will use:

* PostgreSQL
* SQLAlchemy 2.x ORM
* Psycopg 3 PostgreSQL driver

The FastAPI backend is the only application layer allowed to access PostgreSQL.

The frontend must never access PostgreSQL directly.

### Database Connection

The PostgreSQL connection string must be provided through the environment variable:

`DATABASE_URL`

Example format:

`postgresql+psycopg://username:password@localhost:5432/supportlens`

Database credentials must never be hard-coded or committed to Git.

### Ticket Table

The primary application table is `tickets`.

Required fields:

* `id`

  * Integer
  * Primary key
  * Automatically generated

* `ticket_id`

  * String
  * Required
  * Original ticket identifier from the uploaded CSV

* `customer_message`

  * Text
  * Required
  * Original customer message

* `created_at`

  * Timestamp
  * Required
  * Original ticket creation time

* `category`

  * String
  * Nullable
  * Populated later by the LLM service

* `priority`

  * String
  * Nullable
  * Populated later by the LLM service

* `summary`

  * Text
  * Nullable
  * Populated later by the LLM service

* `suggested_response`

  * Text
  * Nullable
  * Populated later by the LLM service

* `processed_at`

  * Timestamp
  * Nullable
  * Represents completion of AI processing

Do not add additional database fields or constraints unless explicitly approved.

In particular, do not independently introduce uniqueness constraints, relationships, additional tables, or indexes beyond the approved requirements.

### Backend Responsibilities

`config.py`

* Load database configuration from environment variables.
* Do not contain business logic.

`database.py`

* Create the SQLAlchemy Engine.
* Create the SQLAlchemy session factory.
* Define the declarative ORM base.
* Provide database session lifecycle utilities for FastAPI.

`models.py`

* Define the SQLAlchemy `Ticket` ORM model.
* Reflect only the approved ticket schema.

`schemas.py`

* Define API/data validation schemas where required.
* Keep API schemas separate from database ORM models.

`services/ticket_service.py`

* Handle ticket persistence operations.
* Accept already validated ticket data from the CSV service.
* Convert validated CSV records into Ticket ORM objects.
* Save tickets within a database transaction.

`routers/tickets.py`

* Continue handling HTTP upload concerns.
* Continue using `csv_service.py` for CSV parsing and validation.
* Pass successfully parsed tickets to `ticket_service.py`.
* Do not put raw SQL or database business logic directly in the router.

### Request Flow

The upload flow must become:

CSV upload

→ FastAPI upload endpoint

→ CSV validation

→ parsed ticket records

→ ticket service

→ SQLAlchemy Session

→ PostgreSQL

→ API response

The router should coordinate the request but should not own persistence logic.

### Transaction Behavior

One CSV upload should be treated as one logical persistence operation.

If database persistence fails, the transaction must be rolled back.

Database sessions must always be closed correctly.

Database errors must not expose credentials or internal connection information to frontend users.

### Existing Behavior That Must Be Preserved

The implementation must preserve:

* CSV file validation
* required-column validation
* empty-file rejection
* ticket count response
* preview response
* existing API route
* existing frontend upload behavior
* existing tests unless the requirements legitimately require an update

### Dependencies

Backend dependencies may be updated to include:

* SQLAlchemy 2.x
* Psycopg 3

Do not introduce:

* Alembic
* Redis
* Docker Compose changes
* asynchronous SQLAlchemy
* connection-pool infrastructure
* repository-pattern abstractions
* additional database frameworks

unless explicitly approved.

### Acceptance Criteria

This milestone is complete when:

1. FastAPI can connect to PostgreSQL using `DATABASE_URL`.
2. The `tickets` table matches the approved schema.
3. Uploading a valid CSV persists every parsed ticket.
4. The upload endpoint still returns the processed ticket count.
5. The existing preview behavior still works.
6. Invalid CSV files are not persisted.
7. A database failure rolls back the persistence operation.
8. Database credentials are not hard-coded.
9. Existing upload tests continue to pass.
10. New tests cover the database persistence behavior.
