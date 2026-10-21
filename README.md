# MetricMind – Agentic Semantic BI Engine

MetricMind is a conversational Business Intelligence (BI) application that allows users to ask business questions in natural language and receive data-driven insights from a PostgreSQL database.

## Overview

Traditional BI tools often require users to understand dashboards, database schemas, or SQL queries. MetricMind aims to simplify business analytics by allowing users to ask questions in plain English.

The application combines a Next.js dashboard, a FastAPI backend, a PostgreSQL database, a semantic metrics layer, and an AI-powered query-understanding workflow.

## Features

- Natural-language business queries
- Revenue, cost, profit, and profit-margin analytics
- Country-wise and product-wise analysis
- Multi-step reasoning for selected business questions
- Semantic metric definitions and governed dimensions
- PostgreSQL database integration
- Query history
- Interactive analytics dashboard
- Basic input validation and error handling
- Generated SQL visibility for supported queries

## Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- Recharts

### Backend
- Python
- FastAPI
- Uvicorn
- Psycopg2

### Database
- PostgreSQL

### AI and Query Understanding
- Llama 3.2
- Ollama
- LangChain

## Architecture

1. The user enters a business question in the frontend.
2. The FastAPI backend interprets the question and identifies the relevant metric, dimension, and operation.
3. The semantic layer maps supported metrics to predefined SQL expressions.
4. The backend queries PostgreSQL and processes the result.
5. The frontend displays the answer, analytics, and available query details.
6. Query history records supported query activity.

## Project Structure

```text
MetricMind/
├── backend/
│   ├── main.py
│   └── venv/
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

The virtual environment and generated frontend files are local development artifacts and should not be committed.

## Prerequisites

Install the following before running the application:

- Python 3.12 or a compatible version
- Node.js and npm
- PostgreSQL
- Ollama with the required Llama model, if using local AI inference

## Local Setup

### 1. Configure PostgreSQL

Create a PostgreSQL database named `metricmind` and configure the database connection for the backend.

Ensure the required tables and sample data are available.

**Security:** Keep database credentials in environment variables or a local environment file. Never commit passwords, API keys, or tokens to GitHub.

### 2. Start the Backend

Open PowerShell:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --port 8001
```

If the virtual environment does not exist, create and configure it before activation.

Backend base URL:

`http://127.0.0.1:8001`

Interactive API documentation:

`http://127.0.0.1:8001/docs`

### 3. Start the Frontend

Open a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev -- --webpack
```

Open the application at:

`http://localhost:3000`

Keep both development server windows open while using the application.

## Example Questions

Try asking MetricMind questions such as:

- What is the total revenue?
- Show me revenue by country.
- Show me profit by country.
- Which country has the highest revenue and what is its profit?

The exact response depends on the available database data and supported query patterns.

## API Endpoints

The backend includes endpoints for application health, database connectivity, analytics, semantic metrics, governance information, natural-language queries, and query history.

For available request and response details, start the backend and open `/docs`.

## Testing

Before presenting or deploying the project, verify:

- Database connectivity
- Total revenue and other metric calculations
- Country-wise and product-wise breakdowns
- Multi-step query responses
- Query history persistence
- Empty or unsupported query handling
- Frontend-to-backend communication

## Security Notes

- Never commit passwords, tokens, or private keys.
- Keep local environment files out of Git.
- Do not commit Python virtual environments or `node_modules`.
- Rotate any credential that may have been exposed.
- Review changes before pushing them to a public repository.

## Current Status

MetricMind has implemented its core frontend, backend, PostgreSQL integration, semantic analytics, query history, and selected multi-step query workflows. Further testing and refinements may be required before production deployment.

## Future Improvements

- Improve natural-language intent classification
- Expand supported analytical questions
- Add more robust automated tests
- Improve visualizations and error messages
- Strengthen configuration and deployment practices
- Add authentication and role-based access controls

## Author

Developed as a conversational Business Intelligence project focused on simplifying data analysis through natural-language interaction.
