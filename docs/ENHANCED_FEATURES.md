# OSINT Platform - Enhanced Features Documentation

This document describes the new enhanced features added to the OSINT Intelligence Platform.

## Table of Contents

- [SEO/SEM Analysis](#seosem-analysis)
- [LinkedIn Intelligence](#linkedin-intelligence)
- [Configurable Lists](#configurable-lists)
- [Austrian Zoning Scraper](#austrian-zoning-scraper)
- [Health & Sanity Checks](#health--sanity-checks)
- [API Integrations](#api-integrations)

---

## SEO/SEM Analysis

Comprehensive SEO (Search Engine Optimization) and SEM (Search Engine Marketing) analysis capabilities.

### Features

#### SEO Analysis

- **On-Page SEO Audit**: Analyze meta tags, headings, images, links, content, and schema markup
- **Technical SEO Check**: HTTPS, robots.txt, sitemap, SSL certificates
- **Keyword Analysis**: Keyword rankings, search volume, difficulty, CPC metrics
- **Backlink Analysis**: Backlink profile and domain authority
- **Competitor Analysis**: Compare SEO metrics with competitors
- **Content Analysis**: Word count, readability, keyword density
- **SERP Tracking**: Search engine results page position tracking
- **Rank Tracking**: Historical keyword ranking data

#### SEM Analysis

- **Keyword Research**: Discover high-value keywords with metrics
- **Ad Copy Analysis**: Evaluate ad effectiveness and quality scores
- **Landing Page Analysis**: Optimize conversion pages
- **Competitor Ads**: Analyze competitor advertising strategies
- **Campaign Insights**: Performance metrics and recommendations

### API Endpoints

```
POST /api/v1/seo-sem/seo/analyze
POST /api/v1/seo-sem/seo/keywords/analyze
GET  /api/v1/seo-sem/seo/keywords/{domain}
POST /api/v1/seo-sem/seo/backlinks
POST /api/v1/seo-sem/seo/competitors
GET  /api/v1/seo-sem/seo/analysis/{domain}

POST /api/v1/seo-sem/sem/keyword-research
POST /api/v1/seo-sem/sem/ad-copy-analysis
POST /api/v1/seo-sem/sem/landing-page-analysis
```

### Example Usage

```bash
# Perform on-page SEO audit
curl -X POST http://localhost:8000/api/v1/seo-sem/seo/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "analysis_type": "on_page",
    "investigation_id": 1
  }'

# Analyze keywords
curl -X POST http://localhost:8000/api/v1/seo-sem/seo/keywords/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "keywords": ["seo tools", "keyword research", "backlink analysis"],
    "location": "United States"
  }'

# SEM keyword research
curl -X POST http://localhost:8000/api/v1/seo-sem/sem/keyword-research \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["marketing software", "crm tools"],
    "location": "United States"
  }'
```

---

## LinkedIn Intelligence

Extract and analyze LinkedIn profiles and companies, create targeted verticals.

### Features

- **Profile Extraction**: Full LinkedIn profile data extraction
- **Company Extraction**: Company page information
- **Employee Extraction**: List company employees with filters
- **Vertical Creation**: Create targeted lists based on criteria
  - Industry vertical
  - Geographic vertical
  - Company size vertical
  - Job title vertical
  - Skill-based vertical
- **Vertical Filtering**: Refine verticals with advanced filters
- **Data Export**: Export to JSON, CSV, or Excel

### API Endpoints

```
POST /api/v1/linkedin/extract-profile
POST /api/v1/linkedin/extract-company
POST /api/v1/linkedin/extract-employees
POST /api/v1/linkedin/create-vertical
GET  /api/v1/linkedin/verticals
GET  /api/v1/linkedin/verticals/{vertical_id}
PUT  /api/v1/linkedin/verticals/{vertical_id}/filter
GET  /api/v1/linkedin/verticals/{vertical_id}/export
```

### Example Usage

```bash
# Extract LinkedIn profile
curl -X POST http://localhost:8000/api/v1/linkedin/extract-profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://linkedin.com/in/example",
    "investigation_id": 1
  }'

# Create vertical (e.g., Software Engineers in San Francisco)
curl -X POST http://localhost:8000/api/v1/linkedin/create-vertical \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "name": "SF Software Engineers",
      "type": "job_title",
      "job_title": "Software Engineer",
      "location": "San Francisco",
      "industry": "Technology"
    },
    "investigation_id": 1
  }'
```

---

## Configurable Lists

Create, manage, and sync custom lists with external platforms.

### Features

- **List Creation**: Create custom lists with configurable columns
- **Item Management**: Add, remove, and update list items
- **Sorting**: Sort lists by any field
- **Filtering**: Apply complex filters to lists
- **Export**: Export to JSON, CSV, or Excel
- **Bulk Operations**: Perform operations on multiple items
- **API Integration**: Sync with Zoho CRM and Notion

### API Endpoints

```
POST   /api/v1/lists/create
GET    /api/v1/lists/{list_id}
POST   /api/v1/lists/{list_id}/items
DELETE /api/v1/lists/{list_id}/items
POST   /api/v1/lists/{list_id}/sort
POST   /api/v1/lists/{list_id}/filter
GET    /api/v1/lists/{list_id}/export
POST   /api/v1/lists/{list_id}/sync/zoho
POST   /api/v1/lists/{list_id}/sync/notion
```

### Example Usage

```bash
# Create a list
curl -X POST http://localhost:8000/api/v1/lists/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Target Companies",
    "type": "companies",
    "description": "List of target companies for outreach",
    "columns": {
      "company_name": "string",
      "industry": "string",
      "employee_count": "number",
      "website": "string"
    }
  }'

# Add items to list
curl -X POST http://localhost:8000/api/v1/lists/1/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "data": {
          "company_name": "Acme Corp",
          "industry": "Technology",
          "employee_count": 500,
          "website": "https://acme.com"
        }
      }
    ]
  }'

# Sync to Zoho CRM
curl -X POST http://localhost:8000/api/v1/lists/1/sync/zoho \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "module": "Leads",
    "field_mapping": {
      "company_name": "Company",
      "website": "Website",
      "industry": "Industry"
    },
    "access_token": "YOUR_ZOHO_TOKEN"
  }'
```

---

## Austrian Zoning Scraper

Specialized scraper for Austrian zoning plans (Flächenwidmungsplan).

### Features

- **Address Search**: Search by street name and house number
- **Zoning Text Extraction**: Extract Plantextbestimmungen
- **Data Parsing**: Parse zoning regulations into structured data
- **Search History**: Track all zoning searches
- **Austrian Format Support**: Handle Austrian address formats

### API Endpoints

```
POST /api/v1/zoning/search
GET  /api/v1/zoning/searches
GET  /api/v1/zoning/searches/{search_id}
```

### Example Usage

```bash
# Search zoning plan
curl -X POST http://localhost:8000/api/v1/zoning/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "street_name": "Hauptstraße",
    "house_number": "123",
    "city": "Vienna",
    "investigation_id": 1
  }'

# Get search history
curl -X GET http://localhost:8000/api/v1/zoning/searches \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Health & Sanity Checks

Comprehensive system health monitoring and validation.

### Health Checks

- **Database Health**: Connection, response time, table counts
- **API Health**: Endpoint availability and response times
- **External Services**: Redis, MongoDB, Elasticsearch status
- **Queue Health**: Celery worker and task status
- **Integration Health**: Zoho and Notion integration status
- **Performance Metrics**: CPU, memory, database size

### Sanity Checks

- **Data Integrity**: Orphaned records, duplicates, consistency
- **Configuration**: Environment variables, database configuration
- **API Responses**: Response format validation
- **Integration Validation**: Integration configuration checks

### API Endpoints

```
GET /api/v1/health/health
GET /api/v1/health/health/detailed
GET /api/v1/health/health/database
GET /api/v1/health/health/api
GET /api/v1/health/health/external-services
GET /api/v1/health/health/queue
GET /api/v1/health/health/integrations
GET /api/v1/health/health/metrics

GET /api/v1/health/sanity
GET /api/v1/health/sanity/data-integrity
GET /api/v1/health/sanity/configuration
GET /api/v1/health/sanity/integrations
```

### Example Usage

```bash
# Run full health check
curl -X GET http://localhost:8000/api/v1/health/health/detailed \
  -H "Authorization: Bearer YOUR_TOKEN"

# Run sanity checks
curl -X GET http://localhost:8000/api/v1/health/sanity \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check data integrity
curl -X GET http://localhost:8000/api/v1/health/sanity/data-integrity \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## API Integrations

### Zoho CRM Integration

Sync lists and data with Zoho CRM.

**Features:**
- OAuth2 authentication
- Sync to Zoho modules (Leads, Contacts, Accounts, etc.)
- Field mapping
- Bidirectional sync
- Create and update records

**Configuration:**
```python
zoho_config = {
    "module": "Leads",
    "field_mapping": {
        "name": "Full_Name",
        "email": "Email",
        "company": "Company"
    },
    "access_token": "your_zoho_access_token",
    "refresh_token": "your_zoho_refresh_token"
}
```

### Notion Integration

Sync lists and data with Notion databases.

**Features:**
- API key authentication
- Sync to Notion databases
- Property mapping
- Create and update pages
- Bidirectional sync

**Configuration:**
```python
notion_config = {
    "database_id": "your_notion_database_id",
    "property_mapping": {
        "name": "Name",
        "email": "Email",
        "company": "Company"
    },
    "api_key": "your_notion_api_key"
}
```

---

## Database Schema

All new features use PostgreSQL with JSON support for flexible data storage.

### New Tables

- `seo_analysis` - SEO analysis results
- `keyword_rankings` - Keyword ranking data
- `backlinks` - Backlink information
- `competitor_analysis` - Competitor comparison data
- `linkedin_profiles` - LinkedIn profile data
- `linkedin_companies` - LinkedIn company data
- `linkedin_verticals` - LinkedIn vertical definitions
- `vertical_filters` - Vertical filtering history
- `configurable_lists` - List definitions
- `list_items` - List item data
- `list_integrations` - Integration configurations
- `zoning_searches` - Zoning search history

### Migration

Run the database migration to create all new tables:

```bash
alembic upgrade head
```

Or manually run:

```bash
python database/migrations/add_enhanced_features.py
```

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migration

```bash
alembic upgrade head
```

### 3. Start the Application

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access API Documentation

Visit: http://localhost:8000/api/docs

---

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# SEO/SEM APIs (optional)
SEMRUSH_API_KEY=your_semrush_key
AHREFS_API_KEY=your_ahrefs_key
MOZ_API_KEY=your_moz_key

# LinkedIn (for production scraping)
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Zoho Integration
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token

# Notion Integration
NOTION_API_KEY=your_notion_api_key
```

---

## Security Notes

### LinkedIn Scraping

**IMPORTANT**: LinkedIn scraping should only be performed:
- With proper authentication and authorization
- Using LinkedIn's official API when possible
- In compliance with LinkedIn's Terms of Service
- For legitimate business purposes with consent

The provided LinkedIn module uses simulated data by default. For production use, integrate with LinkedIn's official API.

### API Rate Limiting

All API endpoints implement rate limiting to prevent abuse. Configure limits in `config/settings.py`.

---

## Support

For issues or questions:
- GitHub Issues: [Repository Issues](https://github.com/your-repo/issues)
- Documentation: [Full Documentation](https://docs.your-domain.com)
- Email: support@your-domain.com

---

## License

MIT License - See LICENSE file for details.
