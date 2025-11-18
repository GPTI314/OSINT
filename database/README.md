# OSINT Platform - Database

This directory contains all database schemas, migrations, scripts, and documentation for the OSINT platform.

## Directory Structure

```
database/
├── postgresql/          # PostgreSQL schema and related files
│   └── schema.sql      # Complete PostgreSQL schema
├── mongodb/            # MongoDB collections and configurations
│   └── schema.js       # MongoDB collection definitions
├── elasticsearch/      # Elasticsearch indices and mappings
│   ├── indices.json    # Index definitions
│   └── setup_indices.sh # Setup script
├── migrations/         # Database migration files
│   └── 001_initial_schema.sql
├── scripts/            # Utility scripts
│   ├── setup_postgres.sh  # PostgreSQL setup script
│   └── seed_data.sql      # Development seed data
└── docs/               # Documentation
    └── DATABASE_ARCHITECTURE.md  # Comprehensive architecture docs
```

## Quick Start

### Prerequisites

- PostgreSQL 13+ installed and running
- MongoDB 5.0+ installed and running
- Elasticsearch 8.0+ installed and running

### 1. Setup PostgreSQL

```bash
cd database/scripts
./setup_postgres.sh
```

This will:
- Create the database and user
- Run the schema setup
- Optionally load seed data

**Environment Variables:**
```bash
export DB_NAME=osint_platform
export DB_USER=osint_user
export DB_PASSWORD=your_secure_password
export DB_HOST=localhost
export DB_PORT=5432
```

### 2. Setup MongoDB

```bash
cd database/mongodb
mongosh < schema.js
```

This creates all collections with validation rules and indexes.

**Environment Variables:**
```bash
export MONGO_HOST=localhost:27017
export MONGO_DB=osint_platform
export MONGO_USER=osint_user
export MONGO_PASSWORD=your_secure_password
```

### 3. Setup Elasticsearch

```bash
cd database/elasticsearch
./setup_indices.sh
```

This creates all indices with proper mappings and ILM policies.

**Environment Variables:**
```bash
export ES_HOST=localhost:9200
export ES_USER=elastic
export ES_PASS=your_secure_password
```

## Database Overview

### PostgreSQL (Relational Data)

**Purpose:** Structured, relational data with ACID compliance

**Key Tables:**
- `investigations` - Investigation/project management
- `targets` - Investigation targets (domains, IPs, emails, etc.)
- `scraping_jobs` - Web scraping job queue
- `scraped_data` - Collected data
- `intelligence_data` - Aggregated intelligence
- `findings` - Investigation findings
- `users` - User management

**Connection String:**
```
postgresql://osint_user:password@localhost:5432/osint_platform
```

### MongoDB (Unstructured Data & Logs)

**Purpose:** High-volume logs, unstructured data, caching

**Key Collections:**
- `scraping_logs` - Scraping operation logs (TTL: 90 days)
- `crawling_logs` - Crawling session logs (TTL: 90 days)
- `error_logs` - System error logs (TTL: 180 days)
- `performance_metrics` - Performance data (TTL: 30 days)
- `raw_responses` - Raw HTTP responses (TTL: 30 days)
- `session_data` - User sessions (TTL: 30 days)

**Connection String:**
```
mongodb://osint_user:password@localhost:27017/osint_platform
```

### Elasticsearch (Search & Analytics)

**Purpose:** Full-text search, analytics, log aggregation

**Key Indices:**
- `scraped_content` - Searchable web content
- `intelligence_data` - Searchable intelligence
- `findings` - Searchable findings
- `logs` - Centralized logging
- `social_intelligence` - Social media data
- `domain_intelligence` - Domain data

**Connection String:**
```
http://elastic:password@localhost:9200
```

## Common Tasks

### View Database Status

**PostgreSQL:**
```bash
psql -d osint_platform -c "\dt"  # List tables
psql -d osint_platform -c "SELECT COUNT(*) FROM investigations;"
```

**MongoDB:**
```bash
mongosh osint_platform --eval "db.getCollectionNames()"
mongosh osint_platform --eval "db.scraping_logs.countDocuments()"
```

**Elasticsearch:**
```bash
curl -X GET "localhost:9200/_cat/indices?v"
curl -X GET "localhost:9200/scraped_content/_count"
```

### Backup Databases

**PostgreSQL:**
```bash
pg_dump -h localhost -U osint_user osint_platform > backup_$(date +%Y%m%d).sql
```

