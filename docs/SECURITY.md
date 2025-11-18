# Security Implementation Guide

## Overview

This OSINT platform implements comprehensive security measures across authentication, authorization, data protection, and ethical considerations.

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Data Security](#data-security)
3. [Ethical Considerations](#ethical-considerations)
4. [Compliance](#compliance)
5. [Best Practices](#best-practices)

---

## Authentication & Authorization

### 1. JWT Tokens

**Implementation:** `app/security/jwt_handler.py`

- **Access Tokens:** Short-lived (30 minutes default)
- **Refresh Tokens:** Long-lived (7 days default)
- **Algorithm:** HS256 (configurable)
- **Payload:** User ID, expiration, issue time, token type

**Usage:**
```python
from app.security import create_access_token, verify_token

# Create token
token = create_access_token(data={"sub": str(user_id)})

# Verify token
payload = verify_token(token, token_type="access")
```

**Security Features:**
- Token expiration
- Token type validation
- Secure signing with SECRET_KEY (min 32 characters)

### 2. OAuth2 Integration

**Implementation:** `app/auth/oauth2.py`

**Supported Providers:**
- Google OAuth2
- GitHub OAuth2

**Flow:**
1. Get authorization URL
2. User authorizes on provider
3. Exchange code for token
4. Get user info
5. Create/login user
6. Issue JWT tokens

**Configuration:**
```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 3. Password Hashing

**Implementation:** `app/security/password.py`

**Algorithms:**
- **Primary:** Argon2 (winner of Password Hashing Competition)
- **Fallback:** bcrypt (for compatibility)

**Configuration:**
- Memory cost: 64 MB
- Time cost: 3 iterations
- Parallelism: 4 threads

**Password Policy:**
- Minimum length: 12 characters (configurable)
- Requires uppercase, lowercase, digits, special characters
- Common password detection
- Password history tracking (prevent reuse)

### 4. Role-Based Access Control (RBAC)

**Implementation:** `app/auth/rbac.py`

**Default Roles:**
- **Admin:** Full system access
- **Analyst:** Investigation and collection capabilities
- **Viewer:** Read-only access
- **API User:** Programmatic access

**Permissions Format:** `resource:action`

Examples:
- `user:create`
- `investigation:read`
- `collector:execute`
- `report:export`

**Usage:**
```python
from app.auth.dependencies import require_permissions, require_roles

@router.get("/admin")
async def admin_endpoint(
    user: User = Depends(require_roles(["admin"]))
):
    pass

@router.post("/investigation")
async def create_investigation(
    user: User = Depends(require_permissions(["investigation:create"]))
):
    pass
```

### 5. API Keys

**Implementation:** `app/database/models.py` (APIKey model)

**Features:**
- Long-lived tokens for programmatic access
- Named keys for easy management
- Scoped permissions
- Rate limiting per key
- Expiration dates
- Usage tracking (last used, IP address)
- Key prefix for identification (first 8 chars)

**Security:**
- Keys are hashed before storage
- Only prefix shown in UI
- Revocable at any time

### 6. Session Management

**Implementation:** `app/database/models.py` (Session model)

**Features:**
- Session tokens stored in database
- Device tracking (IP, user agent)
- Session expiration
- Active session management
- Session revocation
- Last activity tracking

**Security:**
- Automatic expiration
- Manual revocation
- Device fingerprinting

---

## Data Security

### 1. Encryption at Rest

**Implementation:** `app/security/encryption.py`

**Algorithm:** AES-256 (via Fernet)

**Key Derivation:**
- PBKDF2 with SHA256
- 100,000 iterations
- Salt-based key derivation

**Usage:**
```python
from app.security import encryption

# Encrypt data
encrypted = encryption.encrypt("sensitive data")

# Decrypt data
decrypted = encryption.decrypt(encrypted)

# Encrypt dictionary fields
data = {"email": "user@example.com", "phone": "555-1234"}
encrypted_data = encryption.encrypt_dict(data, fields=["email", "phone"])
```

### 2. Encryption in Transit

**Implementation:** TLS/HTTPS (configured at deployment)

**Security Headers:**
- Strict-Transport-Security (HSTS)
- Content-Security-Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

**Configuration:**
```env
ENABLE_HSTS=True
HSTS_MAX_AGE=31536000
ENABLE_CSP=True
CSP_POLICY=default-src 'self'
```

### 3. PII Protection

**Implementation:** `app/security/encryption.py` (PIIProtection class)

**Supported PII Types:**
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers (SSN)
- Passport numbers

**Masking Examples:**
- Email: `u***r@example.com`
- Phone: `***-1234`
- Credit Card: `************1234`
- SSN: `***-**-1234`

**Usage:**
```python
from app.security import pii

# Mask email
masked = pii.mask_email("user@example.com")  # u**r@example.com

# Mask phone
masked = pii.mask_phone("555-123-4567")  # ***-4567
```

**Configuration:**
```env
ENABLE_PII_ENCRYPTION=True
ENABLE_PII_MASKING=True
PII_FIELDS=email,phone,ssn,passport,credit_card
```

### 4. Access Logging

**Implementation:** `app/middleware/audit_logger.py`

**Logged Information:**
- User ID
- Action/endpoint
- HTTP method
- Request/response data (sanitized)
- IP address
- User agent
- Duration
- Status (success/failure)
- PII access flag
- Data export flag

**Storage:**
- Database (structured queries)
- JSON log files (backup/analysis)

**Retention:**
```env
AUDIT_LOG_RETENTION_DAYS=730  # 2 years
```

### 5. Data Retention Policies

**Implementation:** `app/utils/compliance.py`

**Policies:**
- General data: 365 days
- PII data: 90 days
- Audit logs: 730 days (2 years)
- Deleted accounts: Soft delete with anonymization

**Configuration:**
```env
DATA_RETENTION_DAYS=365
PII_RETENTION_DAYS=90
AUDIT_LOG_RETENTION_DAYS=730
```

---

## Ethical Considerations

### 1. Robots.txt Compliance

**Implementation:** `app/utils/robots_txt.py`

**Features:**
- Automatic robots.txt fetching and parsing
- Per-domain caching
- User-agent respect
- Crawl delay extraction
- URL allow/disallow checking

**Usage:**
```python
from app.utils import robots_checker

# Check if URL can be fetched
can_fetch, delay = await robots_checker.check_and_delay(
    "https://example.com/page",
    user_agent="OSINTBot/1.0"
)

if can_fetch:
    # Wait for crawl delay
    await asyncio.sleep(delay)
    # Fetch URL
```

**Configuration:**
```env
RESPECT_ROBOTS_TXT=True
DEFAULT_CRAWL_DELAY=1.0
USER_AGENT=OSINTBot/1.0 (Ethical Research)
```

### 2. Rate Limiting

**Implementation:** `app/middleware/rate_limiter.py`

**Strategy:** Redis-based token bucket

**Limits:**
- Per minute: 60 requests
- Per hour: 1,000 requests
- Per day: 10,000 requests

**Headers:**
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp
- `Retry-After`: Seconds until retry

**Configuration:**
```env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000
```

**Custom Limits:**
API keys can have custom rate limits configured per key.

### 3. Terms of Service

**Implementation:** `app/utils/compliance.py`

**Acceptable Use:**
- Ethical research only
- Respect robots.txt
- Rate limiting compliance
- No malicious use

**Prohibited Activities:**
- Illegal surveillance
- Harassment or doxxing
- Unauthorized access
- Violating website ToS
- Bypassing security measures

### 4. Legal Compliance

**GDPR Compliance:**
- Right to access (data export)
- Right to rectification (data correction)
- Right to erasure (account deletion)
- Right to data portability
- Lawful basis for processing
- Privacy by design

**CCPA Compliance:**
- Data disclosure
- Right to delete
- Right to opt-out
- Non-discrimination

---

## Compliance

### Data Export (GDPR Article 15)

**Endpoint:** `/api/v1/compliance/export`

**Includes:**
- Personal information
- Account status
- OAuth connections
- Activity history
- API keys
- Sessions

**Format:** JSON (configurable)

### Account Deletion (GDPR Article 17)

**Endpoint:** `/api/v1/compliance/delete`

**Process:**
1. Soft delete (anonymization)
2. Remove PII
3. Anonymize audit logs
4. Revoke API keys
5. Terminate sessions

**Data Retained:**
- Audit logs (anonymized)
- Compliance records

### Privacy Policy

**Endpoint:** `/api/v1/info/compliance`

**Includes:**
- Data retention policies
- User rights
- Data protection measures
- Compliance frameworks
- Contact information

---

## Best Practices

### For Developers

1. **Never log sensitive data**
   - Use sanitization in audit logs
   - Redact passwords, tokens, keys

2. **Always validate input**
   - Use Pydantic models
   - Sanitize user input
   - Prevent SQL injection

3. **Use dependency injection**
   - Authentication dependencies
   - Permission checks
   - Database sessions

4. **Keep secrets secure**
   - Use environment variables
   - Never commit secrets
   - Rotate keys regularly

5. **Follow least privilege**
   - Grant minimum permissions
   - Use RBAC effectively
   - Audit permission changes

### For Operators

1. **Configure strong secrets**
   - SECRET_KEY: min 32 characters
   - ENCRYPTION_KEY: 32 bytes base64
   - Rotate regularly

2. **Enable security features**
   - HSTS enabled
   - CSP enabled
   - 2FA enabled
   - Email verification

3. **Monitor audit logs**
   - Check for suspicious activity
   - Review failed login attempts
   - Monitor PII access

4. **Regular maintenance**
   - Update dependencies
   - Patch vulnerabilities
   - Review access logs
   - Clean up old data

5. **Backup and recovery**
   - Regular database backups
   - Encrypted backups
   - Test recovery procedures

### For Users

1. **Use strong passwords**
   - Min 12 characters
   - Mix of character types
   - Avoid common passwords

2. **Enable 2FA**
   - Extra security layer
   - Protect against password compromise

3. **Manage API keys**
   - Use descriptive names
   - Revoke unused keys
   - Monitor usage

4. **Review sessions**
   - Check active sessions
   - Revoke suspicious sessions
   - Use logout on shared devices

5. **Respect ethical guidelines**
   - Follow ToS
   - Respect robots.txt
   - Stay within rate limits
   - Use for legal purposes only

---

## Security Checklist

### Deployment

- [ ] Generate strong SECRET_KEY (32+ characters)
- [ ] Generate ENCRYPTION_KEY (32 bytes)
- [ ] Configure DATABASE_URL (encrypted)
- [ ] Set up Redis (secure connection)
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS origins
- [ ] Set up firewall rules
- [ ] Enable security headers
- [ ] Configure rate limiting
- [ ] Set up log rotation
- [ ] Configure backups
- [ ] Review environment variables

### Production

- [ ] DEBUG=False
- [ ] Use strong database credentials
- [ ] Restrict CORS origins
- [ ] Enable HSTS
- [ ] Enable CSP
- [ ] Set up monitoring
- [ ] Configure alerting
- [ ] Regular security audits
- [ ] Dependency updates
- [ ] Log review process
- [ ] Incident response plan

---

## Incident Response

### Security Breach

1. **Contain:** Isolate affected systems
2. **Investigate:** Check audit logs, identify scope
3. **Notify:** Inform affected users (GDPR 72 hours)
4. **Remediate:** Fix vulnerability, revoke compromised credentials
5. **Document:** Record incident details
6. **Review:** Update security measures

### Data Breach

1. **Stop the leak:** Disable access points
2. **Assess impact:** Determine data exposed
3. **Legal compliance:** Report to authorities (GDPR, CCPA)
4. **User notification:** Inform affected users
5. **Offer support:** Credit monitoring, password reset
6. **Prevent recurrence:** Enhance security

---

## Contact

For security concerns or vulnerability reports:

- **Email:** security@example.com
- **PGP Key:** [Link to public key]
- **Responsible Disclosure:** Follow responsible disclosure practices

---

## Updates

This security implementation is regularly reviewed and updated. Last updated: 2025-11-18
