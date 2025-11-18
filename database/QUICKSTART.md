# OSINT Platform - Database Quick Start Guide

This guide will help you get the database infrastructure up and running in minutes.

## Option 1: Docker Compose (Recommended for Development)

The fastest way to get all databases running locally.

### Step 1: Prerequisites

- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

### Step 2: Configure Environment

```bash
cd database
cp .env.example .env
# Edit .env and set secure passwords
```

### Step 3: Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Elasticsearch (port 9200)
- Kibana (port 5601) - optional
- pgAdmin (port 5050) - optional
- Mongo Express (port 8081) - optional
- Redis (port 6379) - optional

### Step 4: Verify Services

```bash
# Check all services are running
docker-compose ps

# Check PostgreSQL
docker-compose exec postgres psql -U osint_user -d osint_platform -c "\dt"

# Check MongoDB
docker-compose exec mongodb mongosh -u admin -p changeme --eval "db.adminCommand('listDatabases')"

# Check Elasticsearch
curl -X GET "localhost:9200/_cluster/health?pretty"
```

### Step 5: Setup Elasticsearch Indices

```bash
cd elasticsearch
./setup_indices.sh
```

### Step 6: Access Management UIs

- **pgAdmin**: http://localhost:5050 (PostgreSQL management)
- **Mongo Express**: http://localhost:8081 (MongoDB management)
- **Kibana**: http://localhost:5601 (Elasticsearch visualization)

### Stop Services

```bash
docker-compose down
```

### Remove All Data (Fresh Start)

```bash
docker-compose down -v
```

---

## Option 2: Manual Installation

For production or if you prefer installing databases directly.

### Prerequisites

- PostgreSQL 13+
- MongoDB 5.0+
- Elasticsearch 8.0+

### Step 1: Setup PostgreSQL

```bash
cd database/scripts
chmod +x setup_postgres.sh
./setup_postgres.sh
```

When prompted, choose whether to load seed data (development only).

### Step 2: Setup MongoDB

```bash
cd database/mongodb
mongosh < schema.js
```

### Step 3: Setup Elasticsearch

```bash
cd database/elasticsearch
chmod +x setup_indices.sh
./setup_indices.sh
```

---

## Verify Installation

### PostgreSQL

```bash
psql -U osint_user -d osint_platform -c "
SELECT
    'investigations' as table_name, COUNT(*) as rows FROM investigations
UNION ALL
SELECT 'targets', COUNT(*) FROM targets
UNION ALL
SELECT 'users', COUNT(*) FROM users;
"
```

### MongoDB

```bash
mongosh osint_platform --eval "
db.getCollectionNames().forEach(function(collection) {
    print(collection + ': ' + db[collection].countDocuments());
});
"
```

### Elasticsearch

```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

---

## Connection Information

### PostgreSQL

**Connection String:**
```
postgresql://osint_user:changeme@localhost:5432/osint_platform
```

**psql Command:**
```bash
psql -h localhost -p 5432 -U osint_user -d osint_platform
```

### MongoDB

**Connection String:**
```
mongodb://admin:changeme@localhost:27017/osint_platform?authSource=admin
```

**mongosh Command:**
```bash
mongosh "mongodb://localhost:27017/osint_platform" -u admin -p changeme --authenticationDatabase admin
```

### Elasticsearch

**Connection String:**
```
http://localhost:9200
```

**curl Command:**
```bash
curl -X GET "localhost:9200/_cluster/health?pretty"
```

---

## Testing the Setup

### Create a Test Investigation

```bash
psql -U osint_user -d osint_platform << EOF
INSERT INTO users (username, email, password_hash, role)
VALUES ('testuser', 'test@example.com', 'hashed_password', 'analyst')
RETURNING id;

-- Use the returned ID in the next query
INSERT INTO investigations (name, description, status, created_by)
VALUES (
    'Test Investigation',
    'This is a test investigation',
    'active',
    'USER_ID_FROM_ABOVE'
);

SELECT * FROM investigations;
EOF
```

### Insert a Test Log (MongoDB)

```bash
mongosh osint_platform << EOF
db.scraping_logs.insertOne({
    job_id: "test-job-123",
    investigation_id: "test-inv-123",
    timestamp: new Date(),
    level: "info",
    message: "Test log entry",
    url: "https://example.com"
});

db.scraping_logs.find().limit(1);
EOF
```

### Index Test Document (Elasticsearch)

```bash
curl -X POST "localhost:9200/scraped_content/_doc" \
-H 'Content-Type: application/json' \
-d '{
  "url": "https://example.com",
  "title": "Test Page",
  "content": "This is test content for full-text search",
  "created_at": "2024-01-01T00:00:00Z"
}'

curl -X GET "localhost:9200/scraped_content/_search?q=test"
```

---

## Common Issues & Solutions

### PostgreSQL Connection Failed

**Issue:** `psql: error: connection to server at "localhost" failed`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### MongoDB Connection Failed

**Issue:** `MongoNetworkError: connect ECONNREFUSED 127.0.0.1:27017`

**Solution:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Elasticsearch Connection Failed

**Issue:** `curl: (7) Failed to connect to localhost port 9200`

**Solution:**
```bash
# Check if Elasticsearch is running
sudo systemctl status elasticsearch

# Start Elasticsearch
sudo systemctl start elasticsearch

# Check logs
sudo journalctl -u elasticsearch -f
```

### Docker Compose Issues

**Issue:** Containers keep restarting

**Solution:**
```bash
# Check logs
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs elasticsearch

# Check resources
docker stats
```

---

## Next Steps

1. **Read the Documentation**
   - [Database Architecture](./docs/DATABASE_ARCHITECTURE.md)
   - [Main README](./README.md)

2. **Explore the Schema**
   - PostgreSQL: `database/postgresql/schema.sql`
   - MongoDB: `database/mongodb/schema.js`
   - Elasticsearch: `database/elasticsearch/indices.json`

3. **Review Seed Data**
   - `database/scripts/seed_data.sql`

4. **Setup Application**
   - Configure your application to connect to these databases
   - Use the connection strings from above

5. **Configure Monitoring**
   - Set up monitoring for all databases
   - Configure alerts for critical metrics

---

## Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all database connections
- [ ] Configure firewall rules to restrict database access
- [ ] Set up regular backups
- [ ] Enable audit logging
- [ ] Review and apply security best practices
- [ ] Implement role-based access control
- [ ] Encrypt sensitive data at rest
- [ ] Set up intrusion detection
- [ ] Regular security updates

---

## Need Help?

- Check the [Main README](./README.md) for detailed information
- Review [Database Architecture](./docs/DATABASE_ARCHITECTURE.md) for design details
- Check individual database logs for error messages
- Consult official documentation for each database system

---

## Success!

If all services are running and the verification tests pass, you're ready to start developing!

**Web UIs:**
- pgAdmin: http://localhost:5050
- Mongo Express: http://localhost:8081
- Kibana: http://localhost:5601

**Database Ports:**
- PostgreSQL: 5432
- MongoDB: 27017
- Elasticsearch: 9200
- Redis: 6379

Happy developing! 🚀
