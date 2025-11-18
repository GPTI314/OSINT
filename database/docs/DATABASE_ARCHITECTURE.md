# OSINT Platform - Database Architecture

## Overview

The OSINT platform uses a polyglot persistence architecture, leveraging three database systems to optimize for different data types and access patterns:

1. **PostgreSQL** - Relational data and transactional operations
2. **MongoDB** - Unstructured data, logs, and high-write workloads
3. **Elasticsearch** - Full-text search and analytics

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │     │   MongoDB    │     │Elasticsearch │
│              │     │              │     │              │
│ Structured   │     │ Unstructured │     │ Search &     │
│ Relational   │     │ Logs         │     │ Analytics    │
│ Data         │     │ Cache        │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 1. PostgreSQL Schema

### Purpose
PostgreSQL stores structured, relational data that requires ACID compliance, complex queries, and data integrity constraints.

### Core Tables

#### User Management
- **users** - User accounts and authentication
- **api_keys** - API key management for programmatic access

#### Investigation Management
- **investigations** - Core investigation/project tracking
- **targets** - Investigation targets (domains, IPs, emails, etc.)
- **findings** - Investigation findings and insights
- **reports** - Generated investigation reports

#### Data Collection
- **scraping_jobs** - Web scraping job queue and tracking
- **scraped_data** - Collected data from scraping operations
- **crawling_sessions** - Web crawling session management
- **crawled_pages** - Individual crawled pages

#### Intelligence Data
- **intelligence_data** - Generic aggregated intelligence
- **social_intelligence** - Social media OSINT
- **domain_intelligence** - Domain and DNS intelligence
- **ip_intelligence** - IP address intelligence
- **email_intelligence** - Email-related intelligence
- **phone_intelligence** - Phone number intelligence
- **image_intelligence** - Image analysis and reverse search results

#### Audit & Compliance
- **audit_log** - System audit trail

### Key Features

#### Indexes
- B-tree indexes for primary and foreign keys
- GiN indexes for JSONB columns
- Full-text search indexes for content
- Composite indexes for common query patterns

#### Triggers
- Automatic timestamp updates via `update_updated_at_column()` function
- Applied to: investigations, targets, intelligence data, findings

#### Views
- `v_active_investigations` - Active investigations with statistics
- `v_recent_findings` - Recent findings across all investigations
- `v_job_queue_status` - Current job queue status

#### Constraints
- Foreign key constraints with CASCADE and SET NULL
- Check constraints for data validation
- Unique constraints to prevent duplicates

---

## 2. MongoDB Collections

### Purpose
MongoDB handles unstructured data, high-volume logs, and temporary data that doesn't require strict schema validation.

### Collections

#### Logging Collections
- **scraping_logs** - Detailed scraping operation logs
  - TTL: 90 days
  - Indexed by: job_id, investigation_id, timestamp, level

- **crawling_logs** - Crawling session logs
  - TTL: 90 days
  - Indexed by: session_id, investigation_id, timestamp, level

- **error_logs** - System-wide error tracking
  - TTL: 180 days
  - Indexed by: timestamp, error_type, severity, component

- **api_request_logs** - API request/response logs
  - TTL: 90 days
  - Indexed by: timestamp, user_id, endpoint, response_status

#### Operational Collections
- **performance_metrics** - System performance monitoring
  - TTL: 30 days
  - Indexed by: timestamp, metric_type, component

- **raw_responses** - Raw HTTP responses for analysis
  - TTL: 30 days
  - Indexed by: job_id, investigation_id, url, timestamp

- **session_data** - User session storage
  - TTL: 30 days
  - Indexed by: session_id (unique), user_id, active

- **webhook_events** - Webhook event storage
  - TTL: 90 days
  - Indexed by: timestamp, source, event_type, processed

- **notification_queue** - Async notification queue
  - TTL: 30 days
  - Indexed by: status, priority, created_at

- **cache** - Application-level caching
  - TTL: Configurable per entry
  - Indexed by: key (unique), tags

