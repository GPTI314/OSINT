# OSINT Platform - Database Schema Documentation

## Overview

The OSINT platform uses a multi-database architecture to optimize for different data access patterns:

- **PostgreSQL**: Primary relational database for structured data
- **Neo4j**: Graph database for relationship analysis
- **MongoDB**: Document store for unstructured data
- **Elasticsearch**: Search and analytics engine
- **Redis**: Cache and session store

## PostgreSQL Schema

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    users    │────────▶│ collections  │────────▶│   sources   │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │
      │                        ▼
      │                 ┌──────────────┐
      │                 │    items     │
      │                 └──────────────┘
      │                        │
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│  workflows  │         │   entities   │
└─────────────┘         └──────────────┘
      │                        │
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│ executions  │         │ risk_scores  │
└─────────────┘         └──────────────┘
```

### Tables

#### users

User accounts and authentication.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Roles**: `admin`, `analyst`, `user`, `readonly`

#### api_keys

API keys for programmatic access.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    scopes TEXT[],
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

#### collections

Data collection job definitions.

```sql
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    collector_type VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    schedule JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    progress DECIMAL(5,2) DEFAULT 0.00,
    items_collected INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collections_user_id ON collections(user_id);
CREATE INDEX idx_collections_status ON collections(status);
CREATE INDEX idx_collections_collector_type ON collections(collector_type);
CREATE INDEX idx_collections_created_at ON collections(created_at);
```

**Status Values**: `pending`, `running`, `completed`, `failed`, `cancelled`

**Collector Types**: `social_media`, `domain_intel`, `public_db`, `news`, `dark_web`, `custom`

#### sources

Data sources for collections.

```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    base_url VARCHAR(500),
    credentials JSONB,
    config JSONB,
    rate_limit INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    reliability_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_source_type ON sources(source_type);
CREATE INDEX idx_sources_is_active ON sources(is_active);
```

#### collection_items

Raw collected data items.

```sql
CREATE TABLE collection_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    raw_data JSONB NOT NULL,
    item_type VARCHAR(100),
    hash VARCHAR(64) UNIQUE,
    is_processed BOOLEAN DEFAULT FALSE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collection_items_collection_id ON collection_items(collection_id);
CREATE INDEX idx_collection_items_source_id ON collection_items(source_id);
CREATE INDEX idx_collection_items_is_processed ON collection_items(is_processed);
CREATE INDEX idx_collection_items_hash ON collection_items(hash);
```

#### entities

Extracted and identified entities.

```sql
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500),
    properties JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    risk_score INTEGER DEFAULT 0,
    confidence DECIMAL(3,2) DEFAULT 0.50,
    is_verified BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entities_entity_type ON entities(entity_type);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_normalized_name ON entities(normalized_name);
CREATE INDEX idx_entities_risk_score ON entities(risk_score);
CREATE INDEX idx_entities_tags ON entities USING GIN(tags);
CREATE INDEX idx_entities_properties ON entities USING GIN(properties);
```

**Entity Types**: `person`, `organization`, `location`, `domain`, `ip_address`, `email`, `phone`, `cryptocurrency_address`, `username`, `document`

#### entity_sources

Links entities to collection items (many-to-many).

```sql
CREATE TABLE entity_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    collection_item_id UUID NOT NULL REFERENCES collection_items(id) ON DELETE CASCADE,
    confidence DECIMAL(3,2) DEFAULT 0.50,
    extraction_method VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_id, collection_item_id)
);

CREATE INDEX idx_entity_sources_entity_id ON entity_sources(entity_id);
CREATE INDEX idx_entity_sources_collection_item_id ON entity_sources(collection_item_id);
```

#### risk_scores

Historical risk scores for entities.

```sql
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    level VARCHAR(20),
    factors JSONB NOT NULL,
    calculation_method VARCHAR(100),
    calculated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_scores_entity_id ON risk_scores(entity_id);
CREATE INDEX idx_risk_scores_score ON risk_scores(score);
CREATE INDEX idx_risk_scores_level ON risk_scores(level);
CREATE INDEX idx_risk_scores_calculated_at ON risk_scores(calculated_at);
```

**Risk Levels**: `low` (0-25), `medium` (26-50), `high` (51-75), `critical` (76-100)

#### workflows

Automated workflow definitions.

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger JSONB NOT NULL,
    steps JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_status ON workflows(status);
```