**MongoDB:**
```bash
mongodump --db=osint_platform --out=backup_$(date +%Y%m%d)
```

**Elasticsearch:**
```bash
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_$(date +%Y%m%d)?wait_for_completion=true"
```

### Restore Databases

**PostgreSQL:**
```bash
psql -h localhost -U osint_user -d osint_platform < backup.sql
```

**MongoDB:**
```bash
mongorestore --db=osint_platform backup_dir/osint_platform
```

**Elasticsearch:**
```bash
curl -X POST "localhost:9200/_snapshot/my_backup/snapshot_name/_restore"
```

### Reset Database (Development Only!)

**PostgreSQL:**
```bash
psql -U postgres -c "DROP DATABASE osint_platform;"
cd database/scripts && ./setup_postgres.sh
```

**MongoDB:**
```bash
mongosh osint_platform --eval "db.dropDatabase()"
mongosh < database/mongodb/schema.js
```

**Elasticsearch:**
```bash
curl -X DELETE "localhost:9200/_all"
cd database/elasticsearch && ./setup_indices.sh
```

## Schema Migrations

### Creating a New Migration

1. Create a new file in `database/migrations/` with format `XXX_description.sql`
2. Include both UP and DOWN migration scripts
3. Update the schema_migrations table

Example:
```sql
-- migrations/002_add_user_preferences.sql

-- UP Migration
ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';

-- Record migration
INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Add user preferences column');
```

### Running Migrations

```bash
psql -d osint_platform -f database/migrations/002_add_user_preferences.sql
```

## Seed Data

The seed data file (`scripts/seed_data.sql`) contains sample data for development and testing.

**⚠️ WARNING:** Never run seed data in production!

**Includes:**
- Sample users (admin, analysts, viewer)
- Sample investigations
- Sample targets and scraping jobs
- Sample findings and intelligence data

## Performance Tuning

### PostgreSQL

**Check slow queries:**
```sql
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

**Analyze table statistics:**
```sql
ANALYZE VERBOSE investigations;
```

**Check index usage:**
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

### MongoDB

**Check slow queries:**
```javascript
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

**Analyze index usage:**
```javascript
db.scraping_logs.aggregate([{ $indexStats: {} }])
```

### Elasticsearch

**Check cluster health:**
```bash
curl -X GET "localhost:9200/_cluster/health?pretty"
```

**Check slow queries:**
```bash
curl -X GET "localhost:9200/_nodes/stats/indices/search?pretty"
```

## Monitoring

### Health Checks

**PostgreSQL:**
```bash
pg_isready -h localhost -p 5432
```

**MongoDB:**
```bash
mongosh --eval "db.adminCommand('ping')"
```

**Elasticsearch:**
```bash
curl -X GET "localhost:9200/_cluster/health"
```

### Metrics to Monitor

- **Connection count**: Ensure connection pools aren't exhausted
- **Query performance**: Monitor slow queries
- **Disk usage**: Track database growth
- **Replication lag**: For replicated setups
- **Cache hit ratio**: PostgreSQL shared buffers
- **Index usage**: Identify unused indexes

## Security Best Practices

1. **Never use default passwords** in production
2. **Use SSL/TLS** for all database connections
3. **Implement row-level security** in PostgreSQL where needed
4. **Regularly rotate credentials** and API keys
5. **Enable audit logging** for compliance
6. **Restrict network access** using firewalls
7. **Encrypt sensitive data** in JSONB fields
8. **Regular security updates** for all database systems

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Check logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Check connections
mongosh --eval "db.serverStatus().connections"

# Check logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Elasticsearch Connection Issues

```bash
# Check if Elasticsearch is running
sudo systemctl status elasticsearch

# Check cluster status
curl -X GET "localhost:9200/_cluster/health?pretty"

# Check logs
sudo tail -f /var/log/elasticsearch/elasticsearch.log
```

## Additional Resources

- [Database Architecture Documentation](./docs/DATABASE_ARCHITECTURE.md)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-notes/)
- [Elasticsearch Best Practices](https://www.elastic.co/guide/en/elasticsearch/reference/current/general-recommendations.html)

## Support

For issues or questions:
1. Check the [DATABASE_ARCHITECTURE.md](./docs/DATABASE_ARCHITECTURE.md) documentation
2. Review logs for error messages
3. Consult the official documentation for each database system
4. Open an issue in the project repository

## License

This database schema is part of the OSINT Platform and is subject to the project's license terms.
