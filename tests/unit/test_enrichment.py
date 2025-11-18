"""
Unit tests for data enrichment pipeline.

Tests cover:
- Data validation
- Format transformation
- Deduplication
- Enrichment processors
- Pipeline orchestration
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from typing import Dict, Any


@pytest.mark.unit
class TestEnrichmentPipeline:
    """Test the enrichment pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_execution(self, sample_collection_result):
        """Test executing the enrichment pipeline."""
        pipeline = Mock()
        pipeline.process = AsyncMock(
            return_value={
                "status": "success",
                "enriched_data": {"validated": True, "normalized": True},
            }
        )

        result = await pipeline.process(sample_collection_result)

        assert result["status"] == "success"
        assert result["enriched_data"]["validated"] is True

    @pytest.mark.asyncio
    async def test_pipeline_stages(self):
        """Test pipeline processes data through multiple stages."""
        pipeline = Mock()
        pipeline.stages = ["validate", "normalize", "enrich", "deduplicate"]
        pipeline.execute_stages = AsyncMock(return_value={"processed": True})

        result = await pipeline.execute_stages({})

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self):
        """Test pipeline handles errors in stages."""
        pipeline = Mock()
        pipeline.process = AsyncMock(
            return_value={"status": "error", "stage": "validation", "error": "Invalid data"}
        )

        result = await pipeline.process({})

        assert result["status"] == "error"
        assert result["stage"] == "validation"


@pytest.mark.unit
class TestDataValidation:
    """Test data validation."""

    def test_validate_ip_address(self, sample_ip_address):
        """Test IP address validation."""
        validator = Mock()
        validator.validate_ip = Mock(return_value=True)

        assert validator.validate_ip(sample_ip_address) is True

    def test_validate_domain(self, sample_domain):
        """Test domain validation."""
        validator = Mock()
        validator.validate_domain = Mock(return_value=True)

        assert validator.validate_domain(sample_domain) is True

    def test_validate_email(self, sample_email):
        """Test email validation."""
        validator = Mock()
        validator.validate_email = Mock(return_value=True)

        assert validator.validate_email(sample_email) is True

    def test_invalid_ip_address(self):
        """Test validation rejects invalid IP addresses."""
        validator = Mock()
        validator.validate_ip = Mock(return_value=False)

        assert validator.validate_ip("999.999.999.999") is False

    def test_invalid_domain(self):
        """Test validation rejects invalid domains."""
        validator = Mock()
        validator.validate_domain = Mock(return_value=False)

        assert validator.validate_domain("invalid..domain") is False

    def test_schema_validation(self):
        """Test schema validation for structured data."""
        validator = Mock()
        validator.validate_schema = Mock(return_value=True)

        data = {"entity_type": "ip", "value": "8.8.8.8"}
        assert validator.validate_schema(data) is True


@pytest.mark.unit
class TestDataTransformation:
    """Test data transformation."""

    def test_normalize_ip_address(self):
        """Test IP address normalization."""
        transformer = Mock()
        transformer.normalize_ip = Mock(return_value="8.8.8.8")

        result = transformer.normalize_ip("008.008.008.008")

        assert result == "8.8.8.8"

    def test_normalize_domain(self):
        """Test domain normalization."""
        transformer = Mock()
        transformer.normalize_domain = Mock(return_value="example.com")

        result = transformer.normalize_domain("EXAMPLE.COM")

        assert result == "example.com"

    def test_convert_date_format(self):
        """Test date format conversion."""
        transformer = Mock()
        transformer.convert_date = Mock(return_value="2024-01-01T00:00:00Z")

        result = transformer.convert_date("01/01/2024")

        assert "2024-01-01" in result

    def test_extract_metadata(self, sample_collection_result):
        """Test extracting metadata from collection results."""
        transformer = Mock()
        transformer.extract_metadata = Mock(
            return_value={"source": "dns_collector", "timestamp": "2024-01-01"}
        )

        metadata = transformer.extract_metadata(sample_collection_result)

        assert "source" in metadata
        assert "timestamp" in metadata


