# SupportLens Project Requirements

## 1. Project Overview

Project Name:
SupportLens

Type:
Cloud AI Customer Support Analytics Platform

Goal:
Build a full-stack AI-powered customer support analytics platform that helps support teams analyze customer tickets automatically.

The system allows users to upload customer support tickets in CSV format, uses an LLM service to analyze tickets, stores structured results, and provides business insights through a dashboard.


## 2. Problem Statement

Customer support teams receive large volumes of customer messages.

Manual processing causes:

- slow response time
- inconsistent ticket classification
- difficulty discovering customer pain points

SupportLens aims to automate ticket understanding and provide data-driven support analytics.


## 3. Target Users

Primary users:

- Customer support managers
- Support agents
- Business analysts

Secondary users:

- Company managers who need customer feedback insights


## 4. MVP Scope

The first version must support:

### Ticket Upload

Users can upload CSV files containing customer tickets.


### AI Ticket Analysis

The system generates:

- category
- priority
- summary
- suggested_response


Allowed categories:

- Billing
- Bug
- Feature Request
- Account
- API


Priority:

- Low
- Medium
- High


## 5. System Workflow

User
 ↓
Frontend (Next.js)
 ↓
Backend API (FastAPI)
 ↓
LLM API
 ↓
PostgreSQL Database
 ↓
Dashboard


## 6. Functional Requirements


### Frontend

The frontend should provide:

- CSV upload page
- Dashboard page
- AI query page


### Backend

The backend should provide:

- REST API
- CSV processing
- LLM integration
- Database operations


### Database

The database stores:

- ticket information
- AI analysis results
- processing status


## 7. Non Goals

The V1 system will NOT implement:

- Kubernetes
- Kafka
- Redis
- Terraform
- model training
- RAG system
- multi-agent architecture


## 8. Success Criteria

The MVP is considered complete when:

1. Users can upload ticket CSV files.

2. Backend successfully processes tickets.

3. AI generates structured ticket analysis.

4. Results are stored in PostgreSQL.

5. Dashboard displays ticket analytics.

6. Application can be deployed using Docker.


## 9. Development Principles

Architecture decisions are controlled by human developers.

AI tools may assist with:

- code generation
- testing
- documentation

but must not independently change:

- system architecture
- database schema
- API contracts