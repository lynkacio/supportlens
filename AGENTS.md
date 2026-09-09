# Agent Instructions

## Repository State

- This repository is an early scaffold. Do not assume a backend or frontend framework unless configuration is added to the repository.
- `backend/` contains empty `app/routers/`, `app/services/`, and `tests/` directories.
- `frontend/` contains empty `app/`, `components/`, and `lib/` directories.
- `data/`, `docs/`, and `.github/` currently contain no project documentation or conventions.
- `README.md` does not describe the product or development workflow.

## Current Implementation

- `test.py` defines `calculate_average(numbers)`, which returns `0` for an empty input and otherwise returns the arithmetic mean.
- There are no dependency manifests, application entry points, automated tests, lint configuration, build scripts, or CI workflows.

## Working Guidelines

- Inspect the repository for newly added manifests and documentation before choosing tools, frameworks, or commands.
- Keep changes small and consistent with the existing Python style: four-space indentation and `snake_case` names.
- Do not claim that `python test.py` validates behavior; it only loads the function and produces no output.
- Add focused tests when changing existing behavior. Treat dependency installation and build commands as unknown until the repository defines them.