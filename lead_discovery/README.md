# Lead Discovery & Matchmaking System

**⚠️ WARNING: For Authorized Security Testing Only**

This system is designed for authorized security testing, vulnerability assessment, and research purposes. Use only with proper authorization and in compliance with applicable privacy laws.

## Quick Start

### 1. Configure Privacy Mode

```bash
# Set environment variables
export PRIVACY_MODE=testing          # Options: gdpr_strict, standard, testing
export REQUIRE_CONSENT=false
export ENABLE_CROSS_SITE_TRACKING=true
export ENABLE_FINGERPRINTING=true
```

### 2. Run Database Migrations

```bash
# Apply lead discovery schema
psql -U postgres -d osint_db -f migrations/011_lead_discovery_system.sql
```

### 3. Import Modules

```python
from lead_discovery import (
    CookieTracker,
    IdentifierManager,
    LeadDiscoveryEngine,
    LeadSignalDetector,
    LeadMatchmaker,
    GeographicTargeting,
    ProfilerIntegration,
    LeadAlertSystem,
)

# Initialize with database pool
tracker = CookieTracker(db_pool)
engine = LeadDiscoveryEngine(db_pool)
matchmaker = LeadMatchmaker(db_pool)
```

### 4. Use API Endpoints

```bash
# Discover leads
curl -X POST http://localhost:8000/api/v1/lead-discovery/discover \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_id": "uuid",
    "geographic_area": "San Francisco, CA",
    "industry": "technology"
  }'

# Get privacy configuration
curl http://localhost:8000/api/v1/lead-discovery/privacy/config
```

## Core Components

### 1. Cookie & Identifier Tracking (`cookie_tracker.py`)
- Track cookies, emails, phones, user IDs
- Build user profiles from identifiers
- Cross-site tracking
- Device fingerprinting
- Behavioral tracking

### 2. Lead Discovery (`lead_discovery.py`)
- Discover leads from multiple sources
- Scrape for signals
- Local/geographic discovery
- Industry-based discovery
- Keyword discovery

### 3. Signal Detection (`signal_detector.py`)
- Loan need signals
- Consulting need signals
- Financial distress signals
- Growth signals
- Expansion signals

### 4. Matchmaking (`matchmaker.py`, `matching_algorithm.py`)
- Multi-factor matching algorithm
- Geographic matching
- Industry matching
- Need-based matching
- Profile matching
- Behavioral matching

### 5. Geographic Targeting (`geographic_targeting.py`)
- Location-based discovery
- Radius search
- Local market analysis
- Distance calculation

### 6. Privacy Configuration (`privacy_config.py`)
- Runtime privacy mode switching
- GDPR strict mode
- Standard mode
- Testing mode
- Configurable data retention
- User rights management

### 7. Profiler Integration (`profiler_integration.py`)
- Enrich leads with OSINT data
- Cross-reference findings
- Merge profiles
- Create investigations from leads

### 8. Alerts (`alerts.py`)
- Real-time lead alerts
- Match alerts
- Geographic alerts
- Behavior alerts
- Alert rules

## Module Structure

```
lead_discovery/
├── __init__.py                 # Package exports
├── cookie_tracker.py           # Cookie & identifier tracking
├── identifier_manager.py       # Identifier management
├── lead_discovery.py           # Lead discovery engine
├── signal_detector.py          # Signal detection
├── matchmaker.py               # Matchmaking engine
├── matching_algorithm.py       # Matching algorithm
├── geographic_targeting.py     # Geographic targeting
├── profiler_integration.py     # OSINT profiler integration
├── alerts.py                   # Alert system
├── privacy_config.py           # Privacy configuration
└── README.md                   # This file
```

## Privacy Modes

### GDPR Strict
- ✅ Consent required
- ✅ PII anonymization
- ✅ 30-90 day retention
- ✅ Full user rights
- ❌ No cross-site tracking
- ❌ No fingerprinting

### Standard (Default)
- ✅ Consent for invasive tracking
- ✅ Hash sensitive data
- ✅ 90-365 day retention
- ⚠️ Limited tracking

### Testing
- ❌ No consent required
- ❌ Minimal anonymization
- ✅ Full tracking capabilities
- ⚠️ **FOR TESTING ONLY**

## Examples

### Example 1: Track and Discover

```python
# Track cookies
await tracker.track_cookies(
    investigation_id,
    'https://example.com',
    [{'name': '_ga', 'value': 'GA1.2.123456789'}]
)

# Discover leads
lead_ids = await engine.discover_leads(investigation_id, {
    'geographic_area': 'Austin, TX',
    'radius_km': 25,
    'industry': 'restaurant',
})
```

### Example 2: Detect and Match

```python
# Detect signals
detector = LeadSignalDetector()
signals = detector.detect_loan_signals(content, {})

# Create lead
lead_id = await engine.create_lead(investigation_id, lead_data, signals)

# Match to services
matches = await matchmaker.match_lead_to_services(lead_id)
```

### Example 3: Alerts

```python
# Setup alert rule
await alerts.setup_alert_rules([{
    'rule_name': 'High Value Leads',
    'rule_type': 'new_lead',
    'conditions': {'min_intent_score': 80},
    'alert_channels': ['dashboard', 'email'],
}])
```

## Testing

```bash
# Run tests
pytest tests/test_lead_discovery.py -v

# Run with coverage
pytest tests/test_lead_discovery.py --cov=lead_discovery --cov-report=html
```

## Documentation

Full documentation: `/docs/LEAD_DISCOVERY.md`

- Architecture
- API Reference
- Privacy & Compliance
- Usage Examples
- Dashboard Guide

## Legal Notice

**This system is for authorized security testing and research only.**

Users must:
- Obtain proper authorization
- Secure consent where required
- Comply with GDPR, CCPA, and other privacy laws
- Use only in controlled environments
- Document legitimate use cases

Unauthorized use may violate laws. Use at your own risk.

## Support

- Documentation: `/docs/LEAD_DISCOVERY.md`
- Tests: `/tests/test_lead_discovery.py`
- API: `http://localhost:8000/api/docs`

## License

See LICENSE file.
