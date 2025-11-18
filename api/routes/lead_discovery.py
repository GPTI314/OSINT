"""
Lead Discovery API Routes

REST API endpoints for lead discovery and matchmaking system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from ...database import get_db_pool
from ...lead_discovery import (
    CookieTracker,
    IdentifierManager,
    LeadDiscoveryEngine,
    LeadSignalDetector,
    LeadMatchmaker,
    GeographicTargeting,
    ProfilerIntegration,
    LeadAlertSystem,
)
from ...lead_discovery.privacy_config import get_privacy_config


router = APIRouter(prefix="/api/v1/lead-discovery", tags=["lead_discovery"])


# ============================================================================
# Request/Response Models
# ============================================================================

class LeadDiscoveryCriteria(BaseModel):
    investigation_id: UUID
    geographic_area: Optional[str] = None
    radius_km: Optional[float] = 50
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    company_size: Optional[str] = None
    lead_category: Optional[str] = None


class IdentifierData(BaseModel):
    investigation_id: UUID
    identifier_type: str
    identifier_value: str
    sites: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class CookieData(BaseModel):
    investigation_id: UUID
    url: str
    cookies: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = {}


class BehaviorData(BaseModel):
    profile_id: UUID
    behavior_type: str
    behavior_data: Dict[str, Any]
    site_url: Optional[str] = None


class LocalDiscoveryRequest(BaseModel):
    investigation_id: UUID
    location: str
    radius_km: float = Field(default=50, ge=1, le=500)
    criteria: Optional[Dict[str, Any]] = {}


class MatchCriteria(BaseModel):
    min_match_score: Optional[float] = None
    location: Optional[str] = None
    industry: Optional[str] = None


class LeadEnrichmentRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


# ============================================================================
# Lead Discovery Endpoints
# ============================================================================

@router.post("/discover")
async def discover_leads(
    criteria: LeadDiscoveryCriteria,
    db_pool=Depends(get_db_pool)
):
    """
    Discover leads based on criteria.

    Searches for potential leads using:
    - Geographic targeting
    - Industry filtering
    - Keyword matching
    - Company size filtering
    """
    engine = LeadDiscoveryEngine(db_pool)

    try:
        lead_ids = await engine.discover_leads(
            str(criteria.investigation_id),
            criteria.dict(exclude={'investigation_id'})
        )

        return {
            "success": True,
            "leads_discovered": len(lead_ids),
            "lead_ids": lead_ids
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads")
async def list_leads(
    investigation_id: Optional[UUID] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    industry: Optional[str] = None,
    min_signal_strength: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db_pool=Depends(get_db_pool)
):
    """List discovered leads with optional filters."""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM discovered_leads WHERE 1=1"
            params = []
            param_count = 1

            if investigation_id:
                query += f" AND investigation_id = ${param_count}"
                params.append(str(investigation_id))
                param_count += 1

            if status:
                query += f" AND status = ${param_count}"
                params.append(status)
                param_count += 1

            if location:
                query += f" AND (city ILIKE ${param_count} OR state ILIKE ${param_count})"
                params.append(f"%{location}%")
                param_count += 1

            if industry:
                query += f" AND industry ILIKE ${param_count}"
                params.append(f"%{industry}%")
                param_count += 1

            if min_signal_strength is not None:
                query += f" AND signal_strength >= ${param_count}"
                params.append(min_signal_strength)
                param_count += 1

            query += f" ORDER BY signal_strength DESC, discovered_at DESC"
            query += f" LIMIT ${param_count} OFFSET ${param_count + 1}"
            params.extend([limit, offset])

            leads = await conn.fetch(query, *params)

            return {
                "success": True,
                "count": len(leads),
                "leads": [dict(lead) for lead in leads]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}")
async def get_lead(lead_id: UUID, db_pool=Depends(get_db_pool)):
    """Get detailed information about a lead."""
    try:
        async with db_pool.acquire() as conn:
            # Get lead
            lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, str(lead_id))

            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")

            # Get signals
            signals = await conn.fetch("""
                SELECT * FROM lead_signals WHERE lead_id = $1
                ORDER BY signal_strength DESC
            """, str(lead_id))

            # Get behaviors
            behaviors = await conn.fetch("""
                SELECT * FROM lead_behavior WHERE lead_id = $1
                ORDER BY timestamp DESC
                LIMIT 50
            """, str(lead_id))

            return {
                "success": True,
                "lead": dict(lead),
                "signals": [dict(s) for s in signals],
                "behaviors": [dict(b) for b in behaviors]
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/{lead_id}/enrich")
async def enrich_lead(
    lead_id: UUID,
    enrichment: LeadEnrichmentRequest,
    db_pool=Depends(get_db_pool)
):
    """Enrich lead with profiler data."""
    integration = ProfilerIntegration(db_pool)

    try:
        result = await integration.enrich_lead_with_profiler(
            str(lead_id),
            enrichment.username,
            enrichment.email
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Matchmaking Endpoints
# ============================================================================

@router.post("/leads/{lead_id}/match")
async def match_lead_to_services(
    lead_id: UUID,
    limit: int = Query(default=10, le=50),
    db_pool=Depends(get_db_pool)
):
    """Match lead to appropriate services."""
    matchmaker = LeadMatchmaker(db_pool)

    try:
        matches = await matchmaker.match_lead_to_services(str(lead_id), limit)

        return {
            "success": True,
            "lead_id": str(lead_id),
            "matches_count": len(matches),
            "matches": matches
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}/matches")
async def get_lead_matches(
    lead_id: UUID,
    db_pool=Depends(get_db_pool)
):
    """Get service matches for a lead."""
    try:
        async with db_pool.acquire() as conn:
            matches = await conn.fetch("""
                SELECT lsm.*, sc.service_name, sc.service_type, sc.description
                FROM lead_service_matches lsm
                JOIN services_catalog sc ON sc.id = lsm.service_id
                WHERE lsm.lead_id = $1
                ORDER BY lsm.match_score DESC
            """, str(lead_id))

            return {
                "success": True,
                "count": len(matches),
                "matches": [dict(m) for m in matches]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_id}/leads")
async def get_leads_for_service(
    service_id: UUID,
    criteria: Optional[MatchCriteria] = None,
    limit: int = Query(default=100, le=500),
    db_pool=Depends(get_db_pool)
):
    """Get matched leads for a service."""
    matchmaker = LeadMatchmaker(db_pool)

    try:
        criteria_dict = criteria.dict(exclude_none=True) if criteria else {}

        leads = await matchmaker.rank_leads(
            str(service_id),
            criteria_dict,
            limit
        )

        return {
            "success": True,
            "service_id": str(service_id),
            "count": len(leads),
            "leads": leads
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/matches/{match_id}/status")
async def update_match_status(
    match_id: UUID,
    status: str,
    notes: Optional[str] = None,
    db_pool=Depends(get_db_pool)
):
    """Update match status."""
    matchmaker = LeadMatchmaker(db_pool)

    try:
        success = await matchmaker.update_match_status(
            str(match_id),
            status,
            notes
        )

        return {
            "success": success,
            "match_id": str(match_id),
            "status": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tracking Endpoints
# ============================================================================

@router.post("/tracking/identifiers")
async def track_identifier(
    identifier_data: IdentifierData,
    db_pool=Depends(get_db_pool)
):
    """Track a cookie or identifier."""
    tracker = CookieTracker(db_pool)
    privacy = get_privacy_config()

    # Check if tracking is allowed
    if privacy.requires_consent(identifier_data.identifier_type):
        if not identifier_data.metadata.get('consent_given'):
            raise HTTPException(
                status_code=403,
                detail="Consent required for this type of tracking"
            )

    try:
        identifier_id = await tracker._track_identifier(
            identifier_data.identifier_type,
            identifier_data.identifier_value,
            identifier_data.sites,
            identifier_data.metadata
        )

        return {
            "success": True,
            "identifier_id": identifier_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tracking/cookies")
async def track_cookies(
    cookie_data: CookieData,
    db_pool=Depends(get_db_pool)
):
    """Track cookies from a website."""
    tracker = CookieTracker(db_pool)

    try:
        tracking_ids = await tracker.track_cookies(
            str(cookie_data.investigation_id),
            cookie_data.url,
            cookie_data.cookies,
            cookie_data.metadata
        )

        return {
            "success": True,
            "cookies_tracked": len(tracking_ids),
            "tracking_ids": tracking_ids
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tracking/behavior")
async def track_behavior(
    behavior_data: BehaviorData,
    db_pool=Depends(get_db_pool)
):
    """Track user behavior."""
    tracker = CookieTracker(db_pool)

    try:
        behavior_id = await tracker.track_behavior(
            str(behavior_data.profile_id),
            behavior_data.behavior_type,
            behavior_data.behavior_data,
            behavior_data.site_url
        )

        return {
            "success": True,
            "behavior_id": behavior_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracking/profiles")
async def list_profiles(
    investigation_id: Optional[UUID] = None,
    limit: int = Query(default=100, le=500),
    db_pool=Depends(get_db_pool)
):
    """List tracked user profiles."""
    try:
        async with db_pool.acquire() as conn:
            if investigation_id:
                profiles = await conn.fetch("""
                    SELECT * FROM user_profiles
                    WHERE investigation_id = $1
                    ORDER BY updated_at DESC
                    LIMIT $2
                """, str(investigation_id), limit)
            else:
                profiles = await conn.fetch("""
                    SELECT * FROM user_profiles
                    ORDER BY updated_at DESC
                    LIMIT $1
                """, limit)

            return {
                "success": True,
                "count": len(profiles),
                "profiles": [dict(p) for p in profiles]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracking/profiles/{profile_id}")
async def get_profile(profile_id: UUID, db_pool=Depends(get_db_pool)):
    """Get user profile details."""
    manager = IdentifierManager(db_pool)

    try:
        async with db_pool.acquire() as conn:
            profile = await conn.fetchrow("""
                SELECT * FROM user_profiles WHERE id = $1
            """, str(profile_id))

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            # Get identifiers
            identifiers = await manager.get_profile_identifiers(str(profile_id))

            # Get behaviors
            behaviors = await conn.fetch("""
                SELECT * FROM behavioral_tracking
                WHERE profile_id = $1
                ORDER BY timestamp DESC
                LIMIT 100
            """, str(profile_id))

            return {
                "success": True,
                "profile": dict(profile),
                "identifiers": identifiers,
                "behaviors": [dict(b) for b in behaviors]
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Geographic Targeting Endpoints
# ============================================================================

@router.post("/local/discover")
async def discover_local_leads(
    request: LocalDiscoveryRequest,
    db_pool=Depends(get_db_pool)
):
    """Discover leads in specific geographic area."""
    geo_targeting = GeographicTargeting(db_pool)

    try:
        lead_ids = await geo_targeting.discover_local_leads(
            str(request.investigation_id),
            request.location,
            request.radius_km,
            request.criteria
        )

        return {
            "success": True,
            "location": request.location,
            "radius_km": request.radius_km,
            "leads_discovered": len(lead_ids),
            "lead_ids": lead_ids
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/local/market-analysis")
async def analyze_local_market(
    location: str,
    db_pool=Depends(get_db_pool)
):
    """Analyze local market for opportunities."""
    geo_targeting = GeographicTargeting(db_pool)

    try:
        analysis = await geo_targeting.analyze_local_market(location)

        return {
            "success": True,
            **analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Alert Endpoints
# ============================================================================

@router.get("/alerts")
async def list_alerts(
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db_pool=Depends(get_db_pool)
):
    """List alerts."""
    alert_system = LeadAlertSystem(db_pool)

    try:
        alerts = await alert_system.get_alerts(status, alert_type, priority, limit)

        return {
            "success": True,
            "count": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/summary")
async def get_alert_summary(db_pool=Depends(get_db_pool)):
    """Get alert summary statistics."""
    alert_system = LeadAlertSystem(db_pool)

    try:
        summary = await alert_system.get_alert_summary()

        return {
            "success": True,
            **summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: UUID, db_pool=Depends(get_db_pool)):
    """Mark alert as read."""
    alert_system = LeadAlertSystem(db_pool)

    try:
        success = await alert_system.mark_alert_read(str(alert_id))

        return {
            "success": success,
            "alert_id": str(alert_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Privacy & Configuration Endpoints
# ============================================================================

@router.get("/privacy/config")
async def get_privacy_configuration():
    """Get current privacy configuration."""
    privacy = get_privacy_config()

    return {
        "success": True,
        "config": privacy.to_dict()
    }


@router.get("/privacy/policy")
async def get_privacy_policy():
    """Get privacy policies."""
    privacy = get_privacy_config()

    return {
        "success": True,
        "mode": privacy.mode.value,
        "cookie_policy": privacy.get_cookie_policy(),
        "user_rights": privacy.get_user_rights(),
        "logging_policy": privacy.get_logging_policy(),
        "analytics_policy": privacy.get_analytics_policy()
    }


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.get("/analytics/overview")
async def get_analytics_overview(db_pool=Depends(get_db_pool)):
    """Get analytics overview."""
    try:
        async with db_pool.acquire() as conn:
            # Lead stats
            lead_stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_leads,
                    COUNT(*) FILTER (WHERE status = 'new') as new_leads,
                    COUNT(*) FILTER (WHERE status = 'qualified') as qualified_leads,
                    COUNT(*) FILTER (WHERE status = 'contacted') as contacted_leads,
                    COUNT(*) FILTER (WHERE status = 'converted') as converted_leads,
                    AVG(signal_strength) as avg_signal_strength,
                    AVG(intent_score) as avg_intent_score
                FROM discovered_leads
            """)

            # Match stats
            match_stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_matches,
                    AVG(match_score) as avg_match_score,
                    COUNT(*) FILTER (WHERE status = 'converted') as conversions
                FROM lead_service_matches
            """)

            # Tracking stats
            tracking_stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_profiles,
                    COUNT(DISTINCT investigation_id) as investigations
                FROM user_profiles
            """)

            return {
                "success": True,
                "lead_stats": dict(lead_stats),
                "match_stats": dict(match_stats),
                "tracking_stats": dict(tracking_stats)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
