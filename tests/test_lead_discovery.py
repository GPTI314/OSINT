"""
Tests for Lead Discovery & Matchmaking System
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from lead_discovery import (
    CookieTracker,
    IdentifierManager,
    LeadDiscoveryEngine,
    LeadSignalDetector,
    LeadMatchmaker,
    MatchingAlgorithm,
    GeographicTargeting,
    ProfilerIntegration,
    LeadAlertSystem,
)
from lead_discovery.privacy_config import PrivacyConfig, PrivacyMode


# ============================================================================
# Privacy Configuration Tests
# ============================================================================

def test_privacy_config_gdpr_mode():
    """Test GDPR strict mode configuration."""
    config = PrivacyConfig()
    config.mode = PrivacyMode.GDPR_STRICT

    assert config.is_gdpr_mode() is True
    assert config.requires_consent('cookies') is True
    assert config.allows_fingerprinting() is False
    assert config.allows_cross_site_tracking() is False
    assert config.get_data_retention_days('cookies') == 30


def test_privacy_config_testing_mode():
    """Test testing mode configuration."""
    config = PrivacyConfig()
    config.mode = PrivacyMode.TESTING

    assert config.is_testing_mode() is True
    assert config.requires_consent('cookies') is False
    assert config.allows_fingerprinting() is True
    assert config.allows_cross_site_tracking() is True


# ============================================================================
# Signal Detection Tests
# ============================================================================

def test_loan_signal_detection():
    """Test detection of loan need signals."""
    detector = LeadSignalDetector()

    content = """
    We are looking for a small business loan to expand our operations.
    Need capital for new equipment and inventory financing.
    """

    signals = detector.detect_loan_signals(content, {})

    assert len(signals) > 0
    assert any(s['type'] == 'loan_need' for s in signals)
    assert all(s['strength'] > 0 for s in signals)


def test_consulting_signal_detection():
    """Test detection of consulting need signals."""
    detector = LeadSignalDetector()

    content = """
    We need help improving our business processes.
    Looking for strategic consulting to optimize operations.
    """

    signals = detector.detect_consulting_signals(content, {})

    assert len(signals) > 0
    assert any(s['type'] == 'consulting_need' for s in signals)


def test_financial_distress_detection():
    """Test detection of financial distress signals."""
    detector = LeadSignalDetector()

    content = """
    Struggling to make payroll. Cash flow crisis.
    Behind on payments and need urgent help.
    """

    signals = detector.detect_financial_distress(content)

    assert len(signals) > 0
    assert all(s['type'] == 'financial_distress' for s in signals)
    assert all(s['strength'] >= 80 for s in signals)  # High strength


def test_signal_strength_calculation():
    """Test signal strength calculation."""
    detector = LeadSignalDetector()

    signals = [
        {'type': 'loan_need', 'strength': 80},
        {'type': 'growth', 'strength': 70},
        {'type': 'expansion', 'strength': 75},
    ]

    strength = detector.calculate_signal_strength(signals)

    assert strength > 0
    assert strength <= 100
    assert strength > 75  # Should be above average with bonus


# ============================================================================
# Matching Algorithm Tests
# ============================================================================

def test_geographic_match():
    """Test geographic matching."""
    algo = MatchingAlgorithm()

    # Exact city match
    score1 = algo.geographic_match(
        'San Francisco', 'California', 'US',
        ['San Francisco, CA']
    )
    assert score1 == 100

    # State match
    score2 = algo.geographic_match(
        'Los Angeles', 'California', 'US',
        ['California', 'Nevada']
    )
    assert score2 == 85

    # Nationwide
    score3 = algo.geographic_match(
        'New York', 'New York', 'US',
        ['nationwide']
    )
    assert score3 == 100

    # No match
    score4 = algo.geographic_match(
        'New York', 'New York', 'US',
        ['California']
    )
    assert score4 == 0


def test_industry_match():
    """Test industry matching."""
    algo = MatchingAlgorithm()

    # Exact match
    score1 = algo.industry_match('technology', ['technology', 'software'])
    assert score1 == 100

    # Partial match
    score2 = algo.industry_match('software development', ['technology'])
    assert score2 >= 60

    # All industries
    score3 = algo.industry_match('retail', ['all'])
    assert score3 == 100

    # No match
    score4 = algo.industry_match('healthcare', ['technology', 'finance'])
    assert score4 <= 40


def test_need_match():
    """Test need matching."""
    algo = MatchingAlgorithm()

    # Direct need match
    score1 = algo.need_match(
        ['business_loan', 'expansion_financing'],
        'loan',
        'loan',
        'business_loan'
    )
    assert score1 >= 85

    # Category match
    score2 = algo.need_match(
        ['consulting'],
        'consulting',
        'consulting',
        'business_strategy'
    )
    assert score2 >= 70


def test_complete_match_score():
    """Test complete match score calculation."""
    algo = MatchingAlgorithm()

    lead = {
        'city': 'San Francisco',
        'state': 'California',
        'country': 'US',
        'industry': 'technology',
        'needs_identified': ['business_loan', 'growth_capital'],
        'lead_category': 'loan',
        'lead_type': 'business',
        'company_size': 'small',
        'signal_strength': 85,
        'intent_score': 80,
    }

    service = {
        'target_locations': ['California', 'Nevada'],
        'target_industries': ['technology', 'software'],
        'service_type': 'loan',
        'service_category': 'business_loan',
        'target_audience': 'business',
        'target_company_sizes': ['small', 'medium'],
        'requirements': {},
    }

    result = algo.calculate_match_score(lead, service)

    assert result['match_score'] > 0
    assert result['match_score'] <= 100
    assert result['geographic_score'] >= 80  # California match
    assert result['industry_score'] >= 80  # Tech match
    assert result['need_score'] >= 80  # Loan need match
    assert len(result['reasons']) > 0
    assert result['confidence_level'] in ['low', 'medium', 'high']


# ============================================================================
# Cookie Tracking Tests (Mocked)
# ============================================================================

@pytest.mark.asyncio
async def test_hash_identifier():
    """Test identifier hashing."""
    # Create mock db_pool
    db_pool = MagicMock()

    tracker = CookieTracker(db_pool)
    hash1 = tracker._hash_identifier('test@example.com')
    hash2 = tracker._hash_identifier('test@example.com')
    hash3 = tracker._hash_identifier('different@example.com')

    # Same input = same hash
    assert hash1 == hash2
    # Different input = different hash
    assert hash1 != hash3
    # Hash is 64 characters (SHA-256 hex)
    assert len(hash1) == 64


# ============================================================================
# Geographic Targeting Tests
# ============================================================================

def test_parse_location():
    """Test location parsing."""
    # Mock db_pool
    db_pool = MagicMock()
    geo = GeographicTargeting(db_pool)

    # City, State
    loc1 = geo._parse_location('San Francisco, CA')
    assert loc1['city'] == 'San Francisco'
    assert loc1['state'] == 'CA'
    assert loc1['type'] == 'text'

    # ZIP code
    loc2 = geo._parse_location('94102')
    assert loc2['postal_code'] == '94102'
    assert loc2['type'] == 'zip'

    # Lat, Lng
    loc3 = geo._parse_location('37.7749, -122.4194')
    assert loc3['latitude'] == 37.7749
    assert loc3['longitude'] == -122.4194
    assert loc3['type'] == 'coordinates'


def test_haversine_distance():
    """Test distance calculation."""
    db_pool = MagicMock()
    geo = GeographicTargeting(db_pool)

    # San Francisco to Los Angeles (approx 559 km)
    distance = geo._haversine_distance(
        37.7749, -122.4194,  # SF
        34.0522, -118.2437   # LA
    )

    assert 550 < distance < 570  # Approximately correct


# ============================================================================
# Integration Tests
# ============================================================================

def test_end_to_end_signal_to_match():
    """Test end-to-end: signal detection to matching."""
    # 1. Detect signals
    detector = LeadSignalDetector()
    content = "Need small business loan for expansion. Budget $50,000."
    signals = detector.detect_loan_signals(content, {})

    assert len(signals) > 0

    # 2. Create mock lead
    lead = {
        'city': 'Austin',
        'state': 'Texas',
        'industry': 'restaurant',
        'needs_identified': ['business_loan'],
        'lead_category': 'loan',
        'lead_type': 'business',
        'company_size': 'small',
        'signal_strength': detector.calculate_signal_strength(signals),
        'intent_score': 75,
    }

    # 3. Create mock service
    service = {
        'target_locations': ['Texas', 'nationwide'],
        'target_industries': ['all'],
        'service_type': 'loan',
        'service_category': 'business_loan',
        'target_audience': 'business',
        'target_company_sizes': ['small', 'medium'],
        'requirements': {},
    }

    # 4. Calculate match
    algo = MatchingAlgorithm()
    match = algo.calculate_match_score(lead, service)

    assert match['match_score'] >= 70  # Should be a good match
    assert match['need_score'] >= 80  # Strong need match
    assert 'loan' in str(match['reasons']).lower()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
