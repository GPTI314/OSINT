-- OSINT Toolkit Database Initialization
-- This script is run when the PostgreSQL container first starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS osint;

-- Set search path
SET search_path TO osint, public;

-- Create initial tables (example schema)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL,
    target_value TEXT NOT NULL,
    metadata JSONB,
    risk_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    target_id UUID REFERENCES targets(id) ON DELETE CASCADE,
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    data JSONB,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_investigations_user ON investigations(user_id);
CREATE INDEX IF NOT EXISTS idx_targets_investigation ON targets(investigation_id);
CREATE INDEX IF NOT EXISTS idx_targets_type ON targets(target_type);
CREATE INDEX IF NOT EXISTS idx_data_sources_target ON data_sources(target_id);
CREATE INDEX IF NOT EXISTS idx_data_sources_type ON data_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_targets_metadata ON targets USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_data_sources_data ON data_sources USING gin(data);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_investigations_updated_at BEFORE UPDATE ON investigations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_targets_updated_at BEFORE UPDATE ON targets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA osint TO osint;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA osint TO osint;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA osint TO osint;