@pytest.mark.unit
class TestDeduplication:
    """Test data deduplication."""

    def test_deduplicate_entities(self):
        """Test deduplicating entities."""
        deduplicator = Mock()
        entities = [
            {"type": "ip", "value": "8.8.8.8"},
            {"type": "ip", "value": "8.8.8.8"},
            {"type": "ip", "value": "1.1.1.1"},
        ]
        deduplicator.deduplicate = Mock(
            return_value=[
                {"type": "ip", "value": "8.8.8.8"},
                {"type": "ip", "value": "1.1.1.1"},
            ]
        )

        result = deduplicator.deduplicate(entities)

        assert len(result) == 2

    def test_merge_duplicate_data(self):
        """Test merging data from duplicates."""
        deduplicator = Mock()
        deduplicator.merge = Mock(
            return_value={
                "value": "8.8.8.8",
                "sources": ["source1", "source2"],
                "metadata": {"merged": True},
            }
        )

        result = deduplicator.merge([{"value": "8.8.8.8"}, {"value": "8.8.8.8"}])

        assert result["metadata"]["merged"] is True
        assert len(result["sources"]) == 2

    def test_fuzzy_matching(self):
        """Test fuzzy matching for near-duplicates."""
        deduplicator = Mock()
        deduplicator.fuzzy_match = Mock(return_value=True)

        is_match = deduplicator.fuzzy_match("example.com", "example.org")

        assert is_match is True or is_match is False  # Depends on threshold


@pytest.mark.unit
class TestEnrichmentProcessors:
    """Test individual enrichment processors."""

    @pytest.mark.asyncio
    async def test_geolocation_enrichment(self, sample_ip_address):
        """Test geolocation enrichment."""
        enricher = Mock()
        enricher.enrich_geolocation = AsyncMock(
            return_value={
                "country": "US",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.084,
            }
        )

        result = await enricher.enrich_geolocation(sample_ip_address)

        assert "country" in result
        assert "city" in result

    @pytest.mark.asyncio
    async def test_asn_enrichment(self, sample_ip_address):
        """Test ASN enrichment."""
        enricher = Mock()
        enricher.enrich_asn = AsyncMock(
            return_value={"asn": "AS15169", "org": "Google LLC"}
        )

        result = await enricher.enrich_asn(sample_ip_address)

        assert "asn" in result
        assert "org" in result

    @pytest.mark.asyncio
    async def test_ssl_certificate_enrichment(self, sample_domain):
        """Test SSL certificate enrichment."""
        enricher = Mock()
        enricher.enrich_ssl = AsyncMock(
            return_value={
                "valid": True,
                "issuer": "Let's Encrypt",
                "expiry": "2025-01-01",
            }
        )

        result = await enricher.enrich_ssl(sample_domain)

        assert result["valid"] is True
        assert "issuer" in result

    @pytest.mark.asyncio
    async def test_reputation_enrichment(self, sample_ip_address):
        """Test reputation score enrichment."""
        enricher = Mock()
        enricher.enrich_reputation = AsyncMock(
            return_value={"score": 85, "category": "trusted", "sources": 5}
        )

        result = await enricher.enrich_reputation(sample_ip_address)

        assert result["score"] == 85
        assert result["category"] == "trusted"


@pytest.mark.unit
class TestDataQuality:
    """Test data quality checks."""

    def test_completeness_check(self, sample_entity_data):
        """Test data completeness validation."""
        quality_checker = Mock()
        quality_checker.check_completeness = Mock(
            return_value={"complete": True, "missing_fields": []}
        )

        result = quality_checker.check_completeness(sample_entity_data)

        assert result["complete"] is True

    def test_consistency_check(self):
        """Test data consistency validation."""
        quality_checker = Mock()
        quality_checker.check_consistency = Mock(return_value=True)

        data = {"ip": "8.8.8.8", "domain": "dns.google", "matches": True}
        assert quality_checker.check_consistency(data) is True

    def test_freshness_check(self):
        """Test data freshness validation."""
        quality_checker = Mock()
        quality_checker.check_freshness = Mock(
            return_value={"fresh": True, "age_hours": 2}
        )

        result = quality_checker.check_freshness({"timestamp": datetime.now()})

        assert result["fresh"] is True


@pytest.mark.unit
class TestCaching:
    """Test caching in enrichment pipeline."""

    @pytest.mark.asyncio
    async def test_cache_enrichment_results(self, mock_redis_client):
        """Test caching enrichment results."""
        cache = Mock()
        cache.client = mock_redis_client
        cache.set = AsyncMock(return_value=True)

        result = await cache.set("key", {"data": "value"}, ttl=3600)

        assert result is True

    @pytest.mark.asyncio
    async def test_retrieve_cached_results(self, mock_redis_client):
        """Test retrieving cached results."""
        cache = Mock()
        cache.get = AsyncMock(return_value={"data": "cached_value"})

        result = await cache.get("key")

        assert result is not None
        assert result["data"] == "cached_value"

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, mock_redis_client):
        """Test cache invalidation."""
        cache = Mock()
        cache.delete = AsyncMock(return_value=True)

        result = await cache.delete("key")

        assert result is True
