We are starting the PostgreSQL persistence milestone for SupportLens.

Do NOT implement anything yet.

First inspect:

* `docs/project-requirements.md`
* `.github/copilot-instructions.md`
* `backend/app/main.py`
* `backend/app/routers/tickets.py`
* `backend/app/services/csv_service.py`
* `backend/tests/test_tickets.py`
* `backend/requirements.txt`
* `data/sample_tickets.csv`

Then inspect any other existing backend file that is directly relevant.

Your task is to produce an implementation plan for PostgreSQL persistence.

The approved architecture is:

Frontend
→ FastAPI router
→ CSV service
→ ticket service
→ SQLAlchemy 2.x Session
→ PostgreSQL

The database driver is Psycopg 3.

The connection must use the `DATABASE_URL` environment variable.

The approved ticket fields are:

* id
* ticket_id
* customer_message
* created_at
* category
* priority
* summary
* suggested_response
* processed_at

Do not invent additional schema fields or constraints.

Do not implement LLM functionality.

Do not implement dashboard analytics.

Do not implement the AI query feature.

Do not introduce Alembic, Redis, asynchronous SQLAlchemy, Docker changes, authentication, or unrelated infrastructure.

Before implementation, report:

1. the current ticket upload flow
2. the exact files that already exist and are relevant
3. the files that need to be created
4. the files that need to be modified
5. dependency changes required
6. how the SQLAlchemy Engine and Session will be managed
7. how FastAPI will receive a database Session
8. how parsed CSV records will be converted into Ticket ORM objects
9. how commit and rollback will work
10. how `created_at` from the existing CSV will be converted to a database timestamp
11. how the current upload response and preview will remain backward compatible
12. the tests that should be added
13. any assumptions or architectural decisions that are not already defined by the requirements

Do not write or modify code yet.

Stop after presenting the implementation plan.
