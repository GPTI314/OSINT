# OSINT Toolkit API

A comprehensive Open-Source Intelligence (OSINT) platform with REST API for investigations, intelligence gathering, and automated workflow management.

## Features

### Core Functionality
- **Investigation Management**: Full CRUD operations for managing investigations with case tracking
- **Target Management**: Track and manage investigation targets (domains, IPs, emails, phones, etc.)
- **Scraping & Crawling**: Automated web scraping and crawling capabilities
- **Intelligence Gathering**: Collect intelligence from multiple sources:
  - Domain Intelligence (WHOIS, DNS, subdomains, SSL)
  - IP Intelligence (geolocation, ASN, ports, threats)
  - Email Intelligence (validation, breaches, social profiles)
  - Phone Intelligence (validation, carrier, location)
  - Social Media Intelligence (profiles, posts, connections)
  - Image Intelligence (EXIF, reverse search, OCR)
- **Findings Management**: Document and track investigation discoveries
- **Report Generation**: Generate reports in multiple formats (PDF, HTML, Excel, CSV, JSON, Markdown)

### API Features
- **Authentication**: JWT tokens and API keys
- **Authorization**: Role-based access control (Admin, Analyst, Viewer)
- **Rate Limiting**: Per-user and per-endpoint limits
- **Pagination**: Cursor and offset-based pagination
- **Filtering**: Advanced query filters on all resources
- **Sorting**: Multi-field sorting capabilities
- **API Versioning**: Versioned API endpoints (/api/v1)
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Webhooks**: Real-time event notifications
- **Streaming**: Real-time data streaming support

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd OSINT
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the services**
```bash
make docker-up
```

4. **Access the API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Manual Installation

1. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up database**
```bash
# Install PostgreSQL and create database
createdb osint_db

# Run migrations
alembic upgrade head
```

3. **Start Redis**
```bash
redis-server
```

4. **Run the application**
```bash
uvicorn app.main:app --reload
```

## API Documentation

### Authentication

#### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "username": "analyst",
    "password": "securepassword123",
    "full_name": "John Analyst",
    "role": "analyst"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the API

#### With JWT Token
```bash
export TOKEN="your_access_token_here"

curl -X GET "http://localhost:8000/api/v1/investigations" \
  -H "Authorization: Bearer $TOKEN"
```

#### With API Key
```bash
# Create an API key first
curl -X POST "http://localhost:8000/api/v1/api-keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 365
  }'

# Use the API key
curl -X GET "http://localhost:8000/api/v1/investigations" \
  -H "X-API-Key: your_api_key_here"
```

### Investigations

#### Create Investigation
```bash
curl -X POST "http://localhost:8000/api/v1/investigations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Phishing Campaign Investigation",
    "description": "Investigating suspected phishing domain",
    "priority": "high",
    "tags": ["phishing", "email-security"]
  }'
```

#### List Investigations
```bash
# With pagination and filtering
curl -X GET "http://localhost:8000/api/v1/investigations?page=1&page_size=20&status=active&priority=high" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Investigation Details
```bash
curl -X GET "http://localhost:8000/api/v1/investigations/1" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Investigation Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/investigations/1/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Targets

#### Add Target to Investigation
```bash
curl -X POST "http://localhost:8000/api/v1/targets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": 1,
    "name": "Suspicious Domain",
    "type": "domain",
    "value": "suspicious-site.com",
    "description": "Domain linked to phishing emails"
  }'
```

#### List Targets
```bash
curl -X GET "http://localhost:8000/api/v1/targets?investigation_id=1&type=domain" \
  -H "Authorization: Bearer $TOKEN"
```

### Intelligence Gathering

#### Domain Intelligence
```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/domain" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com"
  }'
```

#### IP Intelligence
```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/ip" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "8.8.8.8"
  }'
```

#### Email Intelligence
```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/email" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

#### Social Media Intelligence
```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/social" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "username": "example_user",
    "profile_url": "https://twitter.com/example_user"
  }'
```

### Scraping Jobs

#### Create Scraping Job
```bash
curl -X POST "http://localhost:8000/api/v1/scraping-jobs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": 1,
    "name": "Scrape Suspicious Site",
    "type": "web_page",
    "url": "https://suspicious-site.com",
    "config": {
      "max_pages": 100,
      "follow_links": true
    }
  }'
```

#### Start Scraping Job
```bash
curl -X POST "http://localhost:8000/api/v1/scraping-jobs/1/start" \
  -H "Authorization: Bearer $TOKEN"
