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