### Key Features

#### Schema Validation
All collections use JSON Schema validation to ensure data quality while maintaining flexibility.

#### TTL Indexes
Automatic data expiration using MongoDB TTL indexes to manage storage and comply with data retention policies.

#### Aggregation Pipeline
Optimized for complex aggregations and analytics queries on log data.

---

## 3. Elasticsearch Indices

### Purpose
Elasticsearch provides powerful full-text search, analytics, and real-time data exploration capabilities.

### Indices

#### Content Search
- **scraped_content** - Full-text search on scraped web content
  - Custom analyzers: `html_analyzer`, `url_analyzer`
  - Fields: content, title, url, metadata
  - Use case: Search across all collected web content

#### Intelligence Search
- **intelligence_data** - Searchable intelligence from all sources
  - Fields: target data, parsed intelligence, threat data
  - Geo-point support for location data
  - Use case: Cross-reference intelligence across sources

- **social_intelligence** - Social media intelligence
  - Nested fields for posts and connections
  - Use case: Social media monitoring and analysis

- **domain_intelligence** - Domain and website intelligence
  - Nested fields for DNS records and technologies
  - Use case: Domain research and technology profiling

#### Findings & Reports
- **findings** - Searchable investigation findings
  - Full-text search on title and description
  - Faceted search by severity, type, status
  - Use case: Find related findings across investigations

#### Centralized Logging
- **logs** - Unified log index with ILM policy
  - Rolling indices: `logs-000001`, `logs-000002`, etc.
  - Lifecycle: Hot (30d) → Warm (60d) → Cold (90d) → Delete
  - Use case: Centralized logging and debugging

### Key Features

#### Index Lifecycle Management (ILM)
Automatic index rollover and retention management for logs:
- Hot phase: Active indexing, max 50GB or 30 days
- Warm phase: Read-only, shrunk and force-merged
- Cold phase: Frozen for reduced resource usage
- Delete phase: Automatic deletion after 90 days

#### Custom Analyzers
- **html_analyzer** - Strips HTML tags, applies stemming
- **url_analyzer** - Specialized tokenization for URLs

#### Nested Objects
Complex data structures for posts, connections, and DNS records.

---

## Data Flow

### Collection Flow
```
1. User creates investigation → PostgreSQL (investigations)
2. Add targets → PostgreSQL (targets)
3. Queue scraping jobs → PostgreSQL (scraping_jobs)
4. Execute scraping:
   - Log operations → MongoDB (scraping_logs)
   - Store raw responses → MongoDB (raw_responses)
   - Save scraped data → PostgreSQL (scraped_data)
   - Index content → Elasticsearch (scraped_content)
5. Process intelligence:
   - Extract intelligence → PostgreSQL (intelligence_data tables)
   - Index for search → Elasticsearch (intelligence_data)
6. Generate findings:
   - Store findings → PostgreSQL (findings)
   - Index for search → Elasticsearch (findings)
```

### Search Flow
```
1. User searches content → Elasticsearch (scraped_content)
2. User searches intelligence → Elasticsearch (intelligence_data)
3. Results linked back to PostgreSQL for full details
```

### Logging Flow
```
1. Application logs → MongoDB (error_logs, api_request_logs)
2. Scraping/Crawling logs → MongoDB (scraping_logs, crawling_logs)
3. All logs also streamed to → Elasticsearch (logs) for search
4. Performance metrics → MongoDB (performance_metrics)
```

---

## Backup & Disaster Recovery

### PostgreSQL
- **Backup**: pg_dump daily, WAL archiving for point-in-time recovery
- **Retention**: 30 days
- **Recovery Time Objective (RTO)**: < 1 hour
- **Recovery Point Objective (RPO)**: < 15 minutes

### MongoDB
- **Backup**: mongodump daily + oplog tailing
- **Retention**: 7 days (logs are expendable)
- **RTO**: < 30 minutes
- **RPO**: < 1 hour