```

### Crawling Sessions

#### Create Crawling Session
```bash
curl -X POST "http://localhost:8000/api/v1/crawling-sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": 1,
    "name": "Deep Crawl",
    "seed_url": "https://example.com",
    "max_depth": 3,
    "rate_limit": 1.0,
    "respect_robots_txt": true
  }'
```

### Findings

#### Create Finding
```bash
curl -X POST "http://localhost:8000/api/v1/findings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": 1,
    "target_id": 1,
    "title": "Malicious JavaScript Detected",
    "description": "Found obfuscated JavaScript code that attempts credential harvesting",
    "severity": "critical",
    "category": "malware",
    "confidence_score": 0.95,
    "risk_score": 85.0,
    "evidence": {
      "url": "https://suspicious-site.com/login.html",
      "code_snippet": "eval(atob('...'))"
    },
    "tags": ["javascript", "credential-harvesting"]
  }'
```

### Reports

#### Generate Report
```bash
# Create report
curl -X POST "http://localhost:8000/api/v1/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": 1,
    "title": "Phishing Investigation Report",
    "format": "pdf",
    "sections": ["summary", "targets", "findings", "timeline"]
  }'

# Generate the report file
curl -X POST "http://localhost:8000/api/v1/reports/1/generate" \
  -H "Authorization: Bearer $TOKEN"

# Download the report
curl -X GET "http://localhost:8000/api/v1/reports/1/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o report.pdf
```

### Webhooks

#### Create Webhook
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Slack Notifications",
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "events": [
      "investigation.created",
      "finding.created",
      "report.generated"
    ]
  }'
```

## API Endpoints Reference

### Authentication & Users
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `GET /api/v1/users` - List users (admin)
- `GET /api/v1/users/{id}` - Get user (admin)
- `PATCH /api/v1/users/{id}` - Update user (admin)
- `DELETE /api/v1/users/{id}` - Delete user (admin)

### API Keys
- `POST /api/v1/api-keys` - Create API key
- `GET /api/v1/api-keys` - List API keys
- `GET /api/v1/api-keys/{id}` - Get API key
- `PATCH /api/v1/api-keys/{id}` - Update API key
- `DELETE /api/v1/api-keys/{id}` - Delete API key

### Investigations
- `POST /api/v1/investigations` - Create investigation
- `GET /api/v1/investigations` - List investigations
- `GET /api/v1/investigations/{id}` - Get investigation
- `GET /api/v1/investigations/{id}/stats` - Get statistics
- `PATCH /api/v1/investigations/{id}` - Update investigation
- `DELETE /api/v1/investigations/{id}` - Delete investigation

### Targets
- `POST /api/v1/targets` - Create target
- `GET /api/v1/targets` - List targets
- `GET /api/v1/targets/{id}` - Get target
- `PATCH /api/v1/targets/{id}` - Update target
- `DELETE /api/v1/targets/{id}` - Delete target

### Scraping Jobs
- `POST /api/v1/scraping-jobs` - Create scraping job
- `GET /api/v1/scraping-jobs` - List scraping jobs
- `GET /api/v1/scraping-jobs/{id}` - Get scraping job
- `PATCH /api/v1/scraping-jobs/{id}` - Update scraping job
- `DELETE /api/v1/scraping-jobs/{id}` - Delete scraping job
- `POST /api/v1/scraping-jobs/{id}/start` - Start job
- `POST /api/v1/scraping-jobs/{id}/stop` - Stop job

### Crawling Sessions
- `POST /api/v1/crawling-sessions` - Create crawling session
- `GET /api/v1/crawling-sessions` - List crawling sessions
- `GET /api/v1/crawling-sessions/{id}` - Get crawling session
- `PATCH /api/v1/crawling-sessions/{id}` - Update crawling session
- `DELETE /api/v1/crawling-sessions/{id}` - Delete crawling session
- `POST /api/v1/crawling-sessions/{id}/start` - Start session
- `POST /api/v1/crawling-sessions/{id}/stop` - Stop session

### Intelligence
- `POST /api/v1/intelligence/domain` - Gather domain intelligence
- `GET /api/v1/intelligence/domain/{domain}` - Get domain intelligence
- `POST /api/v1/intelligence/ip` - Gather IP intelligence
- `GET /api/v1/intelligence/ip/{ip}` - Get IP intelligence
- `POST /api/v1/intelligence/email` - Gather email intelligence
- `GET /api/v1/intelligence/email/{email}` - Get email intelligence
- `POST /api/v1/intelligence/phone` - Gather phone intelligence
- `GET /api/v1/intelligence/phone/{phone}` - Get phone intelligence
- `POST /api/v1/intelligence/social` - Gather social intelligence
- `GET /api/v1/intelligence/social/{platform}/{username}` - Get social intelligence
- `POST /api/v1/intelligence/image` - Gather image intelligence
- `GET /api/v1/intelligence/image/{hash}` - Get image intelligence

