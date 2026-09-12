# SupportLens Backend Instructions

## Framework

- Use FastAPI.
- Use Python.

## Architecture

- Define request and response models with Pydantic schemas.
- Keep API routers separate from business-logic services.
- Keep database access and persistence logic separated from routers and services.

## Input And Error Handling

- Validate all user and external input before processing it.
- Handle expected errors explicitly and return appropriate HTTP responses.
- Use Python type hints and clear, descriptive names.
