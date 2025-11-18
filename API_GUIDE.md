# OSINT Toolkit - Comprehensive API Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Pagination & Filtering](#pagination--filtering)
4. [Rate Limiting](#rate-limiting)
5. [Error Handling](#error-handling)
6. [API Endpoints](#api-endpoints)
7. [Webhooks](#webhooks)
8. [Best Practices](#best-practices)

## Getting Started

### Base URL
```
http://localhost:8000/api/v1
```

### Content Type
All requests should use `Content-Type: application/json` for POST/PATCH requests.

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

## Authentication

### JWT Token Authentication

1. **Register a new user:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "analyst@example.com",
  "username": "analyst",
  "password": "securepassword123",
  "full_name": "John Analyst",
  "role": "analyst"
}
```

2. **Login to get tokens:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "analyst",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Use the access token:**
```http
GET /api/v1/investigations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

4. **Refresh expired token:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### API Key Authentication

1. **Create an API key:**
```http
POST /api/v1/api-keys
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "name": "Production API Key",
  "expires_in_days": 365,
  "scopes": ["read", "write"]
}
```

Response (key is only shown once):
```json
{
  "id": 1,
  "name": "Production API Key",
  "key": "abc123def456...",
  "prefix": "abc123de",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2025-01-01T00:00:00Z"
}
```

2. **Use the API key:**
```http
GET /api/v1/investigations
X-API-Key: abc123def456...
```

## Pagination & Filtering

### Pagination Parameters
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### Example with Pagination
```http
GET /api/v1/investigations?page=1&page_size=20
```

Response:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### Filtering

#### Investigations
```http
GET /api/v1/investigations?status=active&priority=high&search=phishing
```

Available filters:
- `status` - Filter by status (draft, active, on_hold, completed, archived)
- `priority` - Filter by priority (low, medium, high, critical)
- `search` - Search in title, case_number, description

#### Targets
```http
GET /api/v1/targets?investigation_id=1&type=domain&status=completed
```

Available filters:
- `investigation_id` - Filter by investigation
- `type` - Filter by target type
- `status` - Filter by status

#### Findings
```http
GET /api/v1/findings?investigation_id=1&severity=critical&status=new
```

Available filters:
- `investigation_id` - Filter by investigation
- `severity` - Filter by severity (info, low, medium, high, critical)
- `status` - Filter by status (new, confirmed, false_positive, resolved)

## Rate Limiting

### Default Limits
- 60 requests per minute
- 1,000 requests per hour
- 10,000 requests per day

### Rate Limit Headers
Response headers include:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
```

### Rate Limit Exceeded
Status: `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded"
}
```

## Error Handling

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "detail": "Investigation not found",
  "error": "not_found",
  "code": "INVESTIGATION_NOT_FOUND"
}
```

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## API Endpoints

### Complete Investigation Workflow

#### 1. Create Investigation
```http
POST /api/v1/investigations
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Phishing Campaign Investigation",
  "description": "Investigating suspected phishing emails targeting employees",
  "priority": "high",
  "tags": ["phishing", "email-security", "Q1-2024"]
}
```

Response:
```json
{
  "id": 1,
  "title": "Phishing Campaign Investigation",
  "description": "Investigating suspected phishing emails targeting employees",
  "status": "draft",
  "priority": "high",
  "case_number": "INV-A1B2C3D4",
  "created_by": 1,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "tags": ["phishing", "email-security", "Q1-2024"],
  "metadata": {}
}
```

#### 2. Add Targets
```http
POST /api/v1/targets
Authorization: Bearer <token>
Content-Type: application/json

{
  "investigation_id": 1,
  "name": "Suspicious Phishing Domain",
  "type": "domain",
  "value": "phishing-site.com",
  "description": "Domain used in phishing emails"
}
```

#### 3. Gather Intelligence
```http
POST /api/v1/intelligence/domain
Authorization: Bearer <token>
Content-Type: application/json

{
  "domain": "phishing-site.com"
}
```

Response includes:
- WHOIS data
- DNS records
- Subdomains
- SSL certificate info
- IP addresses
- Reputation score
- Risk indicators

#### 4. Create Scraping Job
```http
POST /api/v1/scraping-jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "investigation_id": 1,
  "name": "Scrape Phishing Site",
  "type": "web_page",
  "url": "https://phishing-site.com",
  "config": {
    "max_pages": 50,
    "follow_links": true,
    "extract_forms": true,
    "screenshot": true
  }
}
```

#### 5. Start Scraping
```http
POST /api/v1/scraping-jobs/1/start
Authorization: Bearer <token>
```

#### 6. Document Findings
```http
POST /api/v1/findings
Authorization: Bearer <token>
Content-Type: application/json

{
  "investigation_id": 1,
  "target_id": 1,
  "title": "Credential Harvesting Form Detected",
  "description": "The phishing site contains a form designed to harvest login credentials",
  "severity": "critical",
  "category": "credential-theft",
  "confidence_score": 0.98,
  "risk_score": 92.0,
  "evidence": {
    "form_action": "https://attacker-site.com/collect.php",
    "fields": ["username", "password", "company"],
    "screenshot": "evidence/screenshot-001.png"
  },
  "artifacts": [
    "https://phishing-site.com/login.html",
    "evidence/source-code.html"
  ],
  "tags": ["credential-harvesting", "high-risk"]
}
```

#### 7. Generate Report
```http
POST /api/v1/reports
Authorization: Bearer <token>
Content-Type: application/json

{
  "investigation_id": 1,
  "title": "Phishing Campaign Analysis Report",
  "format": "pdf",
  "sections": [
    "executive_summary",
    "targets",
    "findings",
    "intelligence",
    "timeline",
    "recommendations"
  ],
  "config": {
    "include_screenshots": true,
    "include_technical_details": true
  }
}
```

#### 8. Generate and Download Report
```http
POST /api/v1/reports/1/generate
Authorization: Bearer <token>
```

```http
GET /api/v1/reports/1/download
Authorization: Bearer <token>
```

### Intelligence Gathering Examples

#### Domain Intelligence
```http
POST /api/v1/intelligence/domain
Authorization: Bearer <token>
Content-Type: application/json

{
  "domain": "example.com"
}
```

Returns:
- WHOIS registration data
- DNS A, AAAA, MX, NS, TXT records
- Discovered subdomains
- SSL certificate details
- Associated IP addresses
- Reputation scores from threat feeds

#### IP Address Intelligence
```http
POST /api/v1/intelligence/ip
Authorization: Bearer <token>
Content-Type: application/json

{
  "ip_address": "8.8.8.8"
}
```

Returns:
- Geolocation (country, city, coordinates)
- ASN and ISP information
- Reverse DNS
- Open ports (if scanning authorized)
- Known vulnerabilities
- Threat intelligence matches
- Proxy/VPN/Tor detection

#### Email Intelligence
```http
POST /api/v1/intelligence/email
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Returns:
- Email validation status
- Domain MX records
- Disposable email detection
- Data breach history
- Associated social media accounts
- Professional profiles

#### Phone Intelligence
```http
POST /api/v1/intelligence/phone
Authorization: Bearer <token>
Content-Type: application/json

{
  "phone_number": "+1234567890"
}
```

Returns:
- Number validation
- Country and carrier information
- Line type (mobile, landline, VoIP)
- Associated accounts
- Social media profiles

#### Social Media Intelligence
```http
POST /api/v1/intelligence/social
Authorization: Bearer <token>
Content-Type: application/json

{
  "platform": "twitter",
  "username": "example_user",
  "profile_url": "https://twitter.com/example_user"
}
```

Returns:
- Profile information
- Recent posts/tweets
- Follower/following counts
- Account creation date
- Activity patterns
- Network connections

## Webhooks

### Creating a Webhook
```http
POST /api/v1/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Slack Notifications",
  "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "events": [
    "investigation.created",
    "finding.created",
    "report.generated"
  ]
}
```

### Webhook Event Payload Example
```json
{
  "event": "finding.created",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "id": 1,
    "investigation_id": 1,
    "title": "Malicious JavaScript Detected",
    "severity": "critical",
    "created_by": 1
  },
  "signature": "sha256=..."
}
```

### Verifying Webhook Signatures
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Available Webhook Events
- `investigation.created`
- `investigation.updated`
- `investigation.completed`
- `target.added`
- `finding.created`
- `finding.updated`
- `scraping_job.completed`
- `crawling_session.completed`
- `report.generated`

## Best Practices

### 1. Use API Keys for Programmatic Access
For automated scripts and integrations, use API keys instead of JWT tokens.

### 2. Implement Exponential Backoff
When hitting rate limits, implement exponential backoff:
```python
import time
import requests

