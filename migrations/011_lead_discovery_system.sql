-- LEAD DISCOVERY & MATCHMAKING SYSTEM DATABASE SCHEMA
-- WARNING: For authorized security testing and research purposes only
-- Implements tracking, lead discovery, and matchmaking capabilities

-- ============================================================================
-- MODULE 1: COOKIE & IDENTIFIER TRACKING
-- ============================================================================

-- Tracked Identifiers
CREATE TABLE IF NOT EXISTS tracked_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier_type VARCHAR(50) NOT NULL, -- cookie, email, phone, user_id, device_id, ip, etc.
    identifier_value VARCHAR(500) NOT NULL,
    identifier_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for privacy
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    seen_count INTEGER DEFAULT 1,
    sites_seen_on TEXT[],
    associated_profile_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_hash)
);

CREATE INDEX idx_tracked_identifiers_type ON tracked_identifiers(identifier_type);
CREATE INDEX idx_tracked_identifiers_hash ON tracked_identifiers(identifier_hash);
CREATE INDEX idx_tracked_identifiers_profile ON tracked_identifiers(associated_profile_id);

-- Cookie Tracking
CREATE TABLE IF NOT EXISTS cookie_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier_id UUID REFERENCES tracked_identifiers(id) ON DELETE CASCADE,
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    cookie_name VARCHAR(255) NOT NULL,
    cookie_value TEXT,
    cookie_domain VARCHAR(255),
    cookie_path VARCHAR(255),
    expires_at TIMESTAMP,
    is_secure BOOLEAN DEFAULT FALSE,
    is_http_only BOOLEAN DEFAULT FALSE,
    same_site VARCHAR(20), -- Strict, Lax, None
    site_url TEXT,
    collected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cookie_tracking_identifier ON cookie_tracking(identifier_id);
CREATE INDEX idx_cookie_tracking_investigation ON cookie_tracking(investigation_id);
CREATE INDEX idx_cookie_tracking_domain ON cookie_tracking(cookie_domain);

-- User Profiles (Built from Identifiers)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    profile_hash VARCHAR(64) UNIQUE NOT NULL,
    identifiers UUID[],
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(255),
    location VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    company VARCHAR(255),
    job_title VARCHAR(255),
    industry VARCHAR(100),
    interests TEXT[],
    behaviors JSONB DEFAULT '{}',
    device_fingerprint VARCHAR(64),
    ip_addresses INET[],
    sites_visited TEXT[],
    visit_count INTEGER DEFAULT 0,
    first_visit_at TIMESTAMP,
    last_visit_at TIMESTAMP,
    profile_score INTEGER DEFAULT 0, -- Quality/completeness score
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_user_profiles_investigation ON user_profiles(investigation_id);
CREATE INDEX idx_user_profiles_hash ON user_profiles(profile_hash);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_location ON user_profiles(city, state);

