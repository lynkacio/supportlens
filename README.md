# SupportLens

AI-Powered Customer Support Analytics Platform

SupportLens is an AI-enabled customer support analytics platform that transforms raw customer tickets into actionable insights.

The system combines a modern full-stack architecture with Large Language Models (LLMs) to automatically analyze support tickets, classify customer issues, identify priorities, generate summaries, and provide interactive analytics through a web dashboard.

## Features

### 1. Automated Ticket Analysis

SupportLens automatically processes customer support tickets and extracts:

- Issue category
- Priority level
- Ticket summary
- Suggested response

Powered by LLM-based analysis.

### 2. AI-Powered Analytics Dashboard

The dashboard provides:

- Ticket volume overview
- Category distribution
- Priority analysis
- Customer issue trends

Helping teams quickly understand support workload and customer needs.

### 3. Natural Language AI Query

Users can ask questions about support data using natural language.

Examples:

- What are the most common customer complaints?
- Which issues require urgent attention?
- Summarize the major problems this week.

The system generates answers based on analyzed ticket data.

### 4. Full-Stack Web Application

The system includes:

- Modern frontend interface
- REST API backend
- Database persistence
- AI analysis pipeline
- Containerized deployment

## System Architecture

```
                 User
                  |
                  |
            Next.js Frontend
                  |
                  |
             REST API
                  |
                  |
          FastAPI Backend
                  |
        -------------------
        |                 |
        |                 |
 PostgreSQL Database   LLM API
        |
        |
 Ticket Data
```

Docker deployment:

```
                Docker Container

              FastAPI Backend
                    |
                    |
             PostgreSQL Database
                    |
                    |
                LLM Service
```

## Tech Stack

### Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS

### Backend

- FastAPI
- Python
- SQLAlchemy
- REST API

### Database

- PostgreSQL

### AI

- Large Language Model API
- Automated ticket classification
- AI-generated summaries

### Deployment

- Docker
- Docker Compose
- Cloud deployment

## Project Structure

```
supportlens/

├── frontend/
│   ├── app/
│   ├── components/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── models/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── compose.yaml
│
└── README.md
```

## Local Development

### Backend Setup

Navigate to backend:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```
.env
```

Example:

```
DATABASE_URL=your_database_url
LLM_API_KEY=your_api_key
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

## Docker Deployment

### Build and Start

From project root:

```bash
docker compose up --build
```

This will:

- Build the backend Docker image
- Create the backend container
- Load environment variables
- Start the FastAPI service

Backend:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

### Stop Services

```bash
docker compose down
```

## Environment Variables

The application uses environment variables for sensitive configuration.

Example:

```
DATABASE_URL=

LLM_API_KEY=
```

Secrets should not be stored directly in source code.

## API Documentation

FastAPI automatically provides interactive API documentation:

Swagger UI:

```
http://localhost:8000/docs
```

Main API functions include:

- Ticket upload
- Ticket analysis
- Statistics retrieval
- AI query

## Development Workflow

Typical workflow:

```
Modify Code
    ↓
Build Docker Image
    ↓
Run Container
    ↓
Test API
    ↓
Deploy
```

Build image manually:

```bash
docker build -t supportlens-backend ./backend
```

Run container:

```bash
docker run \
--env-file backend/.env \
-p 8000:8000 \
supportlens-backend
```

## Future Improvements

Potential improvements include:

- Authentication and user management
- Advanced ticket trend prediction
- Multi-agent AI analysis
- Real-time support monitoring
- Automated workflow integration

## License

This project is developed as a portfolio engineering project.