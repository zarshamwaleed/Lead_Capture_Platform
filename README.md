# Lead Capture Platform

A production-ready embeddable widget and lead-capture platform that lets customers create forms, embed them on any website with a single `<script>` tag, and securely collect leads.

## Features

### Core Features

* Authentication - JWT-based user authentication with bcrypt password hashing
* Widget Management - Full CRUD operations with multiple widget types
* Embeddable Widget - One-line script tag for easy embedding
* Public Submission API - Receive form submissions from external websites
* Rate Limiting - Protect against abuse (10/min, 50/hour per IP)
* Spam Protection - Keyword filtering and honeypot detection
* Geo Enrichment - IP geolocation with fallback providers
* Email Notifications - Background email processing with Mailpit
* Dashboard & Analytics - Comprehensive metrics and visualizations
* Testing - Full test suite with 8+ passing tests

### Security Features

* JWT authentication with bcrypt password hashing
* Rate limiting on all endpoints
* Spam keyword filtering
* Honeypot field for bot detection
* Email validation
* Tenant isolation so users only see their own data

## Tech Stack

| Component      | Technology                                     |
| -------------- | ---------------------------------------------- |
| Backend        | FastAPI (Python 3.11+)                         |
| Database       | SQLite (development) / PostgreSQL (production) |
| ORM            | SQLAlchemy + Alembic                           |
| Validation     | Pydantic V2                                    |
| Authentication | JWT (python-jose) + bcrypt                     |
| Rate Limiting  | SlowAPI                                        |
| Email Testing  | Mailpit                                        |
| Testing        | Pytest + pytest-asyncio                        |
| Container      | Docker + Docker Compose                        |

## Prerequisites

* Python 3.11 or higher
* Docker & Docker Compose (optional)
* Git
* 4GB+ RAM

## Quick Start

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/lead-capture-platform.git
cd lead-capture-platform

# Create virtual environment
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

### Option 2: Docker

```bash
# Start all services
docker-compose up -d

# Seed the database
docker-compose exec app python scripts/seed.py

# Access the API
# http://localhost:8000
# http://localhost:8000/api/docs (Swagger UI)
```

### Option 3: Quick Test with Mailpit

```bash
# Start Mailpit for email testing
docker run -d --name mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit

# Start the application
python -m uvicorn app.main:app --reload --port 8000
```

## API Documentation

### Authentication Endpoints

| Method | Endpoint             | Description             | Auth Required |
| ------ | -------------------- | ----------------------- | ------------- |
| POST   | `/api/auth/register` | Register new user       | No            |
| POST   | `/api/auth/login`    | Login and get JWT token | No            |
| GET    | `/api/auth/me`       | Get current user info   | Yes           |

### Widget Management

| Method | Endpoint                          | Description                 | Auth Required |
| ------ | --------------------------------- | --------------------------- | ------------- |
| POST   | `/api/widgets/`                   | Create a new widget         | Yes           |
| GET    | `/api/widgets/`                   | List all widgets            | Yes           |
| GET    | `/api/widgets/{id}`               | Get widget by ID            | Yes           |
| PUT    | `/api/widgets/{id}`               | Update widget               | Yes           |
| DELETE | `/api/widgets/{id}`               | Delete widget               | Yes           |
| POST   | `/api/widgets/{id}/toggle`        | Toggle widget active status | Yes           |
| GET    | `/api/widgets/public/{id}/config` | Get widget config (public)  | No            |

### Public Submissions

| Method | Endpoint                              | Description              | Auth Required |
| ------ | ------------------------------------- | ------------------------ | ------------- |
| POST   | `/public/submissions/`                | Submit form data         | No            |
| GET    | `/public/submissions/`                | Get submissions          | Yes           |
| GET    | `/public/submissions/{id}`            | Get submission by ID     | Yes           |
| PUT    | `/public/submissions/{id}`            | Update submission status | Yes           |
| GET    | `/public/submissions/stats/dashboard` | Get submission stats     | Yes           |

### Dashboard & Analytics

| Method | Endpoint                             | Description                | Auth Required |
| ------ | ------------------------------------ | -------------------------- | ------------- |
| GET    | `/api/dashboard/stats`               | Dashboard statistics       | Yes           |
| GET    | `/api/dashboard/summary`             | Complete dashboard summary | Yes           |
| GET    | `/api/dashboard/trends`              | Submission trends          | Yes           |
| GET    | `/api/dashboard/widgets/performance` | Widget performance         | Yes           |
| GET    | `/api/dashboard/geo`                 | Geographic distribution    | Yes           |
| GET    | `/api/dashboard/hourly`              | Hourly distribution        | Yes           |

## Example Requests

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "test12345",
    "password_confirm": "test12345",
    "full_name": "Test User"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "test12345"
  }'
```

### Create a Widget

```bash
curl -X POST http://localhost:8000/api/widgets/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Newsletter Signup",
    "description": "Subscribe to our newsletter",
    "widget_type": "signup_form",
    "fields": ["name", "email"],
    "button_text": "Subscribe Now",
    "is_active": true
  }'
```

### Submit a Form

```bash
curl -X POST http://localhost:8000/public/submissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "widget_id": 1,
    "data": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

## Project Structure

```text
Lead_Capture_Platform/
├── app/
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── widgets.py          # Widget management
│   │   ├── submissions.py      # Submission endpoints
│   │   └── dashboard.py        # Dashboard analytics
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # Password hashing & JWT
│   │   ├── auth.py             # Authentication dependencies
│   │   ├── rate_limiter.py     # Rate limiting
│   │   └── spam_protection.py  # Spam detection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── widget.py           # Widget model
│   │   └── submission.py       # Submission model
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py             # User schemas
│   │   ├── widget.py           # Widget schemas
│   │   ├── submission.py       # Submission schemas
│   │   └── dashboard.py        # Dashboard schemas
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── geo_service.py      # IP geolocation
│   │   ├── email_service.py    # Email notifications
│   │   ├── webhook_service.py  # Webhook integration
│   │   └── dashboard_service.py # Dashboard analytics
│   ├── static/                 # Static files
│   │   └── widget.js           # Embeddable widget script
│   └── main.py                 # Application entry point
├── migrations/                 # Alembic migrations
├── scripts/                    # Utility scripts
│   ├── seed.py                 # Database seeding
│   ├── quick_test.py           # Quick model tests
│   └── run_tests.py            # Test runner
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_auth.py            # Authentication tests
│   ├── test_widgets.py         # Widget tests
│   ├── test_submissions.py     # Submission tests
│   ├── test_rate_limiting.py   # Rate limit tests
│   ├── test_geo_enrichment.py  # Geo enrichment tests
│   ├── test_dashboard.py       # Dashboard tests
│   └── test_simple.py          # End-to-end tests
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore file
├── Dockerfile                  # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── capstone.yaml                # Capstone manifest
├── BUILDLOG.md                  # AI usage log
├── EVIDENCE.md                  # Feature verification
└── README.md                    # This file
```

## Testing

### Run All Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py -v
```

### Test Results

```text
collected 8 items

tests/test_simple.py::test_server_running PASSED
tests/test_simple.py::test_health_check PASSED
tests/test_simple.py::test_register_user PASSED
tests/test_simple.py::test_login PASSED
tests/test_simple.py::test_create_widget PASSED
tests/test_simple.py::test_get_widgets PASSED
tests/test_simple.py::test_submit_form PASSED
tests/test_simple.py::test_spam_detection PASSED

=============================================== 8 passed in 54.98s ================================================
```

## Environment Variables

| Variable                      | Description                          | Default                       |
| ----------------------------- | ------------------------------------ | ----------------------------- |
| `DATABASE_URL`                | Database connection URL              | `sqlite:///./lead_capture.db` |
| `SECRET_KEY`                  | JWT secret key                       | Required                      |
| `ALGORITHM`                   | JWT algorithm                        | `HS256`                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time                    | `30`                          |
| `CORS_ORIGINS`                | Allowed CORS origins                 | `["http://localhost:5500"]`   |
| `GEO_PROVIDER_A_URL`          | Primary geo provider                 | `http://ip-api.com/json`      |
| `GEO_PROVIDER_B_URL`          | Fallback geo provider                | `https://ipapi.co/json`       |
| `RATE_LIMIT_PER_MINUTE`       | Rate limit per minute                | `10`                          |
| `SMTP_HOST`                   | SMTP server host                     | `localhost`                   |
| `SMTP_PORT`                   | SMTP server port                     | `1025`                        |
| `EMAIL_FROM`                  | From email address                   | `noreply@leadcapture.com`     |
| `ENVIRONMENT`                 | Environment (development/production) | `development`                 |
| `DEBUG`                       | Debug mode                           | `True`                        |

## Email Testing

This project uses **Mailpit** for local email testing.

### Start Mailpit

```bash
docker run -d --name mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit
```

### Access Mailpit UI

Open `http://localhost:8025/` in your browser to view emails.

## Geo Enrichment

The platform uses two geo providers with fallback:

1. **Primary:** ip-api.com (free, 45 requests/minute, no API key)
2. **Fallback:** ipapi.co (free tier, approximately 1000 lookups/day)

If both providers fail, submissions still succeed through graceful degradation.

## Security Features

* JWT authentication with bcrypt password hashing
* Rate limiting (10/min, 50/hour per IP)
* Spam keyword filtering
* Honeypot field for bot detection
* Email validation
* Tenant isolation
* CORS configuration
* Input validation with Pydantic

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run tests.
5. Submit a pull request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

* Built as part of the FlyRank Internship - Backend Track Capstone
* FastAPI for the web framework
* SQLAlchemy for the ORM
* All open-source libraries used in this project

## Support

For issues or questions, please open an issue on GitHub.
