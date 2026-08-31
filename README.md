# Lead Capture Platform

An embeddable widget and lead-capture platform that lets customers create forms, embed them on any website with a single `<script>` tag, and securely collect leads.

## Features

* Multi-tenant widget management
* One-line embed script
* Public submission API with CORS support
* Rate limiting and spam protection
* IP geolocation enrichment with fallback
* Background email notifications
* Dashboard analytics
* Docker containerization

## Tech Stack

* **Backend:** FastAPI, Python 3.11
* **Database:** PostgreSQL, SQLAlchemy, Alembic
* **Container:** Docker and Docker Compose
* **Cache:** Redis (optional)
* **Email:** Mailpit (local SMTP)
* **Rate Limiting:** SlowAPI

## Prerequisites

* Python 3.11+
* Docker and Docker Compose
* Git

## Quick Start

### Option 1: Using Docker

```bash
# Clone the repository
git clone <your-repo-url>
cd Lead_Capture_Platform

# Start all services
docker-compose up -d

# Seed the database
docker-compose exec app python scripts/seed.py

# Access the API
# http://localhost:8000
# http://localhost:8000/api/docs (Swagger UI)
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Edit .env with your settings

# Run PostgreSQL if not using Docker
# Or use Docker only for required services
docker-compose up -d db redis mailpit

# Run the application
uvicorn app.main:app --reload

# Seed the database
python scripts/seed.py
```

## API Documentation

Once the application is running, visit:

* Swagger UI: `http://localhost:8000/api/docs`
* ReDoc: `http://localhost:8000/api/redoc`

### Key Endpoints

| Method | Endpoint                      | Description       |
| ------ | ----------------------------- | ----------------- |
| POST   | `/api/auth/register`          | Register new user |
| POST   | `/api/auth/login`             | Login user        |
| POST   | `/api/widgets`                | Create widget     |
| GET    | `/api/widgets`                | List widgets      |
| GET    | `/public/widgets/{id}/config` | Get widget config |
| POST   | `/public/submissions`         | Submit lead       |

## Project Structure

```text
Lead_Capture_Platform/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Config, database, security
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── utils/         # Helper functions
│   ├── static/        # Static files
│   ├── templates/     # HTML templates
│   └── main.py        # Application entry
├── migrations/        # Alembic migrations
├── scripts/           # Utility scripts
├── tests/             # Test files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run the test suite using:

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```