-- Cross-Site Tracking
CREATE TABLE IF NOT EXISTS cross_site_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier_id UUID REFERENCES tracked_identifiers(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    site_url TEXT NOT NULL,
    site_domain VARCHAR(255),
    visit_count INTEGER DEFAULT 1,
    first_visit_at TIMESTAMP DEFAULT NOW(),
    last_visit_at TIMESTAMP DEFAULT NOW(),
    pages_visited TEXT[],
    time_spent INTEGER DEFAULT 0, -- seconds
    actions_taken JSONB DEFAULT '[]',
    referrer TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cross_site_tracking_identifier ON cross_site_tracking(identifier_id);
CREATE INDEX idx_cross_site_tracking_profile ON cross_site_tracking(profile_id);
CREATE INDEX idx_cross_site_tracking_domain ON cross_site_tracking(site_domain);

-- Behavioral Tracking
CREATE TABLE IF NOT EXISTS behavioral_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    behavior_type VARCHAR(50), -- page_view, click, form_submit, search, scroll, etc.
    behavior_data JSONB DEFAULT '{}',
    site_url TEXT,
    page_path TEXT,
    element_id VARCHAR(255),
    element_class VARCHAR(255),
    element_text TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_behavioral_tracking_profile ON behavioral_tracking(profile_id);
CREATE INDEX idx_behavioral_tracking_type ON behavioral_tracking(behavior_type);
CREATE INDEX idx_behavioral_tracking_timestamp ON behavioral_tracking(timestamp DESC);

-- Device Fingerprints
CREATE TABLE IF NOT EXISTS device_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    fingerprint_hash VARCHAR(64) UNIQUE NOT NULL,
    user_agent TEXT,
    screen_resolution VARCHAR(50),
    color_depth INTEGER,
    timezone VARCHAR(50),
    language VARCHAR(50),
    plugins TEXT[],
    fonts TEXT[],
    canvas_fingerprint VARCHAR(64),
    webgl_fingerprint VARCHAR(64),
    audio_fingerprint VARCHAR(64),
    platform VARCHAR(50),
    cpu_cores INTEGER,
    device_memory INTEGER,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_device_fingerprints_profile ON device_fingerprints(profile_id);
CREATE INDEX idx_device_fingerprints_hash ON device_fingerprints(fingerprint_hash);

-- ============================================================================
-- MODULE 2: LEAD DISCOVERY
-- ============================================================================

-- Discovered Leads
CREATE TABLE IF NOT EXISTS discovered_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    lead_type VARCHAR(50) DEFAULT 'unknown', -- consumer, business, unknown
    lead_category VARCHAR(50), -- loan, consulting, financial_service, insurance, etc.
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    website TEXT,
    location VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    industry VARCHAR(100),
    company_size VARCHAR(50), -- small, medium, large, enterprise
    revenue_range VARCHAR(50),
    employee_count INTEGER,
    lead_source VARCHAR(100), -- website, social_media, directory, scraper, etc.
    source_url TEXT,
    signal_strength INTEGER DEFAULT 0, -- 0-100
    signals_detected JSONB DEFAULT '[]',
    needs_identified TEXT[],
    pain_points TEXT[],
    intent_score INTEGER DEFAULT 0, -- 0-100
    quality_score INTEGER DEFAULT 0, -- 0-100
    match_score DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'new', -- new, qualified, contacted, interested, converted, lost, invalid
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    assigned_to VARCHAR(255),
    notes TEXT,
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_contact_at TIMESTAMP,
    next_followup_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_discovered_leads_investigation ON discovered_leads(investigation_id);
CREATE INDEX idx_discovered_leads_profile ON discovered_leads(profile_id);
CREATE INDEX idx_discovered_leads_status ON discovered_leads(status);
CREATE INDEX idx_discovered_leads_category ON discovered_leads(lead_category);
CREATE INDEX idx_discovered_leads_location ON discovered_leads(city, state);
CREATE INDEX idx_discovered_leads_signal_strength ON discovered_leads(signal_strength DESC);
CREATE INDEX idx_discovered_leads_intent_score ON discovered_leads(intent_score DESC);

-- Lead Signals
CREATE TABLE IF NOT EXISTS lead_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES discovered_leads(id) ON DELETE CASCADE,
    signal_type VARCHAR(50), -- loan_need, consulting_need, financial_distress, growth, expansion, etc.
    signal_category VARCHAR(50), -- keyword, behavior, content, form, search, social
    signal_source VARCHAR(100),
    signal_content TEXT,
    signal_strength INTEGER DEFAULT 0, -- 0-100
    confidence DECIMAL(5,2) DEFAULT 0, -- 0-100
    context TEXT,
    detected_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lead_signals_lead ON lead_signals(lead_id);
CREATE INDEX idx_lead_signals_type ON lead_signals(signal_type);
CREATE INDEX idx_lead_signals_strength ON lead_signals(signal_strength DESC);

-- Lead Behavior
CREATE TABLE IF NOT EXISTS lead_behavior (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES discovered_leads(id) ON DELETE CASCADE,
    behavior_type VARCHAR(50), -- visit, search, form_fill, download, click, etc.
    behavior_data JSONB DEFAULT '{}',
    site_url TEXT,
    page_path TEXT,
    action_taken VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_lead_behavior_lead ON lead_behavior(lead_id);
CREATE INDEX idx_lead_behavior_type ON lead_behavior(behavior_type);
CREATE INDEX idx_lead_behavior_timestamp ON lead_behavior(timestamp DESC);

-- Lead Sources
CREATE TABLE IF NOT EXISTS lead_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50), -- website, directory, social_media, api, manual
    source_url TEXT,
    source_category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    scrape_frequency VARCHAR(50), -- daily, weekly, monthly, on_demand
    last_scraped_at TIMESTAMP,
    leads_discovered INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    configuration JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lead_sources_type ON lead_sources(source_type);
CREATE INDEX idx_lead_sources_active ON lead_sources(is_active);

-- ============================================================================
-- MODULE 3: MATCHMAKING SYSTEM
-- ============================================================================

-- Services/Products Catalog
CREATE TABLE IF NOT EXISTS services_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50), -- loan, consulting, financial_service, insurance, etc.
    service_category VARCHAR(100),
    description TEXT,
    target_audience VARCHAR(50), -- consumer, business, both
    target_industries TEXT[],
    target_locations TEXT[], -- States, cities, or "nationwide"
    target_company_sizes TEXT[], -- small, medium, large, enterprise
    min_loan_amount DECIMAL(15,2),
    max_loan_amount DECIMAL(15,2),
    interest_rate_range VARCHAR(50),
    loan_term_range VARCHAR(50),
    requirements JSONB DEFAULT '{}',
    matching_criteria JSONB DEFAULT '{}',
    pricing_model VARCHAR(50),
    commission_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    provider_name VARCHAR(255),
    provider_contact VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_services_catalog_type ON services_catalog(service_type);
