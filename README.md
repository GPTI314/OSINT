# OSINT Intelligence Platform (OSINT-IP)

> **Comprehensive, enterprise-grade OSINT tool repository for intelligence gathering, data collection, analysis, and reporting**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Security](#security)
- [License](#license)

## 🎯 Overview

OSINT Intelligence Platform is a comprehensive, production-grade OSINT tool repository that provides unified platform for intelligence gathering, data collection, analysis, and reporting. Built with modern technologies and designed for scalability, security, and extensibility.

### Key Capabilities

- **Multi-source Intelligence Gathering**: Domain, IP, Email, Social Media, Phone intelligence
- **Advanced Web Scraping & Crawling**: JavaScript-rendered sites support with Playwright
- **Data Aggregation & Correlation**: Elasticsearch-powered search and analysis
- **Threat Intelligence**: Integration with major threat intel sources
- **Real-time Processing**: Celery-based asynchronous task queue
- **Modern Web Interface**: React 18 with Material-UI
- **RESTful API**: Complete FastAPI-based API with OpenAPI documentation
- **Scalable Architecture**: Microservices-ready with Docker & Kubernetes support

## ✨ Features

### 🔍 OSINT Collectors

- **Domain Intelligence**
  - WHOIS lookup
  - DNS record enumeration
  - Subdomain discovery
  - SSL certificate analysis
  - Domain reputation checking

- **IP Address Intelligence**
  - Geolocation
  - Port scanning
  - Reverse DNS lookup
  - Shodan integration
  - ASN lookup

- **Email Intelligence**
  - Email validation
  - Breach database checking
  - Domain reputation
  - SMTP verification

- **Social Media Intelligence**
  - Username enumeration across platforms
  - Profile discovery
  - Twitter/Reddit/GitHub integration

- **Phone Intelligence**
  - Number validation
  - Carrier lookup
  - Geographic location
  - Number type detection

### 🕷️ Web Scraping & Crawling

- **Basic Scraper** (BeautifulSoup + Requests)
  - HTML parsing
  - CSS selector extraction
  - Link and image extraction
  - Metadata extraction

- **Advanced Scraper** (Playwright)
  - JavaScript-rendered pages
  - Dynamic content handling
  - Screenshot capture
  - Custom JS execution

- **Intelligent Crawler**
  - Configurable depth control
  - Domain filtering
  - robots.txt respect
  - Concurrent crawling

### 📊 Analysis & Reporting

- Threat intelligence correlation
- Risk scoring
- Pattern recognition
- Automated report generation (PDF, JSON, CSV, Excel)
- Data visualization

### 🏗️ Infrastructure

- **Databases**: PostgreSQL, MongoDB, Elasticsearch, Redis
- **Message Queue**: RabbitMQ + Celery
- **Monitoring**: Prometheus + Grafana
- **Security**: JWT authentication, OAuth2, Rate limiting

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
├───────────────────────────┬─────────────────────────────────┤
│     React Frontend         │         FastAPI Backend         │
│   (TypeScript + MUI)       │    (Python 3.11 + FastAPI)     │
└───────────────────────────┴─────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼────────┐        ┌───────────▼──────────┐    ┌──────────▼─────────┐
│   PostgreSQL   │        │      MongoDB         │    │   Elasticsearch    │
└────────────────┘        └──────────────────────┘    └────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼────────┐        ┌───────────▼──────────┐    ┌──────────▼─────────┐
│     Redis      │        │      RabbitMQ        │    │   Celery Workers   │
└────────────────┘        └──────────────────────┘    └────────────────────┘
```

## 📦 Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.20+
- 8GB+ RAM recommended
- 20GB+ disk space

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd OSINT
```

2. **Configure environment**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Run setup script**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

4. **Access the platform**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs
- Flower (Celery): http://localhost:5555
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

## ⚙️ Configuration

### Environment Variables

Key configuration in `backend/.env`:

```env
# Security (CHANGE THESE!)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database
POSTGRES_PASSWORD=your-postgres-password
MONGO_PASSWORD=your-mongo-password
REDIS_PASSWORD=your-redis-password

# OSINT API Keys (Optional)
SHODAN_API_KEY=your-shodan-key
VIRUSTOTAL_API_KEY=your-virustotal-key
HUNTER_IO_API_KEY=your-hunter-key
```

## 📖 Usage

### Web Interface

1. Login at http://localhost:3000/login
2. Create Investigation
3. Add Targets (domains, IPs, emails, etc.)
4. Run Analysis
5. View Results
6. Generate Reports

### API Usage

#### Authentication

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin&password=password"
```

#### Domain Intelligence

```bash
curl -X POST http://localhost:8000/api/v1/osint/investigate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "domain",
    "target_value": "example.com",
    "operations": ["whois", "dns", "subdomains"]
  }'
```

## 📚 API Documentation

Interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🛠️ Development

### Local Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

### Docker Compose (Production)

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/
```

## 🔒 Security

### Best Practices

1. Change default passwords in `.env`
2. Use strong secrets for JWT
3. Enable HTTPS in production
4. Implement rate limiting
5. Regular security updates
6. Monitor logs
7. Backup databases

### Security Features

- JWT authentication
- Password hashing (bcrypt)
- SQL injection protection
- XSS protection
- CORS configuration
- Input validation
- Rate limiting

## 📜 License

This project is licensed under the MIT License.

## 📧 Support

For issues and questions, please create an issue on GitHub.

---

**⚠️ Disclaimer**: This tool is for authorized security testing, research, and educational purposes only. Users are responsible for complying with applicable laws and regulations. Misuse of this tool for unauthorized activities is strictly prohibited.

**🔐 Ethical Usage**: Always obtain proper authorization before conducting OSINT investigations. Respect privacy and comply with terms of service.

---

Made with ❤️ for the security and intelligence community