### Findings
- `POST /api/v1/findings` - Create finding
- `GET /api/v1/findings` - List findings
- `GET /api/v1/findings/{id}` - Get finding
- `PATCH /api/v1/findings/{id}` - Update finding
- `DELETE /api/v1/findings/{id}` - Delete finding

### Reports
- `POST /api/v1/reports` - Create report
- `GET /api/v1/reports` - List reports
- `GET /api/v1/reports/{id}` - Get report
- `PATCH /api/v1/reports/{id}` - Update report
- `DELETE /api/v1/reports/{id}` - Delete report
- `POST /api/v1/reports/{id}/generate` - Generate report file
- `GET /api/v1/reports/{id}/download` - Download report

### Webhooks
- `POST /api/v1/webhooks` - Create webhook
- `GET /api/v1/webhooks` - List webhooks
- `GET /api/v1/webhooks/{id}` - Get webhook
- `PATCH /api/v1/webhooks/{id}` - Update webhook
- `DELETE /api/v1/webhooks/{id}` - Delete webhook
- `GET /api/v1/webhooks/{id}/events` - List webhook events
- `POST /api/v1/webhooks/{id}/test` - Test webhook

## User Roles

### Admin
- Full access to all features
- User management
- System configuration

### Analyst
- Create and manage investigations
- Add targets and findings
- Generate reports
- Manage scraping/crawling jobs

### Viewer
- Read-only access
- View investigations, targets, and findings
- Download reports

## Rate Limits

Default rate limits per user:
- 60 requests per minute
- 1,000 requests per hour
- 10,000 requests per day

Rate limits can be configured in `.env` file.

## Webhook Events

Available webhook events:
- `investigation.created`
- `investigation.updated`
- `investigation.completed`
- `target.added`
- `finding.created`
- `finding.updated`
- `scraping_job.completed`
- `crawling_session.completed`
- `report.generated`

## Development

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make format
```

### Database Migrations

Create a new migration:
```bash
make migrate-create
```

Apply migrations:
```bash
make migrate
```

### Makefile Commands
- `make install` - Install dependencies
- `make dev` - Run development server
- `make test` - Run tests
- `make docker-up` - Start Docker containers
- `make docker-down` - Stop Docker containers
- `make docker-logs` - View Docker logs
- `make migrate` - Run database migrations
- `make format` - Format code

## Architecture

### Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT + API Keys
- **Documentation**: OpenAPI/Swagger
- **Containerization**: Docker & Docker Compose

### Project Structure
```
OSINT/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # Auth & dependencies
│   │   └── v1/
│   │       ├── api.py                # Router aggregation
│   │       └── endpoints/            # API endpoints
│   ├── celery/
│   │   ├── worker.py                 # Celery worker
│   │   └── tasks/                    # Background tasks
│   ├── core/
│   │   ├── config.py                 # Configuration
│   │   ├── database.py               # Database setup
│   │   ├── rate_limit.py             # Rate limiting
│   │   └── security.py               # Security utilities
│   ├── models/                       # SQLAlchemy models
│   ├── schemas/                      # Pydantic schemas
│   └── main.py                       # Application entry
├── tests/                            # Test suite
├── docker-compose.yml                # Docker Compose config
├── Dockerfile                        # Docker image
├── requirements.txt                  # Python dependencies
├── Makefile                          # Development commands
└── README.md                         # This file
```

## Configuration

All configuration is done via environment variables in `.env` file. See `.env.example` for all available options.

Key configurations:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `RATE_LIMIT_*` - Rate limiting settings
- `CORS_ORIGINS` - Allowed CORS origins
- External API keys for intelligence gathering

## Security Considerations

1. **Always use HTTPS in production**
2. **Change default SECRET_KEY**
3. **Use strong passwords**
4. **Rotate API keys regularly**
5. **Configure CORS appropriately**
6. **Enable rate limiting**
7. **Review webhook URLs before creation**
8. **Restrict file upload types and sizes**

## License

[Your License Here]

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Support

For support, please open an issue on GitHub or contact the maintainers.
