# OSINT Platform - Secure Open-Source Intelligence Toolkit

A comprehensive, security-first OSINT platform with modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## 🔒 Security Features

### Authentication & Authorization
- ✅ **JWT Tokens** - Secure token-based authentication
- ✅ **OAuth2** - Google and GitHub integration
- ✅ **RBAC** - Role-based access control with fine-grained permissions
- ✅ **API Keys** - Programmatic access with scoped permissions
- ✅ **Session Management** - Secure session tracking and management
- ✅ **Password Hashing** - Argon2 and bcrypt with strong password policies

### Data Security
- ✅ **Encryption at Rest** - AES-256 encryption for sensitive data
- ✅ **Encryption in Transit** - TLS/HTTPS with security headers
- ✅ **PII Protection** - Automatic detection, encryption, and masking
- ✅ **Access Logging** - Comprehensive audit trails
- ✅ **Data Retention** - Configurable retention policies
- ✅ **Secure Storage** - Encrypted database fields

### Ethical & Compliance
- ✅ **Robots.txt Compliance** - Automatic respect for website rules
- ✅ **Rate Limiting** - Multi-tier rate limiting (per minute/hour/day)
- ✅ **Terms of Service** - Clear acceptable use policies
- ✅ **Privacy Protection** - GDPR and CCPA compliance
- ✅ **Legal Compliance** - Data export, deletion, and user rights

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd OSINT

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Access API documentation
open http://localhost:8000/docs
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL and Redis
# (See docs/SETUP.md for details)

# Configure environment
cp .env.example .env

# Run application
python -m app.main
```

## 📚 Documentation

- **[Security Guide](docs/SECURITY.md)** - Comprehensive security documentation
- **[Setup Guide](docs/SETUP.md)** - Installation and configuration
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (Swagger)
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API documentation

## 🏗️ Architecture

```
OSINT/
├── app/
│   ├── api/              # API routes
│   │   └── routes/
│   │       └── auth.py   # Authentication endpoints
│   ├── auth/             # Authentication & authorization
│   │   ├── dependencies.py
│   │   ├── oauth2.py
│   │   └── rbac.py
│   ├── database/         # Database models and connection
│   │   ├── base.py
│   │   └── models.py
│   ├── middleware/       # Security middleware
│   │   ├── audit_logger.py
│   │   ├── rate_limiter.py
│   │   └── security_headers.py
│   ├── security/         # Security utilities
│   │   ├── encryption.py
│   │   ├── jwt_handler.py
│   │   └── password.py
│   ├── utils/            # Utility functions
│   │   ├── compliance.py
│   │   └── robots_txt.py
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── docs/                 # Documentation
├── logs/                 # Application logs
├── tests/                # Test suite
├── .env.example          # Environment variables template
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Container definition
└── requirements.txt      # Python dependencies
```

## 🔑 Key Features

### Authentication Methods

1. **Email/Password**
   ```bash
   POST /api/v1/auth/register
   POST /api/v1/auth/login
   ```

2. **OAuth2 (Google/GitHub)**
   ```bash
   GET /api/v1/auth/oauth2/google/authorize
   POST /api/v1/auth/oauth2/google/callback
   ```

3. **API Keys**
   ```bash
   # Use X-API-Key header
   curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/...
   ```

### Role-Based Access Control

**Default Roles:**
- **Admin** - Full system access
- **Analyst** - Investigation and collection
- **Viewer** - Read-only access
- **API User** - Programmatic access

**Permission Format:** `resource:action`
- `user:create`, `user:read`, `user:update`, `user:delete`
- `investigation:create`, `investigation:read`, etc.
- `collector:execute`, `collector:configure`
- `report:create`, `report:read`, `report:export`

### Data Protection

**Encrypted Fields:**
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers
- Custom PII fields

**Security Headers:**
- Strict-Transport-Security (HSTS)
- Content-Security-Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

### Audit Logging

All actions are logged with:
- User ID and action
- IP address and user agent
- Request/response data (sanitized)
- Success/failure status
- Duration
- PII access flags

### Rate Limiting

**Default Limits:**
- 60 requests/minute
- 1,000 requests/hour
- 10,000 requests/day

**Response Headers:**
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## 🛡️ Security Best Practices

### For Developers

1. Never log sensitive data
2. Always validate input
3. Use dependency injection
4. Keep secrets secure
5. Follow least privilege

### For Operators

1. Configure strong secrets (32+ chars)
2. Enable all security features
3. Monitor audit logs
4. Regular maintenance
5. Backup and recovery

### For Users

1. Use strong passwords (12+ chars)
2. Enable 2FA
3. Manage API keys
4. Review sessions
5. Respect ethical guidelines

## 📊 Compliance

### GDPR Compliance

- ✅ Right to access (data export)
- ✅ Right to rectification
- ✅ Right to erasure (account deletion)
- ✅ Right to data portability
- ✅ Privacy by design

### CCPA Compliance

- ✅ Data disclosure
- ✅ Right to delete
- ✅ Right to opt-out
- ✅ Non-discrimination

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

## 🚢 Production Deployment

See [Setup Guide](docs/SETUP.md) for:
- Environment configuration
- Database setup
- Redis configuration
- Nginx/Gunicorn setup
- SSL/TLS configuration
- Monitoring setup

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Security Info

```bash
curl http://localhost:8000/api/v1/info/security
```

### Compliance Info

```bash
curl http://localhost:8000/api/v1/info/compliance
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Specify your license here]

## 🔐 Security Disclosure

For security concerns, please email: security@example.com

Follow responsible disclosure practices.

## 📞 Support

- **Documentation:** `docs/`
- **Issues:** [GitHub Issues]
- **Email:** support@example.com

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Argon2 for secure password hashing
- All security researchers and contributors

---

**Last Updated:** 2025-11-18

**Version:** 1.0.0

**Status:** Production Ready ✅
