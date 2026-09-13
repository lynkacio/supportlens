# SupportLens AI Development Instructions

## Project

SupportLens is a Cloud AI Customer Support Analytics Platform.

Users can upload customer support tickets in CSV format.

The system will:

1. analyze tickets using an LLM
2. classify ticket categories
3. determine ticket priority
4. generate ticket summaries
5. generate suggested customer responses
6. store results in PostgreSQL
7. display analytics through a dashboard

## Technology Stack

Frontend:
- Next.js
- TypeScript

Backend:
- FastAPI
- Python

Database:
- PostgreSQL

AI:
- External LLM API

Deployment:
- Docker
- AWS

Communication:
- REST API

## Architecture Rules

The frontend must communicate with the backend through REST APIs.

The frontend must never connect directly to PostgreSQL.

The frontend must never contain LLM API keys.

All LLM API calls must go through the FastAPI backend.

Database access must be handled by the backend.

Do not introduce additional infrastructure unless explicitly approved.

Do not add:

- Kubernetes
- Kafka
- Redis
- Terraform
- LangChain
- vector databases
- microservices

unless the user explicitly requests them.

## Repository Structure

Expected structure:

frontend/
- Next.js application
- React components
- UI logic

backend/
- FastAPI application
- API routes
- Business services
- Database access

docs/
- Architecture documentation
- API documentation

.github/
- AI instructions
- Prompts
- Agents

## AI Development Workflow

Before implementing a feature:

1. inspect the relevant existing files
2. explain the current architecture
3. propose an implementation plan
4. identify files that need to change
5. identify possible edge cases
6. wait for approval for major architecture changes
7. implement the smallest working solution
8. run relevant tests
9. explain the changes

## LLM Integration Rules

When working with LLM features:

- Use structured outputs whenever possible.
- Validate LLM responses before storing them.
- Handle timeout and API failures gracefully.
- Never assume LLM output is always correct.
- Keep prompts separated from business logic.
- Avoid unnecessary API calls to control cost.

## Feature Development Protocol

For any new feature:

Phase 1: Planning

Before coding:
- inspect existing code
- explain current architecture
- identify affected files
- identify dependencies
- propose implementation steps

Phase 2: Implementation

After approval:
- modify only required files
- avoid unrelated changes
- maintain existing architecture

Phase 3: Verification

After implementation:
- explain changes
- run tests
- report potential issues

## Human Decision Boundaries

Do not independently change:

- system architecture
- database schema
- API contracts
- cloud provider
- authentication architecture
- security architecture

For these decisions:

1. explain the problem
2. provide possible options
3. explain tradeoffs
4. wait for human approval

## Code Quality

Prefer simple and readable code.

Avoid unnecessary abstraction.

Do not perform unrelated refactoring.

Use clear variable and function names.

Python code should use type hints.

TypeScript code should use explicit types where useful.

## Security

Never hard-code:

- API keys
- passwords
- database credentials
- access tokens

Never commit .env files.

Treat uploaded customer ticket data as untrusted input.

Validate all external input.

Keep secrets on the backend.

## Testing

For new features:

- Add tests when adding backend functionality.
- Test API responses.
- Test input validation.
- Test error cases.

Do not consider a feature complete without verification.

## Git Workflow

Use clear commit messages.

Examples:

feat:
fix:
docs:
test:
chore:

Keep commits focused on one purpose.

## Database Development Rules

When implementing database functionality:

* PostgreSQL is the approved persistent datastore.
* Use SQLAlchemy 2.x ORM.
* Use Psycopg 3 as the PostgreSQL driver.
* Database credentials must come from environment variables.
* Never hard-code database credentials.
* Keep ORM models separate from API schemas.
* Keep database persistence logic out of FastAPI routers.
* Database operations should be implemented through service-layer functions.
* Use a request-scoped SQLAlchemy Session.
* Ensure sessions are closed correctly.
* Roll back failed transactions.
* Do not expose raw database exceptions or credentials to API clients.
* Do not independently modify the approved database schema.
* Do not add tables, relationships, constraints, indexes, or migrations unless explicitly requested.
* Do not introduce async database access unless explicitly requested.
* Preserve existing CSV validation behavior and existing API contracts.

Before changing database-related code:

1. inspect the existing backend implementation
2. inspect `docs/project-requirements.md`
3. inspect existing tests
4. describe the current upload flow
5. identify exactly which files need to change
6. propose the smallest implementation plan
7. do not implement until the planned changes are consistent with the approved architecture

After implementation:

1. run existing tests
2. add persistence-specific tests
3. report exactly which tests were executed
4. explain database transaction and session behavior
5. report any unresolved risks or assumptions
