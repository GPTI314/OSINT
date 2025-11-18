# OSINT Platform

> Comprehensive Open-Source Intelligence (OSINT) platform for investigations, threat intelligence, and security research.

## Overview

The OSINT Platform is a professional-grade intelligence gathering and analysis system designed for security researchers, threat analysts, and investigators. It provides modular collectors, enrichment pipelines, link analysis, risk scoring, and investigative workflow automation.

### Key Features

- **Multi-Source Intelligence Gathering**: Collect data from domains, IPs, emails, social media, and more
- **Automated Web Scraping & Crawling**: Intelligent data collection with queue management
- **Advanced Search & Analytics**: Full-text search powered by Elasticsearch
- **Investigation Management**: Organize and track complex investigations
- **Intelligence Enrichment**: Automated correlation and analysis
- **Reporting & Visualization**: Generate comprehensive investigation reports
- **API-First Architecture**: RESTful APIs for integration and automation

## Architecture

The platform uses a modern polyglot persistence architecture:

- **PostgreSQL**: Structured data, investigations, and intelligence
- **MongoDB**: Unstructured data, logs, and high-volume operations
- **Elasticsearch**: Full-text search and analytics
- **Redis**: Caching and pub/sub (optional)

```
┌─────────────────────────────────────────────┐
│          Application Layer                  │
│  (REST API, Web UI, CLI Tools)             │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   PostgreSQL   MongoDB   Elasticsearch
   (Relational) (Logs)    (Search)
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd OSINT

# Setup databases
cd database
cp .env.example .env
# Edit .env with secure passwords

# Start all services
docker-compose up -d

# Setup Elasticsearch indices
cd elasticsearch
./setup_indices.sh

# Verify everything is running
docker-compose ps
```

Access the management UIs:
- **pgAdmin**: http://localhost:5050
- **Mongo Express**: http://localhost:8081
- **Kibana**: http://localhost:5601

For detailed instructions, see [Database Quick Start Guide](./database/QUICKSTART.md).

## Database Schema

The database schema is production-ready and includes:

### PostgreSQL Tables
- **Investigations & Targets**: Core investigation management
- **Scraping & Crawling**: Web data collection infrastructure
- **Intelligence Data**: Domain, IP, email, social media, phone, and image intelligence
- **Findings & Reports**: Investigation results and documentation
- **Users & Authentication**: User management and access control
- **Audit Logging**: Complete audit trail

### MongoDB Collections
- **Logs**: Scraping, crawling, errors, and API requests
- **Performance Metrics**: System monitoring data
- **Raw Responses**: HTTP response storage
- **Sessions**: User session management
- **Notifications**: Async notification queue

### Elasticsearch Indices
- **scraped_content**: Full-text search on web content
- **intelligence_data**: Searchable intelligence
- **findings**: Investigation findings search
- **logs**: Centralized log search

For complete schema documentation, see:
- [Database Architecture](./database/docs/DATABASE_ARCHITECTURE.md)
- [Database README](./database/README.md)

## Directory Structure

```
OSINT/
├── database/                    # Database schemas and setup
│   ├── postgresql/             # PostgreSQL schema
│   ├── mongodb/                # MongoDB collections
│   ├── elasticsearch/          # Elasticsearch indices
│   ├── migrations/             # Schema migrations
│   ├── scripts/                # Setup and utility scripts
│   ├── docs/                   # Database documentation
│   ├── docker-compose.yml      # Docker setup
│   ├── README.md              # Database guide
│   └── QUICKSTART.md          # Quick start guide
├── src/                        # Application source code (TBD)
├── docs/                       # Project documentation
└── README.md                   # This file
```

## Development Setup

### Prerequisites

- Docker & Docker Compose (for containerized setup)
- OR manually install:
  - PostgreSQL 13+
  - MongoDB 5.0+
  - Elasticsearch 8.0+

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd OSINT
   ```

2. **Setup Databases**
   ```bash
   cd database
   # Using Docker
   docker-compose up -d

   # OR manually
   ./scripts/setup_postgres.sh
   mongosh < mongodb/schema.js
   ./elasticsearch/setup_indices.sh
   ```

3. **Verify Installation**
   ```bash
   # PostgreSQL
   psql -U osint_user -d osint_platform -c "\dt"

   # MongoDB
   mongosh osint_platform --eval "db.getCollectionNames()"

   # Elasticsearch
   curl -X GET "localhost:9200/_cat/indices?v"
   ```

4. **Load Development Data** (Optional)
   ```bash
   psql -U osint_user -d osint_platform -f database/scripts/seed_data.sql
   ```

## Documentation

- [Database Architecture](./database/docs/DATABASE_ARCHITECTURE.md) - Comprehensive database design
- [Database README](./database/README.md) - Database setup and maintenance
- [Quick Start Guide](./database/QUICKSTART.md) - Get started in minutes

## Use Cases

### Threat Intelligence
- Monitor adversary infrastructure
- Track phishing campaigns
- Analyze malware C2 servers
- Correlate threat indicators

### Brand Protection
- Detect brand impersonation
- Monitor social media for abuse
- Identify fraudulent websites
- Track intellectual property theft

### Security Research
- Map attack surfaces
- Enumerate subdomains
- Discover exposed data
- Analyze breach databases

### Investigations
- Track digital footprints
- Correlate open-source data
- Generate evidence reports
- Timeline analysis

## API Examples

Coming soon - RESTful API for all operations.

## Security Considerations

- All passwords should be changed from defaults
- Enable SSL/TLS for all database connections
- Implement proper access controls
- Regular security updates
- Audit logging enabled by default
- Follow security best practices in [Database Architecture](./database/docs/DATABASE_ARCHITECTURE.md)

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Roadmap

- [x] Database schema design
- [ ] REST API implementation
- [ ] Web scraping engine
- [ ] Intelligence enrichment modules
- [ ] Web UI dashboard
- [ ] CLI tools
- [ ] Docker deployment
- [ ] Kubernetes support
- [ ] Machine learning integration

## License

[License information to be added]

## Support

For issues, questions, or contributions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with details

## Acknowledgments

This platform is built for legitimate security research, threat intelligence, and investigative purposes only.
