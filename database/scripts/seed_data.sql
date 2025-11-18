-- ============================================================================
-- OSINT Platform - Seed Data
-- ============================================================================
-- This file contains sample data for development and testing
-- ============================================================================

-- WARNING: This is for development/testing only!
-- DO NOT run this in production!

BEGIN;

-- ============================================================================
-- USERS
-- ============================================================================

-- Create sample users (password: 'password123' hashed with bcrypt)
-- Note: In production, use proper password hashing
INSERT INTO users (id, username, email, password_hash, role, preferences) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'admin', 'admin@osint.local', '$2b$10$YourHashedPasswordHere', 'admin', '{"theme": "dark", "notifications": true}'),
    ('550e8400-e29b-41d4-a716-446655440002', 'analyst1', 'analyst1@osint.local', '$2b$10$YourHashedPasswordHere', 'analyst', '{"theme": "light", "notifications": true}'),
    ('550e8400-e29b-41d4-a716-446655440003', 'analyst2', 'analyst2@osint.local', '$2b$10$YourHashedPasswordHere', 'analyst', '{"theme": "dark", "notifications": false}'),
    ('550e8400-e29b-41d4-a716-446655440004', 'viewer', 'viewer@osint.local', '$2b$10$YourHashedPasswordHere', 'viewer', '{"theme": "auto", "notifications": true}')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- INVESTIGATIONS
-- ============================================================================

INSERT INTO investigations (id, name, description, status, priority, created_by, tags) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', 'Sample Investigation - Phishing Campaign', 'Investigation into suspected phishing campaign targeting financial institutions', 'active', 'high', '550e8400-e29b-41d4-a716-446655440001', ARRAY['phishing', 'cybercrime', 'financial']),
    ('650e8400-e29b-41d4-a716-446655440002', 'Brand Impersonation Analysis', 'Monitoring for brand impersonation across social media and web', 'active', 'medium', '550e8400-e29b-41d4-a716-446655440002', ARRAY['brand-protection', 'impersonation']),
    ('650e8400-e29b-41d4-a716-446655440003', 'Infrastructure Mapping', 'Mapping adversary infrastructure and command & control servers', 'active', 'critical', '550e8400-e29b-41d4-a716-446655440001', ARRAY['infrastructure', 'apt', 'c2']),
    ('650e8400-e29b-41d4-a716-446655440004', 'Data Breach Investigation', 'Investigating potential data breach and credential leaks', 'completed', 'high', '550e8400-e29b-41d4-a716-446655440002', ARRAY['breach', 'credentials', 'leak'])
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- TARGETS
-- ============================================================================

INSERT INTO targets (investigation_id, target_type, target_value, status, priority) VALUES
    -- Phishing campaign targets
    ('650e8400-e29b-41d4-a716-446655440001', 'domain', 'suspicious-bank-login.com', 'in_progress', 9),
    ('650e8400-e29b-41d4-a716-446655440001', 'domain', 'secure-banking-verify.net', 'pending', 8),
    ('650e8400-e29b-41d4-a716-446655440001', 'ip', '192.0.2.100', 'in_progress', 7),
    ('650e8400-e29b-41d4-a716-446655440001', 'email', 'support@suspicious-bank-login.com', 'pending', 6),

    -- Brand impersonation targets
    ('650e8400-e29b-41d4-a716-446655440002', 'username', 'fake_brand_official', 'in_progress', 7),
    ('650e8400-e29b-41d4-a716-446655440002', 'domain', 'brand-official-store.net', 'completed', 5),
    ('650e8400-e29b-41d4-a716-446655440002', 'url', 'https://fake-brand-store.com/products', 'pending', 6),

    -- Infrastructure mapping targets
    ('650e8400-e29b-41d4-a716-446655440003', 'ip', '198.51.100.50', 'in_progress', 10),
    ('650e8400-e29b-41d4-a716-446655440003', 'domain', 'malicious-c2-server.xyz', 'in_progress', 10),
    ('650e8400-e29b-41d4-a716-446655440003', 'ip', '203.0.113.25', 'pending', 9),

    -- Data breach investigation targets
    ('650e8400-e29b-41d4-a716-446655440004', 'email', 'leaked-user@example.com', 'completed', 7),
    ('650e8400-e29b-41d4-a716-446655440004', 'domain', 'compromised-service.com', 'completed', 8)
ON CONFLICT (investigation_id, target_type, target_value) DO NOTHING;

-- ============================================================================
-- FINDINGS
-- ============================================================================

INSERT INTO findings (investigation_id, title, description, finding_type, severity, confidence, status, tags, created_by) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', 'Confirmed Phishing Infrastructure', 'Domain registered recently with privacy protection, hosting login page identical to legitimate bank', 'threat', 'critical', 0.95, 'new', ARRAY['phishing', 'confirmed'], '550e8400-e29b-41d4-a716-446655440001'),
    ('650e8400-e29b-41d4-a716-446655440001', 'SSL Certificate Mismatch', 'SSL certificate issued for different domain, possible typosquatting', 'anomaly', 'high', 0.85, 'investigating', ARRAY['ssl', 'typosquatting'], '550e8400-e29b-41d4-a716-446655440001'),
    ('650e8400-e29b-41d4-a716-446655440002', 'Fake Social Media Account', 'Account impersonating brand with similar username and stolen profile images', 'threat', 'medium', 0.90, 'new', ARRAY['impersonation', 'social-media'], '550e8400-e29b-41d4-a716-446655440002'),
    ('650e8400-e29b-41d4-a716-446655440003', 'C2 Server Identified', 'Server showing characteristics of command and control infrastructure', 'threat', 'critical', 0.88, 'investigating', ARRAY['c2', 'infrastructure'], '550e8400-e29b-41d4-a716-446655440001'),
    ('650e8400-e29b-41d4-a716-446655440004', 'Credentials Found in Breach', 'User credentials found in public breach database', 'exposure', 'high', 1.0, 'resolved', ARRAY['breach', 'credentials'], '550e8400-e29b-41d4-a716-446655440002')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- DOMAIN INTELLIGENCE (Sample)
