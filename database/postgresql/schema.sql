-- ============================================================================
-- OSINT Platform - PostgreSQL Database Schema
-- ============================================================================
-- Version: 1.0.0
-- Description: Comprehensive schema for OSINT investigation platform
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Users table (must be created first for foreign key references)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- admin, analyst, viewer
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- API Keys for programmatic access
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    permissions TEXT[],
    rate_limit INTEGER DEFAULT 1000,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- INVESTIGATIONS & TARGETS
-- ============================================================================

-- Projects/Investigations
CREATE TABLE investigations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, completed, archived
    priority VARCHAR(20) DEFAULT 'medium', -- critical, high, medium, low
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Targets (Domains, IPs, Emails, etc.)
CREATE TABLE targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL, -- domain, ip, email, phone, username, url, person, organization
    target_value VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(investigation_id, target_type, target_value)
);

-- ============================================================================
-- SCRAPING & CRAWLING
-- ============================================================================

-- Scraping Jobs
CREATE TABLE scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    target_id UUID REFERENCES targets(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- scrape, crawl, api_fetch, screenshot
    url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'queued', -- queued, running, completed, failed, paused, cancelled
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Scraped Data
CREATE TABLE scraped_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    target_id UUID REFERENCES targets(id) ON DELETE CASCADE,
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL, -- html, text, json, image, pdf, screenshot, etc.
    url TEXT NOT NULL,
    content TEXT,
    content_hash VARCHAR(64),
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    status_code INTEGER,
    headers JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    extracted_data JSONB DEFAULT '{}', -- Structured extracted data
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_id, url, content_hash)
);

-- Crawling Sessions
CREATE TABLE crawling_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    start_url TEXT NOT NULL,
    max_depth INTEGER DEFAULT 3,
    max_pages INTEGER DEFAULT 1000,
    allowed_domains TEXT[] DEFAULT '{}',
    disallowed_patterns TEXT[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed, paused, cancelled
    pages_crawled INTEGER DEFAULT 0,
    pages_failed INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    configuration JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Crawled Pages
CREATE TABLE crawled_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES crawling_sessions(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    depth INTEGER NOT NULL,
    parent_url TEXT,
    title TEXT,
    content TEXT,
    content_hash VARCHAR(64),
    status_code INTEGER,
    load_time FLOAT,
    links TEXT[] DEFAULT '{}',
    images TEXT[] DEFAULT '{}',
    scripts TEXT[] DEFAULT '{}',
    forms JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, url)
);

-- ============================================================================
-- INTELLIGENCE DATA
-- ============================================================================

