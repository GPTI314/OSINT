# OSINT Platform - Tutorials

## Table of Contents

1. [Tutorial 1: Your First Investigation](#tutorial-1-your-first-investigation)
2. [Tutorial 2: Automated Social Media Monitoring](#tutorial-2-automated-social-media-monitoring)
3. [Tutorial 3: Domain Investigation](#tutorial-3-domain-investigation)
4. [Tutorial 4: Link Analysis and Network Mapping](#tutorial-4-link-analysis-and-network-mapping)
5. [Tutorial 5: Creating Custom Workflows](#tutorial-5-creating-custom-workflows)
6. [Tutorial 6: Risk Assessment and Monitoring](#tutorial-6-risk-assessment-and-monitoring)
7. [Tutorial 7: Generating Investigation Reports](#tutorial-7-generating-investigation-reports)
8. [Tutorial 8: Using the API](#tutorial-8-using-the-api)

---

## Tutorial 1: Your First Investigation

**Objective**: Learn the basics by investigating a person or organization.

**Duration**: 15 minutes

**Prerequisites**: Active account on the OSINT platform

### Step 1: Create Your First Entity

1. Log in to the platform
2. Click **Entities** in the navigation menu
3. Click **New Entity** button
4. Fill in the form:
   - **Type**: Select "Person"
   - **Name**: Enter "John Smith"
   - **Properties**: Add any known information:
     - Email: john.smith@example.com
     - Location: New York, USA
   - **Tags**: Add tag "tutorial-1"
5. Click **Create Entity**

### Step 2: Collect Data

1. Navigate to **Collections** > **New Collection**
2. Configure the collection:
   - **Name**: "John Smith Social Media Search"
   - **Description**: "Initial data gathering for John Smith"
   - **Collector Type**: Select "Social Media"
3. Configure collector settings:
   - **Platform**: Twitter
   - **Search Terms**: "John Smith" "New York"
   - **Max Items**: 50
4. Click **Create Collection**
5. Wait for collection to complete (monitor progress bar)

### Step 3: Review Collected Data

1. Go back to **Collections**
2. Click on your completed collection
3. Click **View Results** tab
4. Review the collected items:
   - Social media posts
   - Profile information
   - Timestamps and sources

### Step 4: Link Entities

1. Return to **Entities**
2. Notice new entities automatically created from the collection
3. Click on "John Smith" entity
4. Click **Relationships** tab
5. Review automatically discovered relationships
6. Manually add a relationship:
   - Click **Add Relationship**
   - Select a related entity
   - Choose relationship type (e.g., "WORKS_FOR")
   - Click **Create**

### Step 5: View the Network

1. While viewing the "John Smith" entity
2. Click **Analyze Relationships** button
3. Configure analysis:
   - **Max Depth**: 2
   - **Relationship Types**: All
4. Click **Run Analysis**
5. Explore the interactive graph:
   - Drag nodes to rearrange
   - Click nodes to view details
   - Zoom in/out with mouse wheel

### Step 6: Generate a Report

1. Navigate to **Reports** > **New Report**
2. Configure report:
   - **Title**: "John Smith Investigation - Initial Findings"
   - **Description**: "Preliminary investigation results"
   - **Entities**: Select "John Smith"
   - **Include Relationships**: Yes
   - **Format**: PDF
3. Click **Generate Report**
4. Wait for generation to complete
5. Click **Download** to view your report

**Congratulations!** You've completed your first investigation.

---

## Tutorial 2: Automated Social Media Monitoring

**Objective**: Set up continuous monitoring of social media mentions.

**Duration**: 20 minutes

**Prerequisites**: Completed Tutorial 1

### Step 1: Define Monitoring Criteria

For this tutorial, we'll monitor mentions of a company called "TechCorp Inc."

1. Navigate to **Entities** > **New Entity**
2. Create an organization entity:
   - **Type**: Organization
   - **Name**: "TechCorp Inc."
   - **Tags**: "client", "monitoring"

### Step 2: Create a Scheduled Collection

1. Go to **Collections** > **New Collection**
2. Fill in details:
   - **Name**: "TechCorp Social Media Monitor"
   - **Description**: "Daily monitoring of TechCorp mentions"
   - **Collector Type**: Social Media
3. Configure collector:
   - **Platforms**: Twitter, LinkedIn
   - **Search Terms**:
     - "TechCorp Inc"
     - "#TechCorp"
     - "@TechCorpOfficial"
   - **Max Items**: 100
4. Enable scheduling:
   - Click **Enable Schedule**
   - **Frequency**: Daily
   - **Time**: 09:00 AM
   - **Start Date**: Today
5. Click **Create Collection**

### Step 3: Set Up Enrichment

1. Navigate to **Workflows** > **New Workflow**
2. Configure workflow:
   - **Name**: "Social Media Enrichment"
   - **Description**: "Enrich collected social media data"
   - **Trigger Type**: Event
   - **Event**: Collection Completed
   - **Filter**: Collection name contains "TechCorp Social Media"

3. Add workflow steps:

   **Step 1: Extract Entities**
   - Action: Enrichment > Entity Extraction
   - Parameters:
     - Entity Types: Person, Location, Organization

   **Step 2: Sentiment Analysis**
   - Action: Enrichment > Sentiment Analysis
   - Depends On: Step 1

   **Step 3: Calculate Risk**
   - Action: Risk Scoring > Calculate
   - Depends On: Step 2

4. Click **Create Workflow**

### Step 4: Configure Alerts

1. Go to **Settings** > **Notifications**
2. Add new notification rule:
   - **Name**: "High-Risk Mention Alert"
   - **Trigger**: Entity risk score > 70
   - **Filter**: Tag contains "monitoring"
   - **Notification Method**: Email
   - **Recipients**: your.email@example.com
3. Save notification rule

### Step 5: Test the Setup

1. Manually trigger the collection:
   - Go to **Collections**
   - Find "TechCorp Social Media Monitor"
   - Click **Run Now**
2. Monitor execution:
   - Watch collection progress
   - Check workflow execution in **Workflows** > **Executions**
3. Review results:
   - Check newly created entities
   - Review sentiment analysis results
   - Verify any alerts sent

### Step 6: Create a Monitoring Dashboard (Optional)

1. Go to **Dashboard** > **Customize**
2. Add widgets:
   - **Collection Status**: Show TechCorp collections
   - **Entity Timeline**: TechCorp-related entities
   - **Risk Trend**: Risk score changes over time
   - **Sentiment Chart**: Sentiment distribution
3. Save dashboard

**Success!** You now have automated social media monitoring set up.

---

## Tutorial 3: Domain Investigation

**Objective**: Investigate a suspicious domain name.

**Duration**: 25 minutes

**Prerequisites**: Basic familiarity with the platform

### Step 1: Create Domain Entity

1. Navigate to **Entities** > **New Entity**
2. Create domain entity:
   - **Type**: Domain
   - **Name**: "suspicious-site.com"
   - **Tags**: "investigation", "suspicious"

### Step 2: Run Domain Intelligence Collection

1. Go to **Collections** > **New Collection**
2. Configure:
   - **Name**: "Suspicious Domain Investigation"
   - **Collector Type**: Domain Intelligence
   - **Domain**: suspicious-site.com
   - **Information Types**: Select all:
     - WHOIS data
     - DNS records
     - SSL certificate info
     - Historical data
     - Subdomains
3. Click **Create Collection**
4. Wait for completion

### Step 3: Analyze WHOIS Data

1. Open the collection results
2. Review WHOIS information:
   - Registrant information
   - Registration date
   - Expiration date
   - Registrar
   - Name servers
3. Note any suspicious patterns:
   - Privacy protection enabled
   - Recent registration
   - Offshore registrar

### Step 4: Check DNS Records

1. In collection results, find DNS records
2. Analyze:
   - A records (IP addresses)
   - MX records (mail servers)
   - TXT records (SPF, DKIM)
   - NS records (name servers)
3. Create entities for discovered IP addresses:
   - Click **Create Entity from Result**
   - Select IP address entries
   - Confirm creation

### Step 5: Investigate Related Infrastructure

1. Go to **Collections** > **New Collection**
2. Create IP intelligence collection:
   - **Collector Type**: IP Intelligence
   - **IP Address**: (from DNS A record)
   - **Information Types**: All
3. Review IP information:
   - Geolocation
   - ISP/Hosting provider
   - Open ports (if available)
   - Reputation scores

### Step 6: Search for Related Domains

1. Check if domain is part of a larger network
2. Go to **Analysis** > **Pattern Detection**
3. Configure:
   - **Input Entities**: suspicious-site.com
   - **Pattern Types**: Network patterns
   - **Include**: Same registrant, same IP, same name servers
4. Run analysis
5. Review discovered related domains

### Step 7: Check Threat Intelligence

1. Run threat intelligence enrichment:
   - **Workflows** > **New Workflow**
   - **Name**: "Threat Intel Check"
   - **Steps**:
     - Check VirusTotal
     - Check URLhaus
     - Check PhishTank
2. Execute workflow
3. Review threat intelligence results

### Step 8: Calculate Risk Score

1. Navigate to **Risk Scoring** > **Calculate**
2. Select "suspicious-site.com" entity
3. Review risk factors:
   - Domain age
   - Reputation scores
   - Threat intelligence findings
   - Infrastructure patterns
4. Note the calculated risk score

### Step 9: Create Investigation Report

1. Go to **Reports** > **New Report**
2. Configure:
   - **Title**: "Domain Investigation: suspicious-site.com"
   - **Entities**: Include domain and related IP addresses
   - **Sections**:
     - WHOIS data
     - DNS records
     - Threat intelligence
     - Infrastructure analysis
     - Risk assessment
     - Recommendations
3. Generate and download report

**Complete!** You've conducted a thorough domain investigation.

---

## Tutorial 4: Link Analysis and Network Mapping

**Objective**: Uncover hidden connections between entities.

**Duration**: 30 minutes

**Prerequisites**: Multiple entities in the system

### Step 1: Prepare Sample Data

For this tutorial, create the following entities if not already present:

1. **Person**: Alice Johnson (CEO)
2. **Organization**: Acme Corporation
3. **Person**: Bob Smith (CTO)
4. **Organization**: Beta Industries
5. **Person**: Charlie Davis (Investor)

### Step 2: Create Relationships

Establish the following relationships:

1. Alice Johnson **WORKS_FOR** Acme Corporation (CEO)
2. Bob Smith **WORKS_FOR** Acme Corporation (CTO)
3. Alice Johnson **WORKS_FOR** Beta Industries (Board Member)
4. Charlie Davis **INVESTS_IN** Acme Corporation
5. Charlie Davis **INVESTS_IN** Beta Industries

**To create each relationship**:
- Go to **Relationships** > **New Relationship**
- Select source and target entities
- Choose relationship type
- Add properties (role, start date, etc.)

### Step 3: Basic Network Visualization

1. Navigate to **Entities**
2. Click on "Alice Johnson"
3. Click **Analyze Relationships**
4. Set depth to 2
5. Observe the network:
   - Alice at the center
   - Direct connections (depth 1)
   - Secondary connections (depth 2)

### Step 4: Find Shortest Path

Discover connections between Charlie Davis and Bob Smith:

1. Go to **Analysis** > **Link Analysis**
2. Select **Shortest Path**
3. Configure:
   - **Start Entity**: Charlie Davis
   - **End Entity**: Bob Smith
4. Click **Find Path**
5. Review results:
   - Path: Charlie → Acme Corp → Bob
   - Alternative paths through Beta Industries

### Step 5: Community Detection

Identify groups within the network:

1. Go to **Analysis** > **Link Analysis**
2. Select **Community Detection**
3. Choose algorithm: Louvain
4. Select entities to analyze (select all)
5. Run analysis
6. Observe communities:
   - Business community (Acme-related entities)
   - Investment community (entities connected through Charlie)

### Step 6: Centrality Analysis

Find most influential entities:

1. Go to **Analysis** > **Link Analysis**
2. Select **Centrality Analysis**
3. Choose metrics:
   - Degree Centrality (number of connections)
   - Betweenness Centrality (bridge positions)
   - Closeness Centrality (proximity to others)
4. Run analysis
5. Review results ranked by influence

### Step 7: Temporal Analysis

Analyze relationship evolution:

1. Ensure relationships have start dates
2. Go to **Analysis** > **Temporal Analysis**
3. Select date range
4. Generate timeline:
   - Visualize when relationships formed
   - Identify patterns and clusters
   - Spot anomalies

### Step 8: Export Network Data

1. From the graph visualization
2. Click **Export**
3. Choose format:
   - **GEXF**: For Gephi software
   - **GraphML**: For Cytoscape
   - **JSON**: For custom processing
   - **Image**: PNG or SVG
4. Download and use in external tools

### Step 9: Create Interactive Report

1. Generate a report with interactive elements:
   - Go to **Reports** > **New Report**
   - Enable **Interactive Mode**
   - Include:
     - Network graph
     - Community breakdown
     - Centrality rankings
     - Timeline
2. Share report with stakeholders

**Excellent!** You've mastered link analysis techniques.

---

## Tutorial 5: Creating Custom Workflows

**Objective**: Automate complex investigation processes.

**Duration**: 35 minutes

**Prerequisites**: Understanding of collections and analysis

### Scenario

Automate the investigation of new high-risk entities by:
1. Collecting social media data
2. Enriching with additional context
3. Analyzing relationships
4. Calculating risk
5. Generating and sending a report

### Step 1: Create Workflow Structure

1. Navigate to **Workflows** > **New Workflow**
2. Basic configuration:
   - **Name**: "Automated Entity Investigation"
   - **Description**: "Complete investigation workflow for new entities"
   - **Category**: Investigation

### Step 2: Configure Trigger

1. Set trigger type: **Event-based**
2. Configure:
   - **Event**: Entity Created
   - **Conditions**:
     - Entity type: Person OR Organization
     - Tag contains: "investigate"
     - Risk score > 50 (if already set)

### Step 3: Add Workflow Steps

**Step 1: Social Media Collection**
```
Action: Collection > Run Collector
Parameters:
  - Collector Type: Social Media
  - Search Terms: ${entity.name}
  - Platforms: All
  - Max Items: 100
```

**Step 2: Domain Collection (if applicable)**
```
Action: Collection > Run Collector
Condition: ${entity.type} == "Organization"
Parameters:
  - Collector Type: Domain Intelligence
  - Domain: ${entity.properties.domain}
  - Information Types: All
```

**Step 3: Data Enrichment**
```
Action: Enrichment > Run Pipeline
Depends On: Step 1, Step 2
Parameters:
  - Entity ID: ${entity.id}
  - Enrichment Types:
    - Entity Extraction
    - Geolocation
    - Sentiment Analysis
    - Language Detection
```

**Step 4: Relationship Discovery**
```
Action: Analysis > Link Analysis
Depends On: Step 3
Parameters:
  - Entity ID: ${entity.id}
  - Max Depth: 2
  - Auto-create relationships: true
```

**Step 5: Pattern Detection**
```
Action: Analysis > Pattern Detection
Depends On: Step 4
Parameters:
  - Entity ID: ${entity.id}
  - Pattern Types: All
```

**Step 6: Risk Calculation**
```
Action: Risk Scoring > Calculate
Depends On: Step 5
Parameters:
  - Entity ID: ${entity.id}
  - Force Recalculate: true
```

**Step 7: Conditional Alert**
```
Action: Notification > Send
Condition: ${steps.step6.risk_score} > 75
Parameters:
  - Type: Email
  - Template: high_risk_entity_alert
  - Recipients: security@example.com
  - Include Summary: true
```

**Step 8: Generate Report**
```
Action: Report > Generate
Depends On: Step 6
Parameters:
  - Title: "Investigation: ${entity.name}"
  - Entity ID: ${entity.id}
  - Include Relationships: true
  - Include Risk Analysis: true
  - Format: PDF
```

**Step 9: Send Report**
```
Action: Notification > Send
Depends On: Step 8
Parameters:
  - Type: Email
  - Recipients: investigator@example.com
  - Subject: "Investigation Complete: ${entity.name}"
  - Attachment: ${steps.step8.report_file}
```

### Step 4: Add Error Handling

For each step:
1. Click step settings
2. Enable **Error Handling**
3. Configure:
   - **On Error**: Continue (or Stop)
   - **Retry Attempts**: 3
   - **Retry Delay**: 30 seconds
   - **Notification**: Email admin on failure

### Step 5: Configure Workflow Notifications

1. In workflow settings, add notifications:
   - **On Start**: Log to audit
   - **On Success**: Email confirmation
   - **On Failure**: Email + Slack alert

### Step 6: Test the Workflow

1. Save workflow
2. Create test entity:
   - Name: "Test Company Inc."
   - Type: Organization
   - Tag: "investigate"
3. Workflow should trigger automatically
4. Monitor execution:
   - Go to **Workflows** > **Executions**
   - Click on the running execution
   - Watch step-by-step progress
   - Review logs

### Step 7: Review Results

1. Check created reports
2. Review risk scores
3. Examine discovered relationships
4. Verify notifications were sent

### Step 8: Optimize Workflow

Based on test results:
1. Adjust step parameters
2. Add/remove steps
3. Fine-tune conditions
4. Update error handling
5. Save optimized version

**Awesome!** You've created a powerful automation workflow.

---

## Tutorial 6: Risk Assessment and Monitoring

**Objective**: Implement comprehensive risk monitoring.

**Duration**: 25 minutes

**Prerequisites**: Understanding of entities and risk scores

### Step 1: Understand Risk Factors

Review the risk scoring components:

1. Navigate to **Settings** > **Risk Scoring**
2. Review default weights:
   - Data Source Credibility: 20%
   - Entity Behavior: 30%
   - Relationship Risk: 30%
   - Threat Intelligence: 20%
3. Adjust weights if needed for your use case

### Step 2: Set Up Risk Monitoring

1. Go to **Workflows** > **New Workflow**
2. Create daily risk assessment:
   - **Name**: "Daily Risk Recalculation"
   - **Trigger**: Scheduled
   - **Schedule**: Daily at 02:00 AM
   - **Step**: Recalculate all entity risk scores

### Step 3: Create Risk Alert Rules

1. Navigate to **Settings** > **Notifications**
2. Create alert rules:

**Critical Risk Alert**:
- Trigger: Risk score > 75
- Immediate notification
- Recipients: Security team
- Channels: Email + Slack

**Risk Increase Alert**:
- Trigger: Risk score increased by 20+ points
- Notification: Within 1 hour
- Recipients: Analysts
- Channels: Email

**New High-Risk Entity**:
- Trigger: New entity with risk score > 60
- Notification: Immediate
- Action: Auto-assign to investigator

### Step 4: Build Risk Dashboard

1. Go to **Dashboard** > **Create Dashboard**
2. Name: "Risk Monitoring"
3. Add widgets:
   - **Risk Distribution**: Pie chart of risk levels
   - **High-Risk Entities**: List (score > 70)
   - **Risk Trend**: Line graph over time
   - **Risk Changes**: Recent score changes
   - **Top Risk Factors**: Most common risk factors

### Step 5: Create Risk Investigation Workflow

1. **Workflows** > **New Workflow**
2. **Name**: "High-Risk Entity Investigation"
3. **Trigger**: Entity risk score > 75
4. **Steps**:
   - Collect additional data
   - Deep relationship analysis
   - Check threat intelligence feeds
   - Generate detailed report
   - Assign to investigator
   - Set review deadline

### Step 6: Monitor Risk Trends

1. Generate risk trend report:
   - **Reports** > **New Report**
   - **Type**: Risk Analysis
   - **Period**: Last 30 days
   - **Include**:
     - Risk score changes
     - New high-risk entities
     - Risk factor analysis
     - Recommendations

### Step 7: Implement Risk Review Process

1. Create review workflow:
   - **Name**: "Weekly Risk Review"
   - **Schedule**: Every Monday 9 AM
   - **Steps**:
     - Generate list of high-risk entities
     - Check for score changes
     - Send to review team
     - Track review completion

### Step 8: Test and Validate

1. Manually adjust entity risk:
   - Select test entity
   - Change risk score to 80
   - Verify alerts triggered
   - Check workflow execution
   - Review notifications sent
2. Reset and document

**Perfect!** You have a comprehensive risk monitoring system.

---

## Tutorial 7: Generating Investigation Reports

**Objective**: Create professional investigation reports.

**Duration**: 20 minutes

**Prerequisites**: Completed investigation with entities and relationships

### Step 1: Choose Report Type

1. Navigate to **Reports** > **New Report**
2. Select template:
   - **Comprehensive Investigation**: Full detailed report
   - **Executive Summary**: High-level overview
   - **Technical Analysis**: Detailed technical findings
   - **Risk Assessment**: Focus on risk factors
   - **Custom**: Build from scratch

For this tutorial, select **Comprehensive Investigation**.

### Step 2: Configure Report Basics

1. Fill in report details:
   - **Title**: "Investigation Report: Acme Corporation"
   - **Subtitle**: "Comprehensive Analysis"
   - **Report Date**: Auto (current date)
   - **Classification**: Confidential
   - **Author**: Your name
   - **Reference Number**: INV-2024-001

### Step 3: Select Entities

1. Click **Add Entities**
2. Select primary entities:
   - Acme Corporation (Organization)
   - Related persons
   - Associated domains
3. Options:
   - **Include Related Entities**: Yes (depth: 1)
   - **Include Relationships**: Yes
   - **Minimum Risk Score**: 0 (include all)

### Step 4: Configure Report Sections

Select sections to include:

1. ✅ **Executive Summary**
   - Auto-generated overview
   - Key findings
   - Risk summary

2. ✅ **Methodology**
   - Data sources used
   - Collection methods
   - Analysis techniques

3. ✅ **Entity Profiles**
   - Detailed entity information
   - Properties and attributes
   - Timeline of activity

4. ✅ **Relationship Analysis**
   - Network diagram
   - Key connections
   - Community structure

5. ✅ **Risk Assessment**
   - Risk scores
   - Contributing factors
   - Trend analysis

6. ✅ **Timeline**
   - Chronological event list
   - Visual timeline
   - Key dates

7. ✅ **Data Sources**
   - Source list
   - Credibility ratings
   - Collection metadata

8. ✅ **Findings and Analysis**
   - Key discoveries
   - Patterns identified
   - Anomalies

9. ✅ **Recommendations**
   - Suggested actions
   - Further investigation areas
   - Monitoring suggestions

10. ✅ **Appendices**
    - Raw data tables
    - Technical details
    - References

### Step 5: Customize Sections

For each section, configure:

1. **Executive Summary**:
   - Maximum length: 2 pages
   - Include risk chart: Yes
   - Highlight top findings: 5

2. **Network Diagram**:
   - Layout: Force-directed
   - Color by: Risk score
   - Size by: Centrality
   - Max depth: 2

3. **Timeline**:
   - Format: Visual + Table
   - Date range: All
   - Event types: All

### Step 6: Format and Style

1. Select output format:
   - **PDF**: Professional document (recommended)
   - **DOCX**: Editable Microsoft Word
   - **JSON**: Structured data export
   - **HTML**: Web-viewable report

2. Choose style template:
   - **Professional**: Clean, formal
   - **Executive**: Minimalist, high-level
   - **Technical**: Detailed, data-focused
   - **Custom**: Upload your template

3. Configure branding:
   - Organization logo
   - Color scheme
   - Header/footer content

### Step 7: Review and Generate

1. Click **Preview Report**
2. Review each section
3. Make adjustments as needed
4. Click **Generate Final Report**
5. Wait for processing (may take 1-5 minutes)

### Step 8: Download and Distribute

1. Once complete, click **Download**
2. Open and review the PDF
3. Optional: Share report
   - Click **Share**
   - Enter recipient emails
   - Add message
   - Set expiration date
   - Send

### Step 9: Schedule Recurring Reports

1. In report settings, enable **Recurring Report**
2. Configure:
   - **Frequency**: Weekly
   - **Day**: Monday
   - **Time**: 08:00 AM
   - **Auto-send to**: Distribution list
   - **Update entities**: Yes (include new data)

### Step 10: Create Report Template

Save your configuration for reuse:
1. Click **Save as Template**
2. Name: "Standard Investigation Report"
3. Description: "Comprehensive investigation template"
4. Make available to: Team/Organization

**Fantastic!** You can now create professional investigation reports.

---

## Tutorial 8: Using the API

**Objective**: Interact with the platform programmatically.

**Duration**: 30 minutes

**Prerequisites**: Basic programming knowledge (Python examples)

### Step 1: Generate API Key

1. Log in to the platform
2. Go to **User Profile** > **Settings** > **API Keys**
3. Click **Generate New API Key**
4. Configure:
   - **Name**: "Tutorial API Key"
   - **Scopes**: Select all for tutorial
   - **Rate Limit**: 1000 requests/minute
   - **Expiration**: 30 days
5. Click **Generate**
6. **Important**: Copy and save the API key (shown only once)

### Step 2: Set Up Development Environment

Create a Python script:

```python
import requests
import json

# Configuration
API_BASE_URL = "https://api.osint-platform.example/v1"
API_KEY = "your-api-key-here"

# Headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

### Step 3: Authenticate

Test API authentication:

```python
def test_authentication():
    response = requests.get(
        f"{API_BASE_URL}/auth/me",
        headers=headers
    )

    if response.status_code == 200:
        user = response.json()
        print(f"Authenticated as: {user['username']}")
        return True
    else:
        print(f"Authentication failed: {response.status_code}")
        return False

test_authentication()
```

### Step 4: Create an Entity

```python
def create_entity(name, entity_type, properties=None):
    data = {
        "name": name,
        "type": entity_type,
        "properties": properties or {},
        "tags": ["api-created"]
    }

    response = requests.post(
        f"{API_BASE_URL}/entities",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        entity = response.json()
        print(f"Created entity: {entity['id']}")
        return entity
    else:
        print(f"Failed to create entity: {response.text}")
        return None

# Example usage
entity = create_entity(
    name="API Test Company",
    entity_type="organization",
    properties={
        "domain": "api-test.com",
        "industry": "Technology"
    }
)
```

### Step 5: Run a Collection

```python
def create_collection(name, collector_type, config):
    data = {
        "name": name,
        "collector_type": collector_type,
        "config": config
    }

    response = requests.post(
        f"{API_BASE_URL}/collections",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        collection = response.json()
        print(f"Created collection: {collection['id']}")
        return collection
    else:
        print(f"Failed to create collection: {response.text}")
        return None

# Example usage
collection = create_collection(
    name="API Social Media Collection",
    collector_type="social_media",
    config={
        "platform": "twitter",
        "search_terms": ["API Test Company"],
        "max_items": 50
    }
)
```

### Step 6: Monitor Collection Progress

```python
import time

def monitor_collection(collection_id):
    while True:
        response = requests.get(
            f"{API_BASE_URL}/collections/{collection_id}",
            headers=headers
        )

        if response.status_code == 200:
            collection = response.json()
            status = collection['status']
            progress = collection['progress']

            print(f"Status: {status}, Progress: {progress}%")

            if status in ['completed', 'failed']:
                return collection

            time.sleep(5)  # Check every 5 seconds
        else:
            print(f"Error checking collection: {response.text}")
            return None

# Monitor the collection we created
result = monitor_collection(collection['id'])
```

### Step 7: Retrieve Collection Results

```python
def get_collection_results(collection_id, page=1, limit=20):
    response = requests.get(
        f"{API_BASE_URL}/collections/{collection_id}/results",
        headers=headers,
        params={
            "page": page,
            "limit": limit
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get results: {response.text}")
        return None

# Get results
results = get_collection_results(collection['id'])
print(f"Collected {results['total']} items")

for item in results['results']:
    print(f"- {item['item_type']}: {item['raw_data'][:100]}...")
```

### Step 8: Search Entities

```python
def search_entities(query, entity_type=None, risk_score_min=None):
    params = {"q": query}
    if entity_type:
        params["type"] = entity_type
    if risk_score_min:
        params["risk_score_min"] = risk_score_min

    response = requests.get(
        f"{API_BASE_URL}/search",
        headers=headers,
        params=params
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Search failed: {response.text}")
        return None

# Example search
results = search_entities(
    query="Technology",
    entity_type="organization",
    risk_score_min=50
)

print(f"Found {results['total']} entities")
```

### Step 9: Perform Link Analysis

```python
def link_analysis(entity_id, max_depth=2):
    data = {
        "entity_ids": [entity_id],
        "max_depth": max_depth,
        "algorithm": "shortest_path"
    }

    response = requests.post(
        f"{API_BASE_URL}/analysis/link-analysis",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Analysis failed: {response.text}")
        return None

# Run analysis
if entity:
    analysis = link_analysis(entity['id'])
    print(f"Found {len(analysis['graph']['nodes'])} connected entities")
```

### Step 10: Generate a Report

```python
def generate_report(title, entity_ids, format="pdf"):
    data = {
        "title": title,
        "entity_ids": entity_ids,
        "include_relationships": True,
        "include_risk_analysis": True,
        "format": format
    }

    response = requests.post(
        f"{API_BASE_URL}/reports",
        headers=headers,
        json=data
    )

    if response.status_code == 202:
        report = response.json()
        print(f"Report generation started: {report['id']}")
        return report
    else:
        print(f"Failed to generate report: {response.text}")
        return None

def download_report(report_id, filename="report.pdf"):
    # Wait for report to complete
    while True:
        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}",
            headers=headers
        )

        if response.status_code == 200:
            report = response.json()
            if report['status'] == 'completed':
                break
            elif report['status'] == 'failed':
                print("Report generation failed")
                return False

        time.sleep(5)

    # Download report
    response = requests.get(
        f"{API_BASE_URL}/reports/{report_id}/download",
        headers=headers,
        params={"format": "pdf"}
    )

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Report saved to {filename}")
        return True
    else:
        print(f"Failed to download report: {response.text}")
        return False

# Generate and download report
if entity:
    report = generate_report(
        title="API Generated Report",
        entity_ids=[entity['id']]
    )

    if report:
        download_report(report['id'], "api_report.pdf")
```

### Complete Example Script

```python
#!/usr/bin/env python3
"""
OSINT Platform API Tutorial
Complete workflow example
"""

import requests
import time
import json

# Configuration
API_BASE_URL = "https://api.osint-platform.example/v1"
API_KEY = "your-api-key-here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def main():
    print("=== OSINT Platform API Tutorial ===\n")

    # 1. Test authentication
    print("1. Testing authentication...")
    test_authentication()

    # 2. Create entity
    print("\n2. Creating entity...")
    entity = create_entity(
        name="Tutorial Company Inc.",
        entity_type="organization",
        properties={"domain": "tutorial-company.com"}
    )

    if not entity:
        return

    # 3. Run collection
    print("\n3. Starting data collection...")
    collection = create_collection(
        name="Tutorial Collection",
        collector_type="domain_intel",
        config={"domain": "tutorial-company.com"}
    )

    if not collection:
        return

    # 4. Monitor collection
    print("\n4. Monitoring collection progress...")
    result = monitor_collection(collection['id'])

    # 5. Get results
    print("\n5. Retrieving results...")
    results = get_collection_results(collection['id'])
    print(f"   Collected {results['total']} items")

    # 6. Calculate risk
    print("\n6. Calculating risk score...")
    risk = calculate_risk(entity['id'])
    print(f"   Risk Score: {risk['score']}/100")

    # 7. Generate report
    print("\n7. Generating report...")
    report = generate_report(
        title=f"Investigation: {entity['name']}",
        entity_ids=[entity['id']]
    )

    if report:
        download_report(report['id'], "tutorial_report.pdf")

    print("\n=== Tutorial Complete ===")

if __name__ == "__main__":
    main()
```

**Excellent!** You can now automate OSINT investigations using the API.

---

## Next Steps

Now that you've completed these tutorials, you can:

1. Explore advanced features in the [User Guide](USER_GUIDE.md)
2. Review [Best Practices](BEST_PRACTICES.md)
3. Check the [FAQ](FAQ.md) for common questions
4. Consult the [API Documentation](../technical/API.yaml) for complete API reference

Happy investigating!