CREATE INDEX idx_services_catalog_active ON services_catalog(is_active);

-- Lead-Service Matches
CREATE TABLE IF NOT EXISTS lead_service_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES discovered_leads(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services_catalog(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2) NOT NULL DEFAULT 0, -- 0-100
    geographic_score DECIMAL(5,2) DEFAULT 0,
    industry_score DECIMAL(5,2) DEFAULT 0,
    need_score DECIMAL(5,2) DEFAULT 0,
    profile_score DECIMAL(5,2) DEFAULT 0,
    behavioral_score DECIMAL(5,2) DEFAULT 0,
    match_reasons TEXT[],
    confidence_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    recommended_action VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    matched_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending', -- pending, contacted, interested, not_interested, converted
    contacted_at TIMESTAMP,
    response_received_at TIMESTAMP,
    conversion_at TIMESTAMP,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(lead_id, service_id)
);

CREATE INDEX idx_lead_service_matches_lead ON lead_service_matches(lead_id);
CREATE INDEX idx_lead_service_matches_service ON lead_service_matches(service_id);
CREATE INDEX idx_lead_service_matches_score ON lead_service_matches(match_score DESC);
CREATE INDEX idx_lead_service_matches_status ON lead_service_matches(status);

-- Match History
CREATE TABLE IF NOT EXISTS match_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES lead_service_matches(id) ON DELETE CASCADE,
    event_type VARCHAR(50), -- matched, contacted, responded, interested, converted, lost
    event_data JSONB DEFAULT '{}',
    notes TEXT,
    created_by VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_history_match ON match_history(match_id);
CREATE INDEX idx_match_history_timestamp ON match_history(timestamp DESC);

-- ============================================================================
-- MODULE 4: GEOGRAPHIC TARGETING
-- ============================================================================

-- Geographic Regions
CREATE TABLE IF NOT EXISTS geographic_regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_name VARCHAR(255) NOT NULL,
    region_type VARCHAR(50), -- city, state, country, zip_code, custom
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    radius_km DECIMAL(10, 2),
    population INTEGER,
    business_count INTEGER,
    market_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_geographic_regions_type ON geographic_regions(region_type);
CREATE INDEX idx_geographic_regions_location ON geographic_regions(city, state);

-- Local Businesses
CREATE TABLE IF NOT EXISTS local_businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    industry VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(50),
    email VARCHAR(255),
    website TEXT,
    rating DECIMAL(3,2),
    review_count INTEGER,
    business_hours JSONB,
    source VARCHAR(100), -- google_places, yelp, directory, manual
    source_url TEXT,
    last_updated TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_local_businesses_location ON local_businesses(city, state);
CREATE INDEX idx_local_businesses_industry ON local_businesses(industry);
CREATE INDEX idx_local_businesses_source ON local_businesses(source);

-- ============================================================================
-- MODULE 5: ALERTS & NOTIFICATIONS
-- ============================================================================

-- Alert Rules
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50), -- new_lead, high_score_match, geographic, industry, behavior_change
    conditions JSONB NOT NULL,
    alert_channels TEXT[], -- email, webhook, dashboard
    recipients TEXT[],
    webhook_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    priority VARCHAR(20) DEFAULT 'medium',
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_rules_type ON alert_rules(rule_type);
CREATE INDEX idx_alert_rules_active ON alert_rules(is_active);

-- Alerts
CREATE TABLE IF NOT EXISTS lead_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_rule_id UUID REFERENCES alert_rules(id) ON DELETE CASCADE,
    alert_type VARCHAR(50),
    lead_id UUID REFERENCES discovered_leads(id) ON DELETE CASCADE,
    match_id UUID REFERENCES lead_service_matches(id) ON DELETE CASCADE,
    title VARCHAR(255),
    message TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'new', -- new, read, actioned, dismissed
    alert_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP,
    actioned_at TIMESTAMP
);