def api_call_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            continue
        return response
    raise Exception("Max retries exceeded")
```

### 3. Cache Intelligence Data
Intelligence data doesn't change frequently. Cache results to reduce API calls:
```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def get_domain_intelligence(domain):
    # Cache for 1 hour
    return api_call(f"/api/v1/intelligence/domain/{domain}")
```

### 4. Use Pagination for Large Datasets
Always paginate when fetching large lists:
```python
def get_all_findings(investigation_id):
    findings = []
    page = 1
    while True:
        response = requests.get(
            f"/api/v1/findings",
            params={
                "investigation_id": investigation_id,
                "page": page,
                "page_size": 100
            }
        )
        data = response.json()
        findings.extend(data["items"])
        if page >= data["total_pages"]:
            break
        page += 1
    return findings
```

### 5. Handle Errors Gracefully
```python
try:
    response = requests.post("/api/v1/findings", json=finding_data)
    response.raise_for_status()
    finding = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        print("Validation error:", e.response.json())
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print("HTTP error:", e)
except requests.exceptions.RequestException as e:
    print("Network error:", e)
```

### 6. Batch Operations
When creating multiple resources, use batch operations or async requests:
```python
import asyncio
import aiohttp

async def create_targets(investigation_id, target_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for target_data in target_list:
            task = session.post(
                "/api/v1/targets",
                json={
                    "investigation_id": investigation_id,
                    **target_data
                }
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)
```

### 7. Monitor Webhook Deliveries
Check webhook event status regularly:
```http
GET /api/v1/webhooks/1/events
Authorization: Bearer <token>
```

### 8. Use Appropriate User Roles
- Assign **Viewer** role for read-only access
- Assign **Analyst** role for investigation work
- Assign **Admin** role only for system administrators

### 9. Rotate API Keys Regularly
```http
# Deactivate old key
PATCH /api/v1/api-keys/1
{
  "is_active": false
}

# Create new key
POST /api/v1/api-keys
{
  "name": "Production Key - Rotated",
  "expires_in_days": 365
}
```

### 10. Use Investigation Tags for Organization
```json
{
  "tags": [
    "customer:acme-corp",
    "type:phishing",
    "severity:high",
    "Q1-2024"
  ]
}
```

## Support

- API Documentation: http://localhost:8000/api/docs
- GitHub Issues: [repository-url]/issues
- Email: support@example.com