#### workflow_executions

Workflow execution history.

```sql
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',
    parameters JSONB,
    results JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_executions_started_at ON workflow_executions(started_at);
```

#### reports

Generated investigation reports.

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    format VARCHAR(20) DEFAULT 'pdf',
    file_path VARCHAR(1000),
    file_size BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_at ON reports(created_at);
```

#### audit_logs

System audit trail.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

## Neo4j Graph Schema

### Node Types

#### Entity
Represents any identified entity from the system.

```cypher
CREATE CONSTRAINT entity_id IF NOT EXISTS
FOR (e:Entity) REQUIRE e.id IS UNIQUE;

CREATE INDEX entity_type IF NOT EXISTS
FOR (e:Entity) ON (e.type);

CREATE INDEX entity_name IF NOT EXISTS
FOR (e:Entity) ON (e.name);
```

**Properties**:
- `id`: UUID (unique)
- `type`: String (person, organization, etc.)
- `name`: String
- `risk_score`: Integer (0-100)
- `properties`: Map
- `created_at`: DateTime
- `updated_at`: DateTime

### Relationship Types

#### RELATED_TO
Generic relationship between entities.

```cypher
CREATE (e1:Entity)-[r:RELATED_TO {
    type: String,
    confidence: Float,
    source: String,
    properties: Map,
    created_at: DateTime
}]->(e2:Entity)
```

**Relationship Sub-types** (via `type` property):
- `WORKS_FOR`: Employment relationship
- `OWNS`: Ownership relationship
- `LOCATED_AT`: Location relationship
- `COMMUNICATES_WITH`: Communication relationship
- `ASSOCIATED_WITH`: General association
- `CONTROLS`: Control relationship
- `MEMBER_OF`: Membership relationship
- `TRANSACTS_WITH`: Transaction relationship

#### COLLECTED_FROM
Links entity to data source.

```cypher
CREATE (e:Entity)-[r:COLLECTED_FROM {
    source_id: String,
    collection_id: String,
    collected_at: DateTime,
    confidence: Float
}]->(s:Source)
```

### Example Queries

**Find all relationships within 2 degrees of an entity:**
```cypher
MATCH path = (e:Entity {id: $entity_id})-[*1..2]-(related)
RETURN path
```

**Find shortest path between two entities:**
```cypher
MATCH path = shortestPath(
  (e1:Entity {id: $entity_id_1})-[*]-(e2:Entity {id: $entity_id_2})
)
RETURN path
```

**Find entities with high centrality:**
```cypher
CALL gds.pageRank.stream('entity-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS entity, score
ORDER BY score DESC
LIMIT 10
```

## MongoDB Collections

### enriched_data

Stores enriched and processed data.

```javascript
{
  _id: ObjectId,
  entity_id: UUID,
  collection_item_id: UUID,
  enrichment_type: String,
  data: Object,
  metadata: {
    enricher: String,
    version: String,
    confidence: Number
  },
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes**:
```javascript
db.enriched_data.createIndex({ entity_id: 1 })
db.enriched_data.createIndex({ collection_item_id: 1 })
db.enriched_data.createIndex({ enrichment_type: 1 })
db.enriched_data.createIndex({ created_at: -1 })
```

### raw_documents

Stores raw unstructured documents.

```javascript
{
  _id: ObjectId,
  collection_id: UUID,
  document_type: String,
  content: String,
  metadata: Object,
  hash: String,
  file_info: {
    filename: String,
    size: Number,
    mime_type: String,
    storage_path: String
  },
  created_at: ISODate
}
```

**Indexes**:
```javascript
db.raw_documents.createIndex({ collection_id: 1 })
db.raw_documents.createIndex({ document_type: 1 })
db.raw_documents.createIndex({ hash: 1 }, { unique: true })
db.raw_documents.createIndex({ created_at: -1 })
db.raw_documents.createIndex({ "metadata.source": 1 })
```

### analysis_results

Stores results from various analyses.

```javascript
{
  _id: ObjectId,
  analysis_id: UUID,
  analysis_type: String,
  input_entities: [UUID],
  results: Object,
  metrics: Object,
  insights: [String],
  created_by: UUID,
  created_at: ISODate
}
```

**Indexes**:
```javascript
db.analysis_results.createIndex({ analysis_id: 1 }, { unique: true })
db.analysis_results.createIndex({ analysis_type: 1 })
db.analysis_results.createIndex({ input_entities: 1 })
db.analysis_results.createIndex({ created_at: -1 })
```

## Elasticsearch Indices

### entities

Full-text search for entities.

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "entity_type": { "type": "keyword" },
      "name": {
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "normalized_name": { "type": "text" },
      "properties": { "type": "object", "enabled": false },
      "tags": { "type": "keyword" },
      "risk_score": { "type": "integer" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  }
}
```

### documents

Full-text search for documents.

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "collection_id": { "type": "keyword" },
      "document_type": { "type": "keyword" },
      "content": { "type": "text" },
      "metadata": { "type": "object" },
      "created_at": { "type": "date" }
    }
  }
}
```

### audit_logs

Searchable audit logs.

```json
{
  "mappings": {
    "properties": {
      "user_id": { "type": "keyword" },
      "action": { "type": "keyword" },
      "resource_type": { "type": "keyword" },
      "resource_id": { "type": "keyword" },
      "details": { "type": "object" },
      "ip_address": { "type": "ip" },
      "created_at": { "type": "date" }
    }
  }
}
```

## Redis Data Structures

### Session Storage

```
Key: session:{session_id}
Type: Hash
TTL: 86400 (24 hours)
Fields:
  - user_id
  - username
  - role
  - created_at
  - last_activity
```

### Rate Limiting

```
Key: rate_limit:{user_id}:{endpoint}
Type: String (counter)
TTL: 60 (1 minute)
```

### Job Queue

```
Queue: celery
Type: List
Items: JSON-encoded job definitions
```

### Cache

```
Key: cache:{resource_type}:{resource_id}
Type: String (JSON)
TTL: 300-3600 (5-60 minutes based on resource type)
```

## Data Migration Strategy

### Version Control

All schema changes are versioned using migration tools:
- **PostgreSQL**: Alembic (Python) or Flyway
- **MongoDB**: Custom migration scripts
- **Neo4j**: Cypher migration scripts
- **Elasticsearch**: Index templates with versioning

### Migration Best Practices

1. **Backward Compatibility**: Ensure migrations don't break existing code
2. **Rollback Support**: All migrations must be reversible
3. **Testing**: Test migrations on staging before production
4. **Data Preservation**: Never lose data during migrations
5. **Incremental Changes**: Small, incremental migrations over large changes

## Backup and Recovery

### Backup Schedule

| Database | Frequency | Retention | Method |
|----------|-----------|-----------|--------|
| PostgreSQL | Hourly incremental, Daily full | 30 days | pg_dump + WAL archiving |
| Neo4j | Daily | 14 days | neo4j-admin backup |
| MongoDB | Daily | 30 days | mongodump |
| Elasticsearch | Daily snapshots | 7 days | Snapshot API |
| Redis | Hourly | 7 days | RDB + AOF |

### Recovery Procedures

1. **Point-in-time Recovery**: PostgreSQL supports PITR using WAL logs
2. **Consistency Check**: Verify data integrity after restore
3. **Cascading Recovery**: Restore databases in order of dependencies
4. **Testing**: Regular restore testing in isolated environment

## Performance Optimization

### PostgreSQL

- **Partitioning**: Partition large tables by date (collection_items, audit_logs)
- **Indexing**: Comprehensive indexing strategy on frequently queried columns
- **Vacuuming**: Regular VACUUM and ANALYZE
- **Connection Pooling**: PgBouncer for connection management

### Neo4j

- **Index Strategy**: Index all frequently queried properties
- **Query Optimization**: Use EXPLAIN and PROFILE for query analysis
- **Memory Configuration**: Adequate heap and page cache sizing

### MongoDB

- **Sharding**: Horizontal sharding for large collections
- **Indexes**: Compound indexes for common query patterns
- **Aggregation**: Use aggregation pipeline for complex queries

### Elasticsearch

- **Index Lifecycle**: Automated rollover and deletion of old indices
- **Sharding**: Appropriate number of shards based on data volume
- **Refresh Interval**: Optimize refresh interval for write-heavy indices

## Security Considerations

1. **Encryption at Rest**: All databases encrypted using native encryption
2. **Encryption in Transit**: TLS for all database connections
3. **Access Control**: Role-based access control for all databases
4. **Sensitive Data**: PII data encrypted in JSONB columns
5. **Audit Logging**: All data access logged for compliance
6. **Regular Updates**: Keep database versions up-to-date with security patches
