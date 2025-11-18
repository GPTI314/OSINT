-- ============================================================================
-- Migration: 001_initial_schema
-- Description: Initial database schema setup for OSINT platform
-- Created: 2025-11-18
-- ============================================================================

-- This migration creates the complete initial schema
-- Run the main schema.sql file
\i ../postgresql/schema.sql

-- ============================================================================
-- Migration tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_migrations (version, description)
VALUES ('001', 'Initial schema setup with all core tables');

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