-- Generic Intelligence Data (Aggregated)
CREATE TABLE intelligence_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    target_id UUID REFERENCES targets(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL, -- whois, dns, ssl, social, breach, etc.
    source VARCHAR(100), -- Source of the intelligence
    raw_data JSONB DEFAULT '{}',
    parsed_data JSONB DEFAULT '{}',
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Social Media Intelligence
CREATE TABLE social_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- twitter, facebook, linkedin, instagram, tiktok, github, etc.
    username VARCHAR(255),
    profile_url TEXT,
    profile_data JSONB DEFAULT '{}',
    posts JSONB DEFAULT '[]',
    connections JSONB DEFAULT '{}',
    activity_data JSONB DEFAULT '{}',
    follower_count INTEGER,
    following_count INTEGER,
    collected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Domain Intelligence
CREATE TABLE domain_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    whois_data JSONB DEFAULT '{}',
    dns_records JSONB DEFAULT '{}',
    ssl_certificate JSONB DEFAULT '{}',
    subdomains TEXT[] DEFAULT '{}',
    technologies JSONB DEFAULT '[]', -- Detected technologies (Wappalyzer, etc.)
    historical_data JSONB DEFAULT '{}',
    threat_intelligence JSONB DEFAULT '{}',
    registrar VARCHAR(255),
    creation_date TIMESTAMP,
    expiration_date TIMESTAMP,
    collected_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- IP Intelligence
CREATE TABLE ip_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    geolocation JSONB DEFAULT '{}',
    asn_data JSONB DEFAULT '{}',
    threat_intelligence JSONB DEFAULT '{}',
    port_scan_results JSONB DEFAULT '{}',
    service_detection JSONB DEFAULT '{}',
    reverse_dns TEXT,
    is_proxy BOOLEAN,
    is_vpn BOOLEAN,
    is_tor BOOLEAN,
    collected_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Email Intelligence
CREATE TABLE email_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    breach_data JSONB DEFAULT '[]',
    social_profiles JSONB DEFAULT '[]',
    domain_data JSONB DEFAULT '{}',
    verification_status VARCHAR(50), -- valid, invalid, risky, unknown
    disposable BOOLEAN,
    free_provider BOOLEAN,
    collected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Phone Intelligence
CREATE TABLE phone_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    phone_number VARCHAR(50) NOT NULL,
    carrier_info JSONB DEFAULT '{}',
    location_data JSONB DEFAULT '{}',
    social_profiles JSONB DEFAULT '[]',
    verification_status VARCHAR(50), -- valid, invalid, unknown
    line_type VARCHAR(50), -- mobile, landline, voip, unknown
    collected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Image Intelligence
CREATE TABLE image_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    image_url TEXT,
    image_hash VARCHAR(64),
    file_path TEXT,
    reverse_image_results JSONB DEFAULT '[]',
    metadata_extraction JSONB DEFAULT '{}', -- EXIF, GPS, camera info, etc.
    ocr_text TEXT,
    face_detection JSONB DEFAULT '[]',
    object_detection JSONB DEFAULT '[]',
    image_dimensions JSONB DEFAULT '{}',
    collected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- FINDINGS & REPORTS
-- ============================================================================

-- Findings/Insights
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    finding_type VARCHAR(50), -- threat, correlation, anomaly, vulnerability, exposure
    severity VARCHAR(20), -- critical, high, medium, low, info
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    related_data JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'new', -- new, investigating, resolved, dismissed
    metadata JSONB DEFAULT '{}'
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    report_type VARCHAR(50), -- summary, detailed, executive, technical
    title VARCHAR(255) NOT NULL,
    content TEXT,
    data JSONB DEFAULT '{}',
    format VARCHAR(20), -- pdf, html, json, markdown, docx
    file_path TEXT,
    generated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- AUDIT & LOGGING
-- ============================================================================

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- API Keys indexes
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- Investigation indexes
CREATE INDEX idx_investigations_status ON investigations(status);
CREATE INDEX idx_investigations_created_by ON investigations(created_by);
CREATE INDEX idx_investigations_priority ON investigations(priority);
CREATE INDEX idx_investigations_created_at ON investigations(created_at DESC);

-- Target indexes
CREATE INDEX idx_targets_investigation ON targets(investigation_id);
CREATE INDEX idx_targets_type_value ON targets(target_type, target_value);
CREATE INDEX idx_targets_status ON targets(status);

-- Scraping job indexes
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_investigation ON scraping_jobs(investigation_id);
CREATE INDEX idx_scraping_jobs_target ON scraping_jobs(target_id);
CREATE INDEX idx_scraping_jobs_scheduled ON scraping_jobs(scheduled_at);
CREATE INDEX idx_scraping_jobs_priority ON scraping_jobs(priority DESC);

-- Scraped data indexes
CREATE INDEX idx_scraped_data_job ON scraped_data(job_id);
CREATE INDEX idx_scraped_data_target ON scraped_data(target_id);
CREATE INDEX idx_scraped_data_investigation ON scraped_data(investigation_id);
CREATE INDEX idx_scraped_data_hash ON scraped_data(content_hash);
CREATE INDEX idx_scraped_data_type ON scraped_data(data_type);

-- Crawling session indexes
CREATE INDEX idx_crawling_sessions_investigation ON crawling_sessions(investigation_id);
CREATE INDEX idx_crawling_sessions_status ON crawling_sessions(status);

-- Crawled pages indexes
CREATE INDEX idx_crawled_pages_session ON crawled_pages(session_id);
CREATE INDEX idx_crawled_pages_url ON crawled_pages(url);
CREATE INDEX idx_crawled_pages_hash ON crawled_pages(content_hash);

-- Intelligence data indexes
CREATE INDEX idx_intelligence_data_investigation ON intelligence_data(investigation_id);
CREATE INDEX idx_intelligence_data_target ON intelligence_data(target_id);
CREATE INDEX idx_intelligence_data_type ON intelligence_data(data_type);
CREATE INDEX idx_intelligence_data_source ON intelligence_data(source);

-- Social intelligence indexes
CREATE INDEX idx_social_intelligence_investigation ON social_intelligence(investigation_id);
CREATE INDEX idx_social_intelligence_platform ON social_intelligence(platform);
CREATE INDEX idx_social_intelligence_username ON social_intelligence(username);

-- Domain intelligence indexes
CREATE INDEX idx_domain_intelligence_investigation ON domain_intelligence(investigation_id);
CREATE INDEX idx_domain_intelligence_domain ON domain_intelligence(domain);

-- IP intelligence indexes
CREATE INDEX idx_ip_intelligence_investigation ON ip_intelligence(investigation_id);
CREATE INDEX idx_ip_intelligence_ip ON ip_intelligence(ip_address);

-- Email intelligence indexes
CREATE INDEX idx_email_intelligence_investigation ON email_intelligence(investigation_id);
CREATE INDEX idx_email_intelligence_email ON email_intelligence(email);

-- Phone intelligence indexes
CREATE INDEX idx_phone_intelligence_investigation ON phone_intelligence(investigation_id);
CREATE INDEX idx_phone_intelligence_phone ON phone_intelligence(phone_number);

-- Image intelligence indexes
CREATE INDEX idx_image_intelligence_investigation ON image_intelligence(investigation_id);
CREATE INDEX idx_image_intelligence_hash ON image_intelligence(image_hash);

-- Findings indexes
CREATE INDEX idx_findings_investigation ON findings(investigation_id);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_status ON findings(status);
CREATE INDEX idx_findings_type ON findings(finding_type);
CREATE INDEX idx_findings_created_at ON findings(created_at DESC);

-- Reports indexes
CREATE INDEX idx_reports_investigation ON reports(investigation_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_generated_at ON reports(generated_at DESC);

-- Audit log indexes
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- ============================================================================
-- FULL TEXT SEARCH INDEXES
-- ============================================================================

-- Full-text search on findings
CREATE INDEX idx_findings_fulltext ON findings USING gin(to_tsvector('english',
    coalesce(title, '') || ' ' || coalesce(description, '')));

-- Full-text search on scraped content
CREATE INDEX idx_scraped_data_fulltext ON scraped_data USING gin(to_tsvector('english',
    coalesce(content, '')));

-- Full-text search on crawled pages
CREATE INDEX idx_crawled_pages_fulltext ON crawled_pages USING gin(to_tsvector('english',
    coalesce(title, '') || ' ' || coalesce(content, '')));

-- ============================================================================
-- JSONB INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_intelligence_data_raw_data ON intelligence_data USING gin(raw_data);
CREATE INDEX idx_intelligence_data_parsed_data ON intelligence_data USING gin(parsed_data);
CREATE INDEX idx_findings_related_data ON findings USING gin(related_data);
CREATE INDEX idx_domain_intelligence_technologies ON domain_intelligence USING gin(technologies);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_investigations_updated_at BEFORE UPDATE ON investigations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_targets_updated_at BEFORE UPDATE ON targets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_intelligence_data_updated_at BEFORE UPDATE ON intelligence_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_domain_intelligence_updated_at BEFORE UPDATE ON domain_intelligence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ip_intelligence_updated_at BEFORE UPDATE ON ip_intelligence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_findings_updated_at BEFORE UPDATE ON findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active investigations with target counts
CREATE VIEW v_active_investigations AS
SELECT
    i.id,
    i.name,
    i.description,
    i.status,
    i.priority,
    i.created_at,
    i.updated_at,
    COUNT(DISTINCT t.id) as target_count,
    COUNT(DISTINCT f.id) as finding_count,
    u.username as created_by_username
FROM investigations i
LEFT JOIN targets t ON i.id = t.investigation_id
LEFT JOIN findings f ON i.id = f.investigation_id
LEFT JOIN users u ON i.created_by = u.id
WHERE i.status = 'active'
GROUP BY i.id, u.username;

-- Recent findings by severity
CREATE VIEW v_recent_findings AS
SELECT
    f.*,
    i.name as investigation_name,
    u.username as created_by_username
FROM findings f
LEFT JOIN investigations i ON f.investigation_id = i.id
LEFT JOIN users u ON f.created_by = u.id
WHERE f.created_at > NOW() - INTERVAL '30 days'
ORDER BY f.created_at DESC;

-- Job queue status
CREATE VIEW v_job_queue_status AS
SELECT
    status,
    COUNT(*) as count,
    AVG(priority) as avg_priority
FROM scraping_jobs
WHERE status IN ('queued', 'running')
GROUP BY status;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE investigations IS 'Core investigation/project tracking';
COMMENT ON TABLE targets IS 'Investigation targets (domains, IPs, emails, etc.)';
COMMENT ON TABLE scraping_jobs IS 'Web scraping and data collection jobs';
COMMENT ON TABLE scraped_data IS 'Collected data from scraping operations';
COMMENT ON TABLE intelligence_data IS 'Aggregated intelligence from various sources';
COMMENT ON TABLE findings IS 'Investigation findings and insights';
COMMENT ON TABLE audit_log IS 'System audit trail for compliance and security';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
