# OSINT Platform - Configuration Reference

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Application Configuration](#application-configuration)
3. [Database Configuration](#database-configuration)
4. [Security Configuration](#security-configuration)
5. [Collector Configuration](#collector-configuration)
6. [Analysis Configuration](#analysis-configuration)
7. [Workflow Configuration](#workflow-configuration)
8. [Notification Configuration](#notification-configuration)
9. [Logging Configuration](#logging-configuration)
10. [Performance Configuration](#performance-configuration)

## Environment Variables

### Core Application Settings

```bash
# Application Environment
APP_ENV=production                    # Options: development, staging, production
APP_NAME=OSINT-Platform              # Application name
APP_VERSION=1.0.0                    # Application version
DEBUG=false                          # Enable debug mode (true/false)
LOG_LEVEL=INFO                       # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Server Configuration
API_HOST=0.0.0.0                     # API host address
API_PORT=8000                        # API port number
WORKERS=4                            # Number of worker processes
RELOAD=false                         # Auto-reload on code changes (development only)

# Base URLs
BASE_URL=https://api.osint-platform.example
FRONTEND_URL=https://osint-platform.example
CORS_ORIGINS=https://osint-platform.example,https://app.osint-platform.example
```

### Database Configuration

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/osint
DB_POOL_SIZE=20                      # Connection pool size
DB_MAX_OVERFLOW=10                   # Max overflow connections
DB_POOL_TIMEOUT=30                   # Pool timeout in seconds
DB_ECHO=false                        # Echo SQL queries (true/false)

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
NEO4J_MAX_CONNECTION_LIFETIME=3600
NEO4J_MAX_CONNECTION_POOL_SIZE=50
NEO4J_CONNECTION_TIMEOUT=30

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=osint
MONGODB_MAX_POOL_SIZE=100
MONGODB_MIN_POOL_SIZE=10
MONGODB_SERVER_SELECTION_TIMEOUT=30000

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
REDIS_DECODE_RESPONSES=true

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=password
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
```

### Security Configuration

```bash
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here-minimum-32-characters
JWT_ALGORITHM=HS256                  # Options: HS256, HS384, HS512, RS256
JWT_EXPIRATION=3600                  # Token expiration in seconds (1 hour)
JWT_REFRESH_EXPIRATION=2592000       # Refresh token expiration (30 days)

# Password Requirements
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100              # Requests per window
RATE_LIMIT_WINDOW=60                 # Window in seconds
RATE_LIMIT_PREMIUM_REQUESTS=1000

# Session Management
SESSION_TIMEOUT=86400                # Session timeout in seconds (24 hours)
SESSION_COOKIE_SECURE=true           # Secure cookie flag
SESSION_COOKIE_HTTPONLY=true         # HTTP-only cookie flag
SESSION_COOKIE_SAMESITE=Lax          # Options: Strict, Lax, None

# Encryption
ENCRYPTION_KEY=your-encryption-key-here-32-bytes
ENCRYPTION_ALGORITHM=AES-256-GCM

# CORS
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=3600
```

### External Services

```bash
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_USER=noreply@osint-platform.example
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@osint-platform.example
SMTP_FROM_NAME=OSINT Platform

# Object Storage (S3-compatible)
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=osint-platform-storage
S3_REGION=us-east-1
S3_SECURE=true

# Webhook Notifications
WEBHOOK_ENABLED=true
WEBHOOK_TIMEOUT=10
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=5

# Slack Integration
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#osint-alerts

# Third-party APIs
VIRUSTOTAL_API_KEY=your-virustotal-api-key
SHODAN_API_KEY=your-shodan-api-key
CENSYS_API_ID=your-censys-api-id
CENSYS_API_SECRET=your-censys-api-secret
```

### Celery Configuration

```bash
# Broker
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Task Settings
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json
CELERY_TIMEZONE=UTC
CELERY_ENABLE_UTC=true

# Performance
CELERY_TASK_TIME_LIMIT=3600          # Task hard time limit (1 hour)
CELERY_TASK_SOFT_TIME_LIMIT=3000     # Task soft time limit (50 minutes)
CELERY_WORKER_CONCURRENCY=4          # Number of concurrent workers
CELERY_WORKER_PREFETCH_MULTIPLIER=4  # Tasks to prefetch
CELERY_TASK_ACKS_LATE=true          # Acknowledge tasks after completion
```

## Application Configuration

### config.yaml

Create a `config.yaml` file for application-specific settings:

```yaml
application:
  name: OSINT Platform
  version: 1.0.0
  environment: production

  # Feature Flags
  features:
    social_media_collection: true
    dark_web_collection: false
    ai_enrichment: true
    automated_workflows: true
    report_generation: true
    api_access: true

  # Limits
  limits:
    max_collections_per_user: 100
    max_entities_per_collection: 10000
    max_workflow_steps: 50
    max_report_size_mb: 100
    max_upload_size_mb: 50

  # Retention Policies
  retention:
    audit_logs_days: 90
    collection_data_days: 365
    temporary_files_hours: 24
    session_data_days: 7
```

## Database Configuration

### PostgreSQL Configuration

**postgresql.conf** (key settings):

```ini
# Connection Settings
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 20MB

# Write-Ahead Logging
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB

# Query Planning
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'csvlog'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'mod'
log_min_duration_statement = 1000
```

### Neo4j Configuration

**neo4j.conf** (key settings):

```ini
# Memory Settings
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=4g
dbms.memory.pagecache.size=4g

# Network
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687
dbms.connector.http.enabled=true
dbms.connector.http.listen_address=0.0.0.0:7474

# Security
dbms.security.auth_enabled=true

# Performance
dbms.transaction.timeout=60s
dbms.lock.acquisition.timeout=30s
```

### MongoDB Configuration

**mongod.conf**:

```yaml
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 0.0.0.0

security:
  authorization: enabled

replication:
  replSetName: osint-rs
```

### Elasticsearch Configuration

**elasticsearch.yml**:

```yaml
cluster.name: osint-cluster
node.name: osint-node-1

path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch

network.host: 0.0.0.0
http.port: 9200

discovery.type: single-node

# Memory
bootstrap.memory_lock: true

# Security
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
```

## Security Configuration

### Firewall Rules

```bash
# UFW Configuration
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### SSL/TLS Configuration

**nginx.conf** (SSL settings):

```nginx
server {
    listen 443 ssl http2;
    server_name api.osint-platform.example;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://api-gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Collector Configuration

### collectors.yaml

```yaml
collectors:
  social_media:
    twitter:
      enabled: true
      rate_limit: 100  # requests per 15 minutes
      timeout: 30
      retry_attempts: 3
      credentials:
        api_key: ${TWITTER_API_KEY}
        api_secret: ${TWITTER_API_SECRET}

    linkedin:
      enabled: true
      rate_limit: 50
      timeout: 30
      credentials:
        client_id: ${LINKEDIN_CLIENT_ID}
        client_secret: ${LINKEDIN_CLIENT_SECRET}

  domain_intelligence:
    whois:
      enabled: true
      timeout: 10
      cache_ttl: 3600

    dns:
      enabled: true
      resolvers:
        - 8.8.8.8
        - 1.1.1.1
      timeout: 5

  threat_intelligence:
    virustotal:
      enabled: true
      api_key: ${VIRUSTOTAL_API_KEY}
      rate_limit: 4  # requests per minute (free tier)

    shodan:
      enabled: true
      api_key: ${SHODAN_API_KEY}
      rate_limit: 1

  public_databases:
    enabled: true
    sources:
      - name: haveibeenpwned
        url: https://haveibeenpwned.com/api/v3
        api_key: ${HIBP_API_KEY}
```

## Analysis Configuration

### analysis.yaml

```yaml
analysis:
  link_analysis:
    max_depth: 5
    algorithms:
      - shortest_path
      - community_detection
      - centrality_analysis
    timeout: 300

  pattern_detection:
    enabled: true
    algorithms:
      - temporal_patterns
      - behavioral_patterns
      - network_patterns
    sensitivity: medium  # low, medium, high

  entity_resolution:
    enabled: true
    similarity_threshold: 0.85
    fuzzy_matching: true
    algorithms:
      - name_matching
      - property_matching
      - relationship_matching

  risk_scoring:
    enabled: true
    factors:
      - name: data_source_credibility
        weight: 0.2
      - name: entity_behavior
        weight: 0.3
      - name: relationship_risk
        weight: 0.3
      - name: threat_intelligence
        weight: 0.2
    recalculation_interval: 3600  # seconds
```

## Workflow Configuration

### Workflow Definition

**workflows/example-workflow.yaml**:

```yaml
name: Automated Entity Investigation
description: Automatically investigate a new entity

trigger:
  type: event
  event: entity.created
  filters:
    - risk_score_min: 50

steps:
  - name: collect_social_media
    action: collector.run
    parameters:
      collector_type: social_media
      entity_id: ${trigger.entity_id}

  - name: enrich_data
    action: enrichment.run
    depends_on: collect_social_media
    parameters:
      entity_id: ${trigger.entity_id}
      enrichment_types:
        - geolocation
        - entity_extraction
        - sentiment_analysis

  - name: analyze_links
    action: analysis.link_analysis
    depends_on: enrich_data
    parameters:
      entity_id: ${trigger.entity_id}
      max_depth: 3

  - name: calculate_risk
    action: risk.calculate
    depends_on: analyze_links
    parameters:
      entity_id: ${trigger.entity_id}

  - name: notify_if_high_risk
    action: notification.send
    depends_on: calculate_risk
    condition: ${steps.calculate_risk.risk_score} > 75
    parameters:
      channel: email
      template: high_risk_alert
      recipients:
        - security@osint-platform.example

notifications:
  on_failure:
    - type: email
      recipients: [admin@osint-platform.example]
  on_success:
    - type: webhook
      url: https://webhook.example.com/workflow-completed
```

## Notification Configuration

### notifications.yaml

```yaml
notifications:
  email:
    enabled: true
    templates_dir: /app/templates/email
    default_sender: noreply@osint-platform.example

  slack:
    enabled: true
    default_channel: '#osint-alerts'
    webhook_url: ${SLACK_WEBHOOK_URL}

  webhook:
    enabled: true
    timeout: 10
    retry_attempts: 3

  sms:
    enabled: false
    provider: twilio
    credentials:
      account_sid: ${TWILIO_ACCOUNT_SID}
      auth_token: ${TWILIO_AUTH_TOKEN}
      from_number: ${TWILIO_FROM_NUMBER}

templates:
  high_risk_alert:
    subject: "High Risk Entity Detected"
    channels: [email, slack]

  workflow_completed:
    subject: "Workflow Completed: {workflow_name}"
    channels: [email]

  collection_failed:
    subject: "Collection Failed: {collection_name}"
    channels: [email, slack]
```

## Logging Configuration

### logging.yaml

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'

  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: /var/log/osint/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 10

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: /var/log/osint/errors.log
    maxBytes: 10485760
    backupCount: 10

  syslog:
    class: logging.handlers.SysLogHandler
    level: WARNING
    formatter: json
    address: /dev/log

loggers:
  app:
    level: DEBUG
    handlers: [console, file, error_file]
    propagate: false

  celery:
    level: INFO
    handlers: [console, file]
    propagate: false

  sqlalchemy.engine:
    level: WARNING
    handlers: [file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

## Performance Configuration

### Performance Tuning

```yaml
performance:
  # Caching
  cache:
    enabled: true
    default_ttl: 300  # seconds
    max_size: 1000    # max cached items

    entity_cache_ttl: 600
    query_cache_ttl: 300
    search_cache_ttl: 180

  # Concurrency
  concurrency:
    api_workers: 4
    celery_workers: 8
    max_threads_per_worker: 4

  # Timeouts
  timeouts:
    api_request: 30
    database_query: 60
    collector_job: 300
    analysis_job: 600
    workflow_execution: 3600

  # Pagination
  pagination:
    default_page_size: 20
    max_page_size: 100

  # Background Processing
  background:
    queue_size: 10000
    batch_size: 100
    flush_interval: 10  # seconds
```

## Environment-Specific Configurations

### Development (.env.development)

```bash
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true

DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/osint_dev
REDIS_URL=redis://localhost:6379/0

JWT_EXPIRATION=86400  # 24 hours for easier development
RATE_LIMIT_ENABLED=false
```

### Staging (.env.staging)

```bash
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=postgresql://staging_user:${DB_PASSWORD}@db.staging:5432/osint_staging
BASE_URL=https://staging-api.osint-platform.example

RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=500
```

### Production (.env.production)

```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@db.prod:5432/osint_prod
BASE_URL=https://api.osint-platform.example

RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100

# Strict security settings
SESSION_COOKIE_SECURE=true
CORS_ALLOW_CREDENTIALS=true
```

---

**Note**: Always use environment variables or secrets management systems for sensitive values. Never commit credentials to version control.