CREATE INDEX idx_lead_alerts_rule ON lead_alerts(alert_rule_id);
CREATE INDEX idx_lead_alerts_lead ON lead_alerts(lead_id);
CREATE INDEX idx_lead_alerts_status ON lead_alerts(status);
CREATE INDEX idx_lead_alerts_created ON lead_alerts(created_at DESC);

-- ============================================================================
-- MODULE 6: SCRAPING & DATA COLLECTION
-- ============================================================================

-- Scraping Jobs
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(50), -- discovery, enrichment, monitoring
    source_id UUID REFERENCES lead_sources(id) ON DELETE CASCADE,
    target_url TEXT,
    scraping_config JSONB DEFAULT '{}',
    schedule VARCHAR(50), -- cron expression or frequency
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    leads_discovered INTEGER DEFAULT 0,
    items_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_log TEXT,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scraping_jobs_source ON scraping_jobs(source_id);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_next_run ON scraping_jobs(next_run_at);

-- ============================================================================
-- MODULE 7: ANALYTICS & REPORTING
-- ============================================================================

-- Lead Analytics
CREATE TABLE IF NOT EXISTS lead_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    leads_discovered INTEGER DEFAULT 0,
    leads_qualified INTEGER DEFAULT 0,
    leads_contacted INTEGER DEFAULT 0,
    leads_converted INTEGER DEFAULT 0,
    matches_created INTEGER DEFAULT 0,
    avg_signal_strength DECIMAL(5,2) DEFAULT 0,
    avg_match_score DECIMAL(5,2) DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0,
    top_sources TEXT[],
    top_industries TEXT[],
    top_locations TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);

CREATE INDEX idx_lead_analytics_date ON lead_analytics(date DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_tracked_identifiers_updated_at BEFORE UPDATE ON tracked_identifiers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_discovered_leads_updated_at BEFORE UPDATE ON discovered_leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_catalog_updated_at BEFORE UPDATE ON services_catalog FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_service_matches_updated_at BEFORE UPDATE ON lead_service_matches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lead_sources_updated_at BEFORE UPDATE ON lead_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_geographic_regions_updated_at BEFORE UPDATE ON geographic_regions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample services
INSERT INTO services_catalog (service_name, service_type, service_category, description, target_audience, target_industries, target_locations, min_loan_amount, max_loan_amount, is_active)
VALUES
    ('Small Business Loan', 'loan', 'business_loan', 'Loans for small businesses up to $500K', 'business', ARRAY['retail', 'services', 'technology'], ARRAY['nationwide'], 10000, 500000, TRUE),
    ('Business Consulting', 'consulting', 'business_strategy', 'Strategic business consulting services', 'business', ARRAY['all'], ARRAY['nationwide'], NULL, NULL, TRUE),
    ('Personal Loan', 'loan', 'personal_loan', 'Personal loans up to $50K', 'consumer', ARRAY['all'], ARRAY['nationwide'], 1000, 50000, TRUE),
    ('Financial Planning', 'consulting', 'financial_planning', 'Comprehensive financial planning services', 'both', ARRAY['all'], ARRAY['nationwide'], NULL, NULL, TRUE);

-- Insert sample lead sources
INSERT INTO lead_sources (source_name, source_type, source_url, source_category, is_active)
VALUES
    ('Google Business', 'directory', 'https://business.google.com', 'local_directory', TRUE),
    ('Yelp', 'directory', 'https://www.yelp.com', 'local_directory', TRUE),
    ('LinkedIn', 'social_media', 'https://www.linkedin.com', 'professional_network', TRUE),
    ('Yellow Pages', 'directory', 'https://www.yellowpages.com', 'business_directory', TRUE);

-- Insert sample alert rule
INSERT INTO alert_rules (rule_name, rule_type, conditions, alert_channels, is_active, priority)
VALUES
    ('High Score Match Alert', 'high_score_match', '{"min_match_score": 80}', ARRAY['dashboard', 'email'], TRUE, 'high'),
    ('New Lead Alert', 'new_lead', '{"min_signal_strength": 60}', ARRAY['dashboard'], TRUE, 'medium');

COMMENT ON TABLE tracked_identifiers IS 'Stores tracked cookies, emails, and other identifiers for security testing';
COMMENT ON TABLE cookie_tracking IS 'Tracks cookies collected during security testing';
COMMENT ON TABLE user_profiles IS 'User profiles built from tracked identifiers';
COMMENT ON TABLE discovered_leads IS 'Leads discovered through scraping and tracking';
COMMENT ON TABLE lead_service_matches IS 'Matches between leads and services';
COMMENT ON TABLE services_catalog IS 'Catalog of services/products to match with leads';