### Elasticsearch
- **Backup**: Snapshot to object storage daily
- **Retention**: 14 days
- **RTO**: < 2 hours
- **RPO**: < 24 hours

---

## Performance Optimization

### PostgreSQL
- Indexes on all foreign keys
- Composite indexes for common query patterns
- JSONB GiN indexes for flexible querying
- Regular VACUUM and ANALYZE
- Connection pooling (PgBouncer)

### MongoDB
- Appropriate indexes on all query patterns
- TTL indexes for automatic cleanup
- Sharding for high-volume collections (if needed)
- Read preference for analytics queries

### Elasticsearch
- Proper shard sizing (aim for 20-50GB per shard)
- ILM for automatic index management
- Force merge on warm indices
- Frozen tier for long-term storage

---

## Scaling Strategy

### Vertical Scaling (Initial)
- PostgreSQL: Start with 4 vCPUs, 16GB RAM
- MongoDB: Start with 4 vCPUs, 8GB RAM
- Elasticsearch: Start with 4 vCPUs, 16GB RAM

### Horizontal Scaling (Growth)
- **PostgreSQL**:
  - Read replicas for analytics queries
  - Partitioning for large tables (scraped_data, crawled_pages)

- **MongoDB**:
  - Sharding on high-volume collections
  - Replica sets for high availability

- **Elasticsearch**:
  - Add data nodes for capacity
  - Add coordinating nodes for query load

---

## Security

### Access Control
- **PostgreSQL**: Role-based access control (RBAC), row-level security
- **MongoDB**: User authentication, role-based permissions
- **Elasticsearch**: Security features, API key authentication

### Encryption
- **At rest**: All databases encrypted at rest
- **In transit**: TLS 1.2+ for all connections
- **Application**: Encrypted JSONB fields for sensitive data

### Audit
- All administrative actions logged to audit_log (PostgreSQL)
- All API requests logged to api_request_logs (MongoDB)
- Query audit logs in Elasticsearch

---

## Monitoring

### Key Metrics

#### PostgreSQL
- Connection count
- Query performance (slow query log)
- Table sizes and index usage
- Cache hit ratio
- Replication lag

#### MongoDB
- Operation latency
- Connection count
- Replication lag
- Disk usage
- TTL index efficiency

#### Elasticsearch
- Indexing rate
- Search latency
- JVM heap usage
- Shard health
- ILM policy execution

### Alerting Thresholds
- Database connection pool > 80%: Warning
- Slow queries > 1s: Warning
- Disk usage > 85%: Critical
- Replication lag > 60s: Critical
- Error rate > 1%: Warning

---

## Development Workflow

### Local Setup
```bash
# PostgreSQL
cd database/scripts
./setup_postgres.sh

# MongoDB
mongosh < ../mongodb/schema.js

# Elasticsearch
cd ../elasticsearch
./setup_indices.sh
```

### Running Migrations
```bash
# PostgreSQL migrations
psql -d osint_platform -f database/migrations/001_initial_schema.sql
```

### Loading Test Data
```bash
# PostgreSQL seed data
psql -d osint_platform -f database/scripts/seed_data.sql
```

---

## Maintenance Tasks

### Daily
- Monitor slow query logs
- Check error logs
- Verify backups completed

### Weekly
- Review index usage
- Analyze query performance
- Check disk usage trends

### Monthly
- Update statistics (ANALYZE)
- Review and optimize indexes
- Archive old data
- Capacity planning review

---

## Future Enhancements

### Phase 2
- [ ] Time-series data with TimescaleDB
- [ ] Graph database (Neo4j) for relationship mapping
- [ ] Redis for caching and pub/sub
- [ ] Message queue (RabbitMQ/Kafka) for async processing

### Phase 3
- [ ] Multi-region deployment
- [ ] Advanced sharding strategies
- [ ] Real-time stream processing
- [ ] Machine learning integration

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [Database Normalization Best Practices](https://en.wikipedia.org/wiki/Database_normalization)
- [Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html)