-- ============================================================================

INSERT INTO domain_intelligence (investigation_id, domain, registrar, whois_data, dns_records, technologies) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', 'suspicious-bank-login.com', 'Namecheap',
     '{"registrant": "WhoisGuard Protected", "created": "2024-01-15", "expires": "2025-01-15"}'::jsonb,
     '{"A": ["192.0.2.100"], "MX": ["mail.suspicious-bank-login.com"], "NS": ["ns1.namecheap.com", "ns2.namecheap.com"]}'::jsonb,
     '[{"name": "Nginx", "version": "1.18.0", "category": "Web Server"}, {"name": "PHP", "version": "7.4", "category": "Programming Language"}]'::jsonb),
    ('650e8400-e29b-41d4-a716-446655440003', 'malicious-c2-server.xyz', 'GoDaddy',
     '{"registrant": "Privacy Protected", "created": "2024-03-01", "expires": "2025-03-01"}'::jsonb,
     '{"A": ["198.51.100.50"], "NS": ["ns1.godaddy.com", "ns2.godaddy.com"]}'::jsonb,
     '[{"name": "Apache", "version": "2.4.41", "category": "Web Server"}]'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- IP INTELLIGENCE (Sample)
-- ============================================================================

INSERT INTO ip_intelligence (investigation_id, ip_address, geolocation, asn_data, is_proxy, is_vpn, is_tor) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', '192.0.2.100',
     '{"country": "US", "city": "Phoenix", "latitude": 33.4484, "longitude": -112.0740}'::jsonb,
     '{"asn": "AS15133", "org": "Edgecast"}'::jsonb, false, false, false),
    ('650e8400-e29b-41d4-a716-446655440003', '198.51.100.50',
     '{"country": "NL", "city": "Amsterdam", "latitude": 52.3702, "longitude": 4.8952}'::jsonb,
     '{"asn": "AS16509", "org": "Amazon.com, Inc."}'::jsonb, false, true, false)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- SCRAPING JOBS (Sample)
-- ============================================================================

DO $$
DECLARE
    target_id_1 UUID;
    target_id_2 UUID;
BEGIN
    SELECT id INTO target_id_1 FROM targets WHERE target_value = 'suspicious-bank-login.com' LIMIT 1;
    SELECT id INTO target_id_2 FROM targets WHERE target_value = 'brand-official-store.net' LIMIT 1;

    IF target_id_1 IS NOT NULL THEN
        INSERT INTO scraping_jobs (investigation_id, target_id, job_type, url, status, priority)
        VALUES
            ('650e8400-e29b-41d4-a716-446655440001', target_id_1, 'scrape', 'http://suspicious-bank-login.com', 'completed', 9),
            ('650e8400-e29b-41d4-a716-446655440001', target_id_1, 'screenshot', 'http://suspicious-bank-login.com/login', 'completed', 8)
        ON CONFLICT DO NOTHING;
    END IF;

    IF target_id_2 IS NOT NULL THEN
        INSERT INTO scraping_jobs (investigation_id, target_id, job_type, url, status, priority)
        VALUES
            ('650e8400-e29b-41d4-a716-446655440002', target_id_2, 'scrape', 'http://brand-official-store.net', 'completed', 5)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- ============================================================================
-- API KEYS (Sample)
-- ============================================================================

-- Sample API key for testing (key: 'test_api_key_123')
INSERT INTO api_keys (user_id, key_hash, name, permissions, rate_limit) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', encode(digest('test_api_key_123', 'sha256'), 'hex'), 'Development API Key',
     ARRAY['read', 'write', 'admin'], 5000)
ON CONFLICT DO NOTHING;

COMMIT;

-- ============================================================================
-- Display summary
-- ============================================================================

SELECT 'Seed data inserted successfully!' AS status;

SELECT
    'Users' AS table_name,
    COUNT(*) AS record_count
FROM users
UNION ALL
SELECT 'Investigations', COUNT(*) FROM investigations
UNION ALL
SELECT 'Targets', COUNT(*) FROM targets
UNION ALL
SELECT 'Findings', COUNT(*) FROM findings
UNION ALL
SELECT 'Domain Intelligence', COUNT(*) FROM domain_intelligence
UNION ALL
SELECT 'IP Intelligence', COUNT(*) FROM ip_intelligence
UNION ALL
SELECT 'Scraping Jobs', COUNT(*) FROM scraping_jobs
UNION ALL
SELECT 'API Keys', COUNT(*) FROM api_keys;

-- ============================================================================
-- END OF SEED DATA
-- ============================================================================
