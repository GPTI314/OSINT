# OSINT Platform - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Data Collection](#data-collection)
5. [Entity Management](#entity-management)
6. [Relationship Analysis](#relationship-analysis)
7. [Risk Scoring](#risk-scoring)
8. [Workflows](#workflows)
9. [Reports](#reports)
10. [Search and Filters](#search-and-filters)
11. [Settings and Preferences](#settings-and-preferences)

## Introduction

Welcome to the OSINT Platform, a comprehensive tool for collecting, analyzing, and visualizing open-source intelligence data. This guide will help you navigate the platform and make the most of its features.

### What is OSINT?

Open-Source Intelligence (OSINT) refers to intelligence collected from publicly available sources. The OSINT Platform helps you:

- Collect data from multiple sources automatically
- Identify and track entities (people, organizations, locations, etc.)
- Discover relationships between entities
- Assess risk levels
- Generate comprehensive investigation reports

### Key Features

- **Modular Collectors**: Gather data from social media, public databases, domain intelligence, and more
- **Enrichment Pipeline**: Automatically enhance collected data with additional context
- **Link Analysis**: Visualize complex relationships between entities
- **Risk Scoring**: Automated risk assessment based on multiple factors
- **Workflow Automation**: Automate repetitive investigation tasks
- **Report Generation**: Create professional investigation reports

## Getting Started

### Creating an Account

1. Navigate to the platform URL provided by your administrator
2. Click "Sign Up" or "Register"
3. Enter your information:
   - Email address
   - Username
   - Password (minimum 8 characters, must include uppercase, lowercase, numbers, and special characters)
   - Full name
4. Verify your email address by clicking the link sent to your inbox
5. Log in with your credentials

### First Login

Upon your first login, you'll see:

- **Dashboard**: Overview of recent activity and statistics
- **Quick Start Guide**: Interactive tutorial (optional)
- **Sample Data**: Example entities and relationships to explore

### Dashboard Overview

The dashboard provides:

- **Recent Collections**: Your latest data collection jobs
- **Active Workflows**: Currently running automated workflows
- **High-Risk Entities**: Entities with elevated risk scores
- **System Statistics**: Overall platform usage and data metrics
- **Quick Actions**: Shortcuts to common tasks

## User Interface Overview

### Navigation Menu

The main navigation menu includes:

- **Dashboard**: Home page with overview
- **Collections**: Manage data collection jobs
- **Entities**: View and manage all entities
- **Relationships**: Explore entity connections
- **Analysis**: Run advanced analyses
- **Workflows**: Automate investigations
- **Reports**: Generate and view reports
- **Search**: Global search functionality
- **Settings**: User preferences and configuration

### Top Bar

- **User Profile**: Access account settings and logout
- **Notifications**: View system alerts and updates
- **Help**: Access documentation and support
- **Search**: Quick search across all data

## Data Collection

### Creating a Collection

1. Navigate to **Collections** > **New Collection**
2. Fill in collection details:
   - **Name**: Descriptive name for the collection
   - **Description**: Purpose and scope of the collection
   - **Collector Type**: Choose from available collectors
3. Configure collector-specific settings
4. Click **Create Collection**

### Collector Types

#### Social Media

Collect data from social media platforms.

**Configuration**:
- Platform selection (Twitter, LinkedIn, Facebook)
- Search terms or hashtags
- User profiles to monitor
- Date range
- Maximum items to collect

**Use Cases**:
- Monitor brand mentions
- Track public figures
- Identify sentiment and trends

#### Domain Intelligence

Gather information about domains and IP addresses.

**Configuration**:
- Domain name or IP address
- Information types (WHOIS, DNS, SSL certificates)
- Historical data inclusion

**Use Cases**:
- Investigate suspicious websites
- Track domain ownership changes
- Identify related infrastructure

#### Public Databases

Search public records and databases.

**Configuration**:
- Database selection
- Search criteria
- Data fields to retrieve

**Use Cases**:
- Background checks
- Company research
- Historical records lookup

#### News and Media

Collect articles and media mentions.

**Configuration**:
- Keywords or topics
- Date range
- Source selection
- Language preferences

**Use Cases**:
- Track news coverage
- Monitor reputation
- Identify emerging trends

### Monitoring Collections

View collection progress:

1. Go to **Collections**
2. Click on a collection to view details
3. Monitor:
   - **Status**: Pending, Running, Completed, or Failed
   - **Progress**: Percentage complete
   - **Items Collected**: Number of data points gathered
   - **Estimated Time**: Time remaining
   - **Logs**: Detailed execution logs

### Scheduled Collections

Automate recurring collections:

1. Create or edit a collection
2. Enable **Schedule**
3. Configure schedule:
   - Frequency (hourly, daily, weekly, monthly)
   - Start date and time
   - End date (optional)
4. Save collection

## Entity Management

### Understanding Entities

Entities represent identifiable objects:

- **Person**: Individuals
- **Organization**: Companies, groups, agencies
- **Location**: Physical addresses, cities, countries
- **Domain**: Websites and domain names
- **IP Address**: Network addresses
- **Email**: Email addresses
- **Phone**: Phone numbers
- **Username**: Social media handles
- **Cryptocurrency Address**: Blockchain addresses

### Viewing Entities

1. Navigate to **Entities**
2. Browse the entity list
3. Use filters to narrow results:
   - Entity type
   - Risk score
   - Tags
   - Date range

### Entity Details

Click on an entity to view:

- **Overview**: Basic information and properties
- **Risk Score**: Current risk assessment
- **Relationships**: Connected entities
- **Timeline**: Activity history
- **Sources**: Data collection sources
- **Tags**: Applied labels
- **Notes**: User-added comments

### Creating Entities Manually

1. Navigate to **Entities** > **New Entity**
2. Select entity type
3. Enter information:
   - Name (required)
   - Properties (type-specific fields)
   - Tags
   - Notes
4. Click **Create Entity**

### Editing Entities

1. Open entity details
2. Click **Edit**
3. Modify information
4. Click **Save**

### Merging Duplicate Entities

When duplicates are detected:

1. Select entities to merge
2. Click **Merge Entities**
3. Review proposed merge
4. Choose primary entity
5. Confirm merge

### Tagging Entities

Organize entities with tags:

1. Open entity details
2. Click **Add Tag**
3. Enter tag name or select existing tag
4. Press Enter or click **Add**

Common tag examples:
- Investigation names
- Priority levels (high, medium, low)
- Categories (suspect, witness, company)
- Status (active, archived, verified)

## Relationship Analysis

### Viewing Relationships

Relationships connect entities and show how they're related.

**Access relationships**:
1. Navigate to **Relationships**
2. Or click **Relationships** tab within an entity

### Relationship Types

- **WORKS_FOR**: Employment relationship
- **OWNS**: Ownership
- **LOCATED_AT**: Physical location
- **COMMUNICATES_WITH**: Communication
- **ASSOCIATED_WITH**: General association
- **CONTROLS**: Control or influence
- **MEMBER_OF**: Membership
- **TRANSACTS_WITH**: Financial transactions

### Creating Relationships

1. Navigate to **Relationships** > **New Relationship**
2. Select source entity
3. Select target entity
4. Choose relationship type
5. Add properties (optional):
   - Confidence level
   - Start date
   - End date
   - Notes
6. Click **Create Relationship**

### Link Analysis

Visualize entity networks:

1. Open entity details
2. Click **Analyze Relationships**
3. Configure analysis:
   - Maximum depth (1-5 levels)
   - Relationship types to include
   - Minimum confidence level
4. Click **Run Analysis**

The graph visualization shows:
- **Nodes**: Entities (size indicates centrality)
- **Edges**: Relationships (thickness indicates strength)
- **Colors**: Entity types or risk levels

**Graph interactions**:
- Click and drag to pan
- Scroll to zoom
- Click nodes for details
- Hover over edges for relationship info

### Shortest Path Analysis

Find connections between two entities:

1. Go to **Analysis** > **Link Analysis**
2. Select **Shortest Path**
3. Choose start entity
4. Choose end entity
5. Click **Find Path**

Results show:
- Path length
- Intermediate entities
- Relationship types
- Alternative paths (if available)

### Community Detection

Identify clusters of related entities:

1. Go to **Analysis** > **Link Analysis**
2. Select **Community Detection**
3. Choose algorithm:
   - Louvain (recommended)
   - Label Propagation
   - Modularity Optimization
4. Click **Run Analysis**

Results highlight distinct communities with shared connections.

## Risk Scoring

### Understanding Risk Scores

Risk scores range from 0-100:

- **0-25**: Low risk (green)
- **26-50**: Medium risk (yellow)
- **51-75**: High risk (orange)
- **76-100**: Critical risk (red)

### Risk Factors

Scores are calculated based on:

1. **Data Source Credibility** (20%): Reliability of information sources
2. **Entity Behavior** (30%): Patterns and activities
3. **Relationship Risk** (30%): Risk propagation from connected entities
4. **Threat Intelligence** (20%): External threat feeds

### Viewing Risk Scores

Risk scores are displayed:
- In entity list
- On entity detail page
- In relationship graph (node colors)
- In dashboard statistics

### Manual Risk Adjustment

Override automated scores when needed:

1. Open entity details
2. Click **Adjust Risk Score**
3. Enter new score
4. Provide justification
5. Click **Save**

### Risk Score History

View score changes over time:

1. Open entity details
2. Click **Risk History**
3. View timeline chart
4. Click data points for details

### Risk Alerts

Configure notifications for high-risk entities:

1. Go to **Settings** > **Notifications**
2. Enable **Risk Alerts**
3. Set threshold (e.g., score > 75)
4. Choose notification method (email, webhook)
5. Save settings

## Workflows

### What are Workflows?

Workflows automate investigation tasks by combining multiple actions in a sequence.

### Creating a Workflow

1. Navigate to **Workflows** > **New Workflow**
2. Enter workflow details:
   - Name
   - Description
3. Configure trigger:
   - **Manual**: Start manually
   - **Scheduled**: Run on schedule
   - **Event**: Triggered by system events
4. Add workflow steps
5. Configure notifications
6. Click **Create Workflow**

### Workflow Steps

Available actions:

- **Run Collection**: Execute a data collection
- **Enrich Data**: Apply enrichment pipeline
- **Analyze Links**: Perform link analysis
- **Calculate Risk**: Update risk scores
- **Send Notification**: Alert users
- **Generate Report**: Create investigation report
- **Execute Script**: Run custom code (admin only)

### Step Configuration

For each step:

1. Choose action type
2. Set parameters
3. Configure conditions (optional)
4. Set dependencies (which steps must complete first)
5. Add error handling

### Example Workflow: New Entity Investigation

```
Trigger: Entity Created (risk score > 50)

Steps:
1. Collect Social Media Data
2. Enrich with Geolocation
3. Analyze Relationships (depth: 2)
4. Calculate Risk Score
5. If risk > 75: Send Alert Email
6. Generate Summary Report
```

### Executing Workflows

**Manual execution**:
1. Navigate to **Workflows**
2. Click on workflow
3. Click **Execute**
4. Provide parameters (if required)
5. Click **Start**

**Monitor execution**:
1. Go to **Workflows** > **Executions**
2. View status and progress
3. Click execution for detailed logs

### Workflow Templates

Use pre-built templates:

1. **Comprehensive Entity Investigation**: Full analysis of new entity
2. **Daily Risk Assessment**: Recalculate all risk scores
3. **Relationship Discovery**: Find new connections
4. **Threat Intelligence Update**: Import latest threat data

## Reports

### Generating Reports

Create investigation reports:

1. Navigate to **Reports** > **New Report**
2. Configure report:
   - **Title**: Report name
   - **Description**: Report purpose
   - **Entities**: Select entities to include
   - **Include Relationships**: Yes/No
   - **Include Risk Analysis**: Yes/No
   - **Format**: PDF, DOCX, or JSON
3. Click **Generate Report**

### Report Sections

Standard reports include:

1. **Executive Summary**: High-level overview
2. **Entity Profiles**: Detailed entity information
3. **Relationship Map**: Visual network diagram
4. **Risk Assessment**: Risk scores and factors
5. **Timeline**: Chronological activity
6. **Data Sources**: Source credibility and references
7. **Recommendations**: Suggested actions

### Downloading Reports

1. Go to **Reports**
2. Find your report (status: Completed)
3. Click **Download**
4. Choose format (if multiple available)

### Scheduling Automated Reports

1. Create report
2. Enable **Schedule**
3. Configure:
   - Frequency
   - Recipients
   - Delivery method (email, webhook)
4. Save report

## Search and Filters

### Global Search

Use the search bar to find:

1. Enter search query
2. Optionally filter by type:
   - Entities
   - Relationships
   - Collections
   - Reports
3. Press Enter

### Advanced Search

Access advanced search:

1. Click search bar
2. Click **Advanced Search**
3. Configure filters:
   - Entity type
   - Risk score range
   - Date range
   - Tags
   - Properties
4. Click **Search**

### Saved Searches

Save frequently used searches:

1. Configure search filters
2. Click **Save Search**
3. Enter name
4. Click **Save**

Access saved searches from the search dropdown.

### Boolean Operators

Supported in search queries:

- `AND`: Both terms must match
- `OR`: Either term matches
- `NOT`: Exclude term
- `"exact phrase"`: Exact match
- `*`: Wildcard

**Examples**:
- `john AND smith`: Entities with both "john" and "smith"
- `"john smith"`: Exact name match
- `doe NOT jane`: "doe" but not "jane"
- `tech*`: Matches "technology", "technical", etc.

## Settings and Preferences

### Account Settings

Access via **User Profile** > **Settings**

**Available settings**:

- **Profile Information**: Update name, email
- **Password**: Change password
- **Two-Factor Authentication**: Enable MFA
- **API Keys**: Generate API keys for programmatic access
- **Session Timeout**: Configure auto-logout

### Notification Preferences

Configure alerts:

1. Go to **Settings** > **Notifications**
2. Enable/disable notification types:
   - Collection completed
   - High-risk entity detected
   - Workflow execution results
   - System updates
3. Choose delivery method:
   - Email
   - In-app notifications
   - Webhook
4. Save preferences

### Display Preferences

Customize interface:

- **Theme**: Light or dark mode
- **Language**: Select preferred language
- **Timezone**: Set local timezone
- **Date Format**: Choose date format
- **Default Page Size**: Items per page in lists

### Privacy Settings

Control data visibility:

- **Profile Visibility**: Public or private
- **Activity Visibility**: Share activity with team
- **Data Retention**: Configure data retention period

### Integrations

Connect external services:

1. Go to **Settings** > **Integrations**
2. Select service to integrate
3. Provide credentials
4. Configure integration settings
5. Test connection
6. Save integration

### Team Management (Admin)

For administrators:

1. Go to **Settings** > **Team**
2. Manage users:
   - Invite new users
   - Assign roles
   - Deactivate accounts
3. Configure permissions
4. View audit logs

## Tips and Best Practices

### Effective Data Collection

- Start with focused collections targeting specific entities
- Use scheduled collections for ongoing monitoring
- Review collection results before running analysis
- Tag entities during collection for better organization

### Relationship Analysis

- Begin with depth 1-2 for initial exploration
- Increase depth gradually for complex investigations
- Use filters to focus on relevant relationship types
- Export graphs for presentations and reports

### Risk Management

- Regularly review high-risk entities
- Investigate sudden risk score changes
- Document manual risk adjustments
- Set up alerts for critical thresholds

### Workflow Efficiency

- Create workflows for repetitive tasks
- Test workflows with sample data first
- Use templates as starting points
- Monitor workflow executions for errors

### Report Generation

- Include context in executive summaries
- Use visual elements (graphs, timelines)
- Cite sources for credibility
- Schedule regular reports for stakeholders

## Getting Help

### In-App Help

- Hover over question marks for tooltips
- Click **Help** in navigation for documentation
- Use **Quick Start** guide for tutorials

### Support Channels

- **Documentation**: Comprehensive guides and references
- **Email Support**: support@osint-platform.example
- **Community Forum**: Share tips and ask questions
- **Video Tutorials**: Step-by-step video guides

### Keyboard Shortcuts

- `Ctrl/Cmd + K`: Quick search
- `Ctrl/Cmd + N`: New entity
- `Ctrl/Cmd + S`: Save current item
- `Esc`: Close modal/dialog
- `?`: Show keyboard shortcuts

---

For technical documentation, API reference, and advanced features, see the [Technical Documentation](../technical/README.md).
