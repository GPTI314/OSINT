# Lead Discovery & Matchmaking System

**WARNING: This system is designed for authorized security testing and research purposes only.**

Use only in controlled environments with proper authorization, consent, and compliance with applicable privacy laws (GDPR, CCPA, etc.).

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Privacy Configuration](#privacy-configuration)
4. [Core Features](#core-features)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Dashboard](#dashboard)
8. [Testing](#testing)
9. [Compliance](#compliance)

---

## Overview

The Lead Discovery & Matchmaking System is a comprehensive platform for:

- **Cookie & Identifier Tracking**: Track user behavior across websites
- **Lead Discovery**: Identify potential customers through signals and patterns
- **Signal Detection**: Detect intent signals (loan needs, consulting needs, etc.)
- **Matchmaking**: Match discovered leads with appropriate services/products
- **Geographic Targeting**: Discover and target leads in specific locations
- **OSINT Integration**: Enrich leads with OSINT profiler data
- **Real-time Alerts**: Get notified of high-value leads and matches

### Key Capabilities

✅ Multi-channel lead discovery
✅ AI-powered signal detection
✅ Intelligent matchmaking algorithm
✅ Privacy-configurable tracking
✅ Geographic and industry targeting
✅ Real-time alerting
✅ OSINT data enrichment
✅ Comprehensive analytics

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Lead Discovery System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Cookie &   │  │     Lead     │  │  Matchmaking │      │
│  │  Identifier  │─▶│  Discovery   │─▶│    Engine    │      │
│  │   Tracking   │  │    Engine    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                   │               │
│         │                 │                   │               │
│  ┌──────▼─────────────────▼───────────────────▼──────┐      │
│  │              PostgreSQL Database                   │      │
│  │  • tracked_identifiers  • lead_signals             │      │
│  │  • user_profiles        • lead_service_matches     │      │
│  │  • discovered_leads     • services_catalog         │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Geographic  │  │   Profiler   │  │    Alert     │      │
│  │  Targeting   │  │ Integration  │  │    System    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

See `migrations/011_lead_discovery_system.sql` for complete schema.

**Key Tables:**
- `tracked_identifiers` - Cookies, emails, phones, user IDs
- `user_profiles` - Aggregated user profiles from identifiers
- `discovered_leads` - Discovered potential customers
- `lead_signals` - Detected intent signals
- `services_catalog` - Available services/products
- `lead_service_matches` - Lead-to-service matches with scores

---

## Privacy Configuration

The system includes **runtime-configurable privacy controls** with GDPR compliance mode.

### Privacy Modes

#### 1. GDPR Strict Mode
```bash
export PRIVACY_MODE=gdpr_strict
export REQUIRE_CONSENT=true
export ANONYMIZE_DATA=true
export ENABLE_CROSS_SITE_TRACKING=false
export ENABLE_FINGERPRINTING=false
```

**Features:**
- ✅ Consent required for all tracking
- ✅ PII anonymization
- ✅ Limited data retention (30-90 days)
- ✅ Full user rights (access, deletion, portability)
- ❌ No cross-site tracking
- ❌ No device fingerprinting

#### 2. Standard Mode (Default)
```bash
export PRIVACY_MODE=standard
export REQUIRE_CONSENT=true
export ANONYMIZE_DATA=true
```

**Features:**
- ✅ Consent for invasive tracking
- ✅ Hash sensitive identifiers
- ✅ Moderate retention (90-365 days)
- ✅ Basic user rights
- ⚠️ Limited cross-site tracking

#### 3. Testing Mode
```bash
export PRIVACY_MODE=testing
export REQUIRE_CONSENT=false
export ENABLE_CROSS_SITE_TRACKING=true
export ENABLE_FINGERPRINTING=true
```

**Features:**
- ❌ No consent required
- ❌ Minimal anonymization
- ✅ Extended retention (365+ days)
- ✅ Full tracking capabilities
- ⚠️ **FOR TESTING ONLY**

### Checking Privacy Configuration

```bash
# API endpoint
curl http://localhost:8000/api/v1/lead-discovery/privacy/config
```

```python
# Python
from lead_discovery.privacy_config import get_privacy_config

privacy = get_privacy_config()
print(f"Mode: {privacy.mode}")
print(f"Requires consent: {privacy.requires_consent('cookies')}")
print(f"Allows fingerprinting: {privacy.allows_fingerprinting()}")
```

---

## Core Features

### 1. Cookie & Identifier Tracking

Track user identifiers across websites to build profiles:

```python
from lead_discovery import CookieTracker

tracker = CookieTracker(db_pool)

# Track cookies
cookies = [
    {'name': '_ga', 'value': 'GA1.2.123456789', 'domain': '.example.com'},
    {'name': 'session', 'value': 'abc123', 'domain': 'example.com'},
]
await tracker.track_cookies(investigation_id, 'https://example.com', cookies)

# Extract identifiers from page
identifiers = await tracker.extract_identifiers(
    page_content=html_content,
    cookies=cookies
)

# Build user profile
profile_id = await tracker.build_user_profile(
    identifiers=[id1, id2, id3],
    investigation_id=investigation_id
)

# Device fingerprinting
fingerprint_id = await tracker.fingerprint_device({
    'userAgent': '...',
    'screenResolution': '1920x1080',
    'timezone': 'America/New_York',
    'language': 'en-US',
    'plugins': ['Chrome PDF Plugin', ...],
})
```

### 2. Lead Discovery

Discover potential leads through various channels:

```python
from lead_discovery import LeadDiscoveryEngine

engine = LeadDiscoveryEngine(db_pool)

# Discover leads by criteria
lead_ids = await engine.discover_leads(investigation_id, {
    'geographic_area': 'San Francisco, CA',
    'radius_km': 50,
    'industry': 'technology',
    'company_size': 'small',
    'lead_category': 'loan',
})

# Scrape for signals
signals = await engine.scrape_for_signals(
    url='https://example.com',
    signal_types=['loan_need', 'consulting_need']
)

# Create lead manually
lead_id = await engine.create_lead(investigation_id, {
    'name': 'John Doe',
    'email': 'john@example.com',
    'company': 'Example Inc',
    'industry': 'technology',
    'lead_category': 'consulting',
}, signals=detected_signals)
```

### 3. Signal Detection

Detect intent signals from content and behavior:

```python
from lead_discovery import LeadSignalDetector

detector = LeadSignalDetector()

# Detect all signals
all_signals = detector.detect_all_signals(
    content="We need help with business expansion financing...",
    metadata={'behavior': behavior_data}
)

# Specific signal types
loan_signals = detector.detect_loan_signals(content, metadata)
consulting_signals = detector.detect_consulting_signals(content, metadata)
growth_signals = detector.detect_growth_signals(content)

# Calculate signal strength
strength = detector.calculate_signal_strength(all_signals)
```

**Detected Signal Types:**
- `loan_need` - Need for business/personal loans
- `consulting_need` - Need for consulting services
- `financial_distress` - Financial difficulty indicators
- `growth` - Business growth signals
- `expansion` - Expansion/scaling signals

### 4. Matchmaking

Match leads with services using multi-factor algorithm:

```python
from lead_discovery import LeadMatchmaker

matchmaker = LeadMatchmaker(db_pool)

# Match lead to services
matches = await matchmaker.match_lead_to_services(lead_id, limit=10)

# Get recommended services
recommendations = await matchmaker.recommend_services(lead_id, limit=5)

# Rank leads for a service
ranked_leads = await matchmaker.rank_leads(
    service_id,
    criteria={'min_match_score': 70, 'location': 'California'},
    limit=100
)

# Find similar leads
similar = await matchmaker.find_similar_leads(lead_id, limit=10)
```

**Matching Factors** (Total: 100 points):
- Geographic match: 0-25 points
- Industry match: 0-20 points
- Need match: 0-25 points
- Profile match: 0-15 points
- Behavioral match: 0-15 points

### 5. Geographic Targeting

Target leads by location:

```python
from lead_discovery import GeographicTargeting

geo = GeographicTargeting(db_pool)

# Discover local leads
local_leads = await geo.discover_local_leads(
    investigation_id,
    location='New York, NY',
    radius_km=25,
    criteria={'industry': 'retail'}
)

# Find nearby businesses
businesses = await geo.find_nearby_businesses(
    location='40.7128,-74.0060',  # lat,lng
    radius_km=10,
    industry='restaurant'
)

# Analyze local market
market_data = await geo.analyze_local_market('Austin, TX')
```

### 6. Profiler Integration

Enrich leads with OSINT profiler data:

```python
from lead_discovery import ProfilerIntegration

integration = ProfilerIntegration(db_pool)

# Enrich lead with profiler data
result = await integration.enrich_lead_with_profiler(
    lead_id,
    username='johndoe',
    email='john@example.com'
)

# Cross-reference with investigation
matches = await integration.cross_reference_findings(
    lead_id,
    investigation_id
)

# Create investigation from lead
inv_id = await integration.create_investigation_from_lead(
    lead_id,
    investigation_name="Deep Dive: John Doe"
)
```

### 7. Alerts

Real-time alerting for important events:

```python
from lead_discovery import LeadAlertSystem

alerts = LeadAlertSystem(db_pool)

# Send custom alert
alert_id = await alerts.send_lead_alert(
    lead_id,
    alert_type='high_score_match',
    title='High Value Match Found',
    message='Lead scored 95% match with Premium Service',
    priority='urgent'
)

# Setup alert rules
rule_ids = await alerts.setup_alert_rules([
    {
        'rule_name': 'High Intent Leads',
        'rule_type': 'new_lead',
        'conditions': {'min_intent_score': 80},
        'alert_channels': ['dashboard', 'email'],
        'priority': 'high'
    }
])

# Get alerts
new_alerts = await alerts.get_alerts(status='new', priority='urgent')
```

---

## API Reference

### Base URL
```
http://localhost:8000/api/v1/lead-discovery
```

### Lead Discovery Endpoints

#### POST /discover
Discover leads based on criteria.

**Request:**
```json
{
  "investigation_id": "uuid",
  "geographic_area": "San Francisco, CA",
  "radius_km": 50,
  "industry": "technology",
  "lead_category": "loan"
}
```

**Response:**
```json
{
  "success": true,
  "leads_discovered": 45,
  "lead_ids": ["uuid1", "uuid2", ...]
}
```

#### GET /leads
List discovered leads.

**Query Parameters:**
- `investigation_id` (UUID) - Filter by investigation
- `status` (string) - Filter by status (new, qualified, contacted, converted, lost)
- `location` (string) - Filter by location
- `industry` (string) - Filter by industry
- `min_signal_strength` (int) - Minimum signal strength
- `limit` (int) - Max results (default: 100)
- `offset` (int) - Pagination offset

**Response:**
```json
{
  "success": true,
  "count": 45,
  "leads": [
    {
      "id": "uuid",
      "name": "John Doe",
      "company": "Example Inc",
      "email": "john@example.com",
      "phone": "555-1234",
      "location": "San Francisco, CA",
      "industry": "technology",
      "signal_strength": 85,
      "intent_score": 75,
      "status": "new"
    }
  ]
}
```

#### GET /leads/{lead_id}
Get detailed lead information.

#### POST /leads/{lead_id}/match
Match lead to services.

#### POST /leads/{lead_id}/enrich
Enrich lead with profiler data.

### Matchmaking Endpoints

#### GET /leads/{lead_id}/matches
Get service matches for lead.

#### GET /services/{service_id}/leads
Get ranked leads for service.

#### PUT /matches/{match_id}/status
Update match status.

### Tracking Endpoints

#### POST /tracking/identifiers
Track an identifier.

#### POST /tracking/cookies
Track cookies from website.

#### POST /tracking/behavior
Track user behavior.

#### GET /tracking/profiles
List user profiles.

#### GET /tracking/profiles/{profile_id}
Get profile details.

### Geographic Endpoints

#### POST /local/discover
Discover local leads.

#### GET /local/market-analysis
Analyze local market.

### Alert Endpoints

#### GET /alerts
List alerts.

#### GET /alerts/summary
Get alert summary statistics.

#### PUT /alerts/{alert_id}/read
Mark alert as read.

### Privacy Endpoints

#### GET /privacy/config
Get privacy configuration.

#### GET /privacy/policy
Get privacy policies.

### Analytics Endpoints

#### GET /analytics/overview
Get analytics overview.

---

## Usage Examples

### Example 1: Discover Leads in Specific Area

```bash
curl -X POST http://localhost:8000/api/v1/lead-discovery/discover \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": "12345678-1234-1234-1234-123456789012",
    "geographic_area": "Austin, TX",
    "radius_km": 30,
    "industry": "restaurant",
    "lead_category": "loan"
  }'
```

### Example 2: Track User Behavior

```python
import asyncio
from lead_discovery import CookieTracker

async def track_user_session():
    tracker = CookieTracker(db_pool)

    # Track cookies
    await tracker.track_cookies(
        investigation_id,
        'https://example.com',
        [
            {'name': '_ga', 'value': 'GA1.2.123456789'},
            {'name': 'user_id', 'value': 'user_12345'},
        ]
    )

    # Track behavior
    await tracker.track_behavior(
        profile_id,
        'page_view',
        {
            'page_path': '/loan-application',
            'time_on_page': 120,
            'scroll_depth': 85,
        },
        'https://example.com'
    )

asyncio.run(track_user_session())
```

### Example 3: Match and Alert

```python
async def match_and_alert():
    matchmaker = LeadMatchmaker(db_pool)
    alerts = LeadAlertSystem(db_pool)

    # Match lead
    matches = await matchmaker.match_lead_to_services(lead_id)

    # Send alert for high-score matches
    for match in matches:
        if match['match_score'] >= 80:
            await alerts.send_match_alert(
                match['match_id'],
                lead_id,
                match['service_id'],
                match['match_score']
            )
```

---

## Dashboard

### Accessing the Dashboard

Navigate to: `http://localhost:3000/lead-discovery`

### Dashboard Features

1. **Overview Tab**
   - Statistics cards (total leads, matches, profiles, alerts)
   - Recent leads list
   - Geographic distribution map

2. **Lead Discovery Tab**
   - Discovery form with criteria
   - Real-time discovery progress
   - Discovered leads table

3. **All Leads Tab**
   - Comprehensive leads table
   - Advanced filtering
   - Bulk actions

4. **Matchmaking Tab**
   - Service catalog
   - Match ranking
   - Match management

5. **Tracking Tab**
   - User profiles list
   - Identifier tracking
   - Behavior timeline

6. **Alerts Tab**
   - Active alerts
   - Alert rules configuration
   - Alert history

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/test_lead_discovery.py -v

# Run specific test
pytest tests/test_lead_discovery.py::test_cookie_tracking -v

# Run with coverage
pytest tests/test_lead_discovery.py --cov=lead_discovery --cov-report=html
```

### Manual Testing

```bash
# Start services
docker-compose up -d

# Run database migrations
alembic upgrade head

# Start API server
uvicorn api.main:app --reload

# In another terminal, test API
curl http://localhost:8000/api/v1/lead-discovery/privacy/config
```

---

## Compliance

### GDPR Compliance

When operating in GDPR-strict mode, the system:

✅ Requires explicit consent for tracking
✅ Anonymizes personal data
✅ Provides data access rights
✅ Enables data deletion
✅ Supports data portability
✅ Limits data retention
✅ Disables cross-site tracking
✅ Disables device fingerprinting

### CCPA Compliance

✅ Opt-out mechanisms
✅ Data access requests
✅ Data deletion requests
✅ Do Not Sell disclosure

### Best Practices

1. **Obtain Consent**: Always obtain explicit consent before tracking
2. **Anonymize Data**: Use hashing for sensitive identifiers
3. **Limit Retention**: Configure appropriate retention periods
4. **Respect Rights**: Honor user data access/deletion requests
5. **Document Purpose**: Clearly document data collection purposes
6. **Regular Audits**: Conduct regular privacy audits
7. **Training**: Train team on privacy requirements

### Legal Disclaimer

This system is provided for **authorized security testing and research purposes only**. Users are responsible for:

- Obtaining proper authorization
- Securing consent where required
- Complying with applicable laws (GDPR, CCPA, etc.)
- Respecting privacy and ethical guidelines
- Using the system only in controlled environments

**Unauthorized use may violate laws and regulations. Use at your own risk.**

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/GPTI314/OSINT/issues
- Documentation: `/docs/LEAD_DISCOVERY.md`
- Privacy Config: `/lead_discovery/privacy_config.py`

---

## License

See LICENSE file for details.
