# OSINT Intelligence Platform

A comprehensive, enterprise-grade Open-Source Intelligence (OSINT) platform for gathering, analyzing, and managing intelligence data from various sources.

## 🚀 Features

### Core Capabilities

- **Web Scraping Engine** - Static, dynamic (JavaScript), and API scraping with proxy rotation, rate limiting, and CAPTCHA solving
- **Web Crawling Engine** - Intelligent web crawling with robots.txt compliance, duplicate detection, and politeness management
- **OSINT Intelligence Modules** - Domain, IP, email intelligence gathering with risk scoring
- **Data Processing Pipeline** - ETL pipeline for data extraction, transformation, and enrichment
- **Analysis Engine** - Correlation, entity linking, and threat intelligence analysis
- **REST API** - Complete FastAPI-based REST API with authentication and authorization
- **Task Queue** - Distributed task processing with Celery and Redis
- **Real-time Processing** - Async architecture for high-performance operations

### Intelligence Gathering

- **Domain Intelligence** - WHOIS, DNS, SSL certificates, subdomains, technology detection
- **IP Intelligence** - Geolocation, ISP information, threat intelligence, Shodan integration
- **Email Intelligence** - Validation, breach detection, domain verification
- **Social Media Intelligence** - Profile discovery and analysis (planned)
- **Image Intelligence** - Reverse image search, metadata extraction (planned)

### Security & Authentication

- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **Role-Based Access Control (RBAC)** - Admin, Analyst, and Viewer roles
- **API Key Management** - Secure API key generation and validation
- **Audit Logging** - Comprehensive audit trail for all operations

### Infrastructure

- **PostgreSQL** - Relational data storage
- **MongoDB** - Document storage for raw data
- **Redis** - Caching and message brokering
- **Elasticsearch** - Search and analytics (optional)
- **Docker** - Containerized deployment
- **Celery** - Distributed task queue

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 15+
- Redis 7+
- MongoDB 6+

### Quick Start with Docker

1. **Clone the repository**

```bash
git clone <repository-url>
cd OSINT
```

2. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the platform**

```bash
docker-compose up -d
```

4. **Initialize the database**

```bash
docker-compose exec api alembic upgrade head
```

5. **Access the platform**

- API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Flower (Celery monitoring): http://localhost:5555

### Manual Installation

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database**

```bash
alembic upgrade head
```

4. **Run the API server**

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Run Celery workers**

```bash
# In separate terminals
celery -A tasks.celery_app worker --loglevel=info -Q scraping
celery -A tasks.celery_app worker --loglevel=info -Q intelligence
celery -A tasks.celery_app beat --loglevel=info
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Application
APP_NAME="OSINT Intelligence Platform"
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_HOST=localhost
POSTGRES_DB=osint_platform
POSTGRES_USER=osint_user
POSTGRES_PASSWORD=your_password

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Third-Party APIs
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_vt_key
IPINFO_API_KEY=your_ipinfo_key
```

## 📖 API Documentation

### Authentication

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"password"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password"

# Returns: {"access_token": "...", "refresh_token": "..."}
```

### Intelligence Gathering

```bash
# Gather domain intelligence
curl -X POST http://localhost:8000/api/v1/intelligence/domain \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com","include_subdomains":true}'

# Gather IP intelligence
curl -X POST http://localhost:8000/api/v1/intelligence/ip \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip_address":"8.8.8.8"}'

# Gather email intelligence
curl -X POST http://localhost:8000/api/v1/intelligence/email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

### Investigation Management

```bash
# Create investigation
curl -X POST http://localhost:8000/api/v1/investigations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Investigation","description":"Investigation details"}'

# List investigations
curl -X GET http://localhost:8000/api/v1/investigations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (TBD)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    FastAPI REST API                          │
│  ┌──────────────┬──────────────┬──────────────┬────────┐   │
│  │ Auth         │ Intelligence │ Scraping     │ More   │   │
│  └──────────────┴──────────────┴──────────────┴────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                     Core Engines                             │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ Scraping     │ Crawling     │ OSINT Intelligence   │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  Background Tasks (Celery)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    Data Storage Layer                        │
│  ┌──────────────┬──────────────┬──────────────┬────────┐   │
│  │ PostgreSQL   │ MongoDB      │ Redis        │ ES     │   │
│  └──────────────┴──────────────┴──────────────┴────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test module
pytest tests/test_scraping.py
```

## 📊 Monitoring

- **Flower** - Celery task monitoring (http://localhost:5555)
- **Prometheus** - Metrics collection (optional)
- **Grafana** - Metrics visualization (optional)
- **ELK Stack** - Log aggregation (optional)

## 🔒 Security

- JWT-based authentication
- Role-based access control
- API key management
- Password hashing with bcrypt
- SQL injection prevention
- XSS protection
- CORS configuration
- Rate limiting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI, Celery, and asyncio
- Uses various OSINT tools and services
- Community-driven development

## 📞 Support

- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]

## 🗺️ Roadmap

- [ ] Frontend React application
- [ ] Social media intelligence modules
- [ ] Image intelligence and reverse search
- [ ] Threat intelligence integration
- [ ] Dark web monitoring
- [ ] Real-time alerts and notifications
- [ ] Advanced visualization and reporting
- [ ] Machine learning-based analysis
- [ ] API rate limiting and quotas
- [ ] Multi-tenant support

---

**Built with ❤️ for the OSINT community**
