# OSINT Platform - Frequently Asked Questions (FAQ)

## Table of Contents

1. [General Questions](#general-questions)
2. [Account and Authentication](#account-and-authentication)
3. [Data Collection](#data-collection)
4. [Entities and Relationships](#entities-and-relationships)
5. [Risk Scoring](#risk-scoring)
6. [Workflows and Automation](#workflows-and-automation)
7. [Reports and Exports](#reports-and-exports)
8. [Performance and Limits](#performance-and-limits)
9. [Privacy and Security](#privacy-and-security)
10. [Troubleshooting](#troubleshooting)
11. [API and Integration](#api-and-integration)

---

## General Questions

### What is the OSINT Platform?

The OSINT Platform is a comprehensive tool for collecting, analyzing, and visualizing open-source intelligence data. It helps investigators gather information from publicly available sources, identify relationships between entities, assess risks, and generate professional reports.

### What does OSINT stand for?

OSINT stands for Open-Source Intelligence - intelligence collected from publicly available sources such as social media, public databases, websites, and other open sources.

### Who should use the OSINT Platform?

The platform is designed for:
- Security analysts and investigators
- Fraud prevention teams
- Compliance and risk management professionals
- Journalists and researchers
- Law enforcement agencies
- Corporate security teams
- Due diligence professionals

### Is the OSINT Platform legal to use?

Yes, when used properly. The platform collects data only from publicly available sources. However, users must:
- Comply with local laws and regulations
- Respect privacy laws (GDPR, CCPA, etc.)
- Obtain proper authorization for investigations
- Use collected data ethically and legally

### What sources does the platform collect data from?

The platform can collect from:
- Social media platforms (Twitter, LinkedIn, Facebook)
- Public databases and registries
- WHOIS and DNS records
- News articles and media outlets
- Threat intelligence feeds
- Government databases
- Public court records
- Custom sources (via API)

### How much does it cost?

Pricing varies by deployment:
- Self-hosted: Open-source (free) or enterprise license
- Cloud SaaS: Tiered pricing based on usage
- Contact your administrator or sales team for specific pricing

---

## Account and Authentication

### How do I create an account?

1. Navigate to the platform URL
2. Click "Sign Up" or "Register"
3. Fill in your information
4. Verify your email address
5. Log in with your credentials

For enterprise deployments, contact your administrator to create an account.

### I forgot my password. How do I reset it?

1. Click "Forgot Password" on the login page
2. Enter your email address
3. Check your email for reset instructions
4. Click the reset link
5. Enter your new password

### How do I enable two-factor authentication (2FA)?

1. Go to **User Profile** > **Settings**
2. Click **Security**
3. Click **Enable Two-Factor Authentication**
4. Scan the QR code with your authenticator app
5. Enter the verification code
6. Save your backup codes

Supported authenticator apps: Google Authenticator, Authy, Microsoft Authenticator

### Can I use API keys instead of logging in?

Yes. Generate API keys for programmatic access:
1. Go to **User Profile** > **Settings** > **API Keys**
2. Click **Generate New API Key**
3. Configure scopes and expiration
4. Copy and securely store the key

API keys are ideal for automation and integrations.

### How long do sessions last?

Default session timeout is 24 hours of inactivity. Administrators can configure this setting. You can also manually log out at any time.

---

## Data Collection

### How do I start collecting data?

1. Navigate to **Collections** > **New Collection**
2. Choose a collector type
3. Configure collection parameters
4. Click **Create Collection**
5. Monitor progress in the collections list

See [Tutorial 1](TUTORIALS.md#tutorial-1-your-first-investigation) for a detailed walkthrough.

### How long does a collection take?

Collection time varies based on:
- Collector type (seconds to hours)
- Amount of data requested
- API rate limits
- Network conditions
- System load

Typical times:
- WHOIS lookup: < 1 minute
- Social media search: 5-30 minutes
- Comprehensive investigation: 1-6 hours

### Can I schedule collections to run automatically?

Yes. When creating or editing a collection:
1. Enable **Schedule**
2. Set frequency (hourly, daily, weekly, monthly)
3. Configure start time
4. Optionally set end date

Scheduled collections run automatically at the specified intervals.

### What happens if a collection fails?

Failed collections:
- Are marked with "Failed" status
- Include error messages in logs
- Can be retried manually
- Trigger failure notifications (if configured)

Common failure reasons:
- API rate limits exceeded
- Invalid credentials
- Network timeouts
- Source unavailable

### How do I stop a running collection?

1. Go to **Collections**
2. Find the running collection
3. Click **Stop** or **Cancel**
4. Confirm the action

Note: Partial data may be saved depending on the collector.

### Are there limits on data collection?

Yes, limits vary by user role and plan:
- Max collections per user
- Max items per collection
- Rate limits per source
- Storage quotas
- Concurrent collections

Check your plan details or contact your administrator.

---

## Entities and Relationships

### What is an entity?

An entity is any identifiable object tracked in the system:
- Person
- Organization
- Location
- Domain
- IP address
- Email address
- Phone number
- Username
- Cryptocurrency address

### How are entities created?

Entities can be created:
1. **Automatically**: Extracted from collected data
2. **Manually**: Created by users
3. **Via API**: Created programmatically
4. **From imports**: Uploaded from CSV/JSON

### Can I merge duplicate entities?

Yes. To merge duplicates:
1. Select entities to merge
2. Click **Merge Entities**
3. Review proposed merge
4. Choose primary entity
5. Confirm merge

The platform also suggests potential duplicates automatically.

### What is a relationship?

A relationship is a connection between two entities, such as:
- Person WORKS_FOR Organization
- Person OWNS Domain
- Organization LOCATED_AT Location

Relationships have types, properties, and confidence scores.

### How do I create a relationship?

1. Navigate to **Relationships** > **New Relationship**
2. Select source entity
3. Select target entity
4. Choose relationship type
5. Add properties (optional)
6. Click **Create Relationship**

Or create from entity detail page by clicking **Add Relationship**.

### Can relationships have a time component?

Yes. Relationships can include:
- Start date
- End date
- First observed
- Last observed

This enables temporal analysis and timeline visualization.

---

## Risk Scoring

### How are risk scores calculated?

Risk scores (0-100) are calculated using multiple factors:
- **Data Source Credibility** (20%): Source reliability
- **Entity Behavior** (30%): Activity patterns
- **Relationship Risk** (30%): Connected entity risks
- **Threat Intelligence** (20%): External threat data

Administrators can adjust these weights.

### What do risk levels mean?

Risk levels are:
- **Low (0-25)**: Minimal risk, routine monitoring
- **Medium (26-50)**: Moderate risk, periodic review
- **High (51-75)**: Elevated risk, active monitoring
- **Critical (76-100)**: Severe risk, immediate attention

### Can I manually adjust risk scores?

Yes. To override automatic scores:
1. Open entity details
2. Click **Adjust Risk Score**
3. Enter new score
4. Provide justification
5. Click **Save**

Manual adjustments are logged for audit purposes.

### How often are risk scores updated?

Risk scores are updated:
- When new data is collected
- During scheduled recalculations (default: daily)
- When relationships change
- When manual adjustments are made
- On-demand via workflows

### Can I get alerts for high-risk entities?

Yes. Configure risk alerts:
1. Go to **Settings** > **Notifications**
2. Enable **Risk Alerts**
3. Set threshold (e.g., score > 75)
4. Choose notification method
5. Save settings

---

## Workflows and Automation

### What are workflows?

Workflows are automated sequences of actions that:
- Collect data
- Enrich information
- Analyze relationships
- Calculate risk
- Send notifications
- Generate reports

Workflows save time and ensure consistent processes.

### How do I create a workflow?

1. Navigate to **Workflows** > **New Workflow**
2. Configure trigger (manual, scheduled, or event)
3. Add workflow steps
4. Configure step parameters
5. Set dependencies and conditions
6. Enable notifications
7. Save and activate workflow

See [Tutorial 5](TUTORIALS.md#tutorial-5-creating-custom-workflows) for detailed instructions.

### Can workflows run on a schedule?

Yes. Workflows support:
- **Manual triggers**: Run on-demand
- **Scheduled triggers**: Run at specified times
- **Event triggers**: Run when events occur (e.g., entity created)

### What happens if a workflow step fails?

Workflow error handling options:
- **Stop**: Halt workflow execution
- **Continue**: Proceed to next step
- **Retry**: Attempt step again (configurable retries)
- **Notify**: Send alert to administrators

Configure error handling per step.

### Can I share workflows with my team?

Yes, if you have appropriate permissions. Workflows can be:
- Private (only you)
- Team (your team members)
- Organization-wide (all users)

---

## Reports and Exports

### How do I generate a report?

1. Navigate to **Reports** > **New Report**
2. Enter title and description
3. Select entities to include
4. Choose report sections
5. Select output format (PDF, DOCX, JSON)
6. Click **Generate Report**
7. Download when complete

### What formats are available for reports?

Reports can be generated in:
- **PDF**: Professional document (recommended)
- **DOCX**: Editable Microsoft Word document
- **JSON**: Structured data export
- **HTML**: Web-viewable report
- **CSV**: Data tables (for specific reports)

### Can I customize report templates?

Yes. Options:
- Use built-in templates
- Customize existing templates
- Create custom templates (admin only)
- Upload organization branding

Administrators can create organization-wide templates.

### How do I export data?

Export options:
1. **Entity export**: CSV/JSON from entity list
2. **Collection results**: JSON/CSV download
3. **Graph data**: GEXF, GraphML formats
4. **Complete reports**: PDF/DOCX
5. **API export**: Programmatic data access

### Can reports be scheduled and emailed automatically?

Yes. For recurring reports:
1. Create or edit a report
2. Enable **Schedule**
3. Set frequency and time
4. Add email recipients
5. Save report

Reports will be automatically generated and emailed.

---

## Performance and Limits

### How many entities can I create?

Limits depend on your plan:
- **Free/Basic**: 1,000 entities
- **Professional**: 10,000 entities
- **Enterprise**: Unlimited

Contact your administrator for specific limits.

### How much storage do I have?

Storage quotas vary by plan:
- **Free**: 5 GB
- **Professional**: 50 GB
- **Enterprise**: Custom

Storage includes collected data, reports, and uploads.

### Why is the platform slow?

Common causes:
- Large dataset queries
- Complex graph visualizations
- Concurrent collections
- System maintenance
- Network issues

Solutions:
- Use filters to narrow results
- Limit graph depth
- Schedule intensive tasks off-peak
- Clear browser cache
- Contact support if persistent

### Can I increase my rate limits?

Yes. Options:
- Upgrade to a higher plan
- Contact support for custom limits
- Use API keys with dedicated limits
- Implement request queuing

### How long is data retained?

Default retention policies:
- **Entities**: Indefinite
- **Collection data**: 365 days
- **Audit logs**: 90 days
- **Temporary files**: 24 hours
- **Reports**: 30 days

Administrators can customize retention policies.

---

## Privacy and Security

### Is my data secure?

Yes. Security measures include:
- **Encryption at rest**: AES-256
- **Encryption in transit**: TLS 1.3
- **Access control**: Role-based permissions
- **Audit logging**: Complete activity trail
- **Regular backups**: Daily automated backups
- **Security updates**: Regular patches

### Who can see my data?

Data visibility depends on:
- **Personal data**: Only you (private)
- **Team data**: Your team members
- **Organization data**: Users with permissions
- **Shared items**: Explicitly shared users

Administrators can configure default visibility.

### Is the platform GDPR compliant?

Yes. GDPR features include:
- Data minimization
- Consent management
- Right to erasure (delete data)
- Data portability (export)
- Privacy by design
- Audit trails

Consult legal counsel for specific compliance requirements.

### Can I delete my data?

Yes. Options:
- Delete individual entities
- Delete collections
- Delete reports
- Request account deletion (removes all data)

Some data may be retained for audit purposes per policy.

### How is sensitive data handled?

Sensitive data handling:
- Automatic detection and masking in logs
- Encryption of PII fields
- Restricted access controls
- Redaction in exports (optional)
- Compliance with data protection laws

---

## Troubleshooting

### I can't log in. What should I do?

Troubleshooting steps:
1. Verify email and password are correct
2. Check Caps Lock is off
3. Try password reset
4. Clear browser cookies/cache
5. Try a different browser
6. Check if account is locked (contact admin)
7. Verify platform is operational

### Collections are not running. Why?

Check:
- Collection status (pending vs. failed)
- API credentials are valid
- Rate limits not exceeded
- Source is accessible
- Sufficient storage available
- Network connectivity
- Review error logs

### Entities are not appearing in search. Why?

Possible causes:
- Search index not updated (wait a few minutes)
- Filters too restrictive
- Entity is private (no permission)
- Spelling or syntax errors
- Entity not yet created

Try:
- Refresh page
- Clear filters
- Use wildcards (*)
- Browse entity list instead

### The graph visualization is not loading. What should I do?

Solutions:
- Refresh page
- Reduce graph depth
- Limit number of entities
- Try different browser
- Disable browser extensions
- Check browser console for errors
- Update browser to latest version

### I'm getting "Rate Limit Exceeded" errors. What does this mean?

This means you've exceeded request limits. Solutions:
- Wait for rate limit window to reset
- Reduce request frequency
- Upgrade to higher plan
- Use API keys with higher limits
- Contact administrator

### Reports are failing to generate. Why?

Common issues:
- Too many entities selected
- Graph too complex
- Insufficient storage
- Template errors
- System overload

Solutions:
- Reduce entity count
- Simplify report sections
- Try different format
- Wait and retry
- Contact support

---

## API and Integration

### How do I access the API?

1. Generate an API key (see Account section)
2. Review API documentation at `/docs` or `/api/docs`
3. Use the API key in Authorization header
4. Make requests to API endpoints

See [Tutorial 8](TUTORIALS.md#tutorial-8-using-the-api) for examples.

### What can I do with the API?

The API supports:
- Entity creation and management
- Collection execution
- Relationship management
- Risk score calculation
- Workflow execution
- Report generation
- Search and filtering
- Data export

See the [API Documentation](../technical/API.yaml) for complete reference.

### Are there API rate limits?

Yes. Default limits:
- **Standard users**: 100 requests/minute
- **Premium users**: 1000 requests/minute
- **API keys**: Custom limits

Exceeding limits returns HTTP 429 (Too Many Requests).

### Can I integrate with other tools?

Yes. Integration options:
- **REST API**: Standard HTTP/JSON API
- **Webhooks**: Event notifications
- **Export formats**: CSV, JSON, GEXF, GraphML
- **STIX/TAXII**: Threat intelligence sharing
- **SIEM integration**: Syslog, webhooks
- **Custom integrations**: Via API

### Is there an API client library?

API client libraries:
- **Python**: Official SDK available
- **JavaScript/Node.js**: Official SDK available
- **Other languages**: Use standard HTTP libraries

See the SDK documentation for installation and usage.

### How do I report API issues?

1. Check API status page
2. Review error messages and codes
3. Consult API documentation
4. Check community forum
5. Contact API support: api-support@osint-platform.example

Include request details, error messages, and timestamps.

---

## Still Have Questions?

### Documentation Resources

- [User Guide](USER_GUIDE.md) - Comprehensive platform guide
- [Tutorials](TUTORIALS.md) - Step-by-step tutorials
- [Best Practices](BEST_PRACTICES.md) - Usage recommendations
- [Technical Documentation](../technical/) - For developers and administrators

### Support Channels

- **Email**: support@osint-platform.example
- **Community Forum**: forum.osint-platform.example
- **Knowledge Base**: kb.osint-platform.example
- **Video Tutorials**: videos.osint-platform.example

### Emergency Support

For critical issues:
- Contact your system administrator
- Check status page: status.osint-platform.example
- Emergency hotline: (for enterprise customers)

---

**Last Updated**: November 2025

This FAQ is regularly updated. If you can't find an answer to your question, please contact support.
