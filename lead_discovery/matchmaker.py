"""
Lead Matchmaking System

Matches discovered leads with appropriate services/products.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncpg
from asyncpg.pool import Pool

from .matching_algorithm import MatchingAlgorithm


class LeadMatchmaker:
    """
    Matchmaking system for leads and services.

    Features:
    - Lead-to-service matching
    - Match scoring algorithm
    - Recommendation engine
    - Priority ranking
    - Geographic matching
    - Industry matching
    - Need-based matching
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool
        self.algorithm = MatchingAlgorithm()

    async def match_lead_to_services(
        self,
        lead_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Match lead to appropriate services/products.

        Args:
            lead_id: Lead UUID
            limit: Maximum number of matches to return

        Returns:
            List of service matches with scores
        """
        async with self.db_pool.acquire() as conn:
            # Get lead data
            lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, lead_id)

            if not lead:
                return []

            # Get all active services
            services = await conn.fetch("""
                SELECT * FROM services_catalog WHERE is_active = TRUE
            """)

            # Calculate match scores for all services
            matches = []
            for service in services:
                match_data = await self.calculate_match_score(
                    dict(lead),
                    dict(service)
                )

                if match_data['match_score'] > 0:
                    matches.append({
                        'service_id': str(service['id']),
                        'service_name': service['service_name'],
                        'service_type': service['service_type'],
                        **match_data
                    })

            # Sort by match score
            matches.sort(key=lambda x: x['match_score'], reverse=True)

            # Limit results
            top_matches = matches[:limit]

            # Store matches in database
            for match in top_matches:
                await self._store_match(lead_id, match)

            return top_matches

    async def calculate_match_score(
        self,
        lead: Dict[str, Any],
        service: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate match score between lead and service.

        Args:
            lead: Lead data
            service: Service data
            weights: Custom scoring weights

        Returns:
            Match data with scores and reasons
        """
        return self.algorithm.calculate_match_score(lead, service, weights)

    async def recommend_services(
        self,
        lead_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend top services for lead.

        Args:
            lead_id: Lead UUID
            limit: Number of recommendations

        Returns:
            List of recommended services
        """
        # Get existing matches or create new ones
        async with self.db_pool.acquire() as conn:
            existing_matches = await conn.fetch("""
                SELECT lsm.*, sc.service_name, sc.service_type, sc.description
                FROM lead_service_matches lsm
                JOIN services_catalog sc ON sc.id = lsm.service_id
                WHERE lsm.lead_id = $1
                ORDER BY lsm.match_score DESC
                LIMIT $2
            """, lead_id, limit)

            if existing_matches:
                return [dict(match) for match in existing_matches]

        # Create new matches
        matches = await self.match_lead_to_services(lead_id, limit)
        return matches

    async def rank_leads(
        self,
        service_id: str,
        criteria: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Rank leads for a specific service.

        Args:
            service_id: Service UUID
            criteria: Additional filtering criteria
            limit: Maximum leads to return

        Returns:
            List of ranked leads
        """
        async with self.db_pool.acquire() as conn:
            # Get service
            service = await conn.fetchrow("""
                SELECT * FROM services_catalog WHERE id = $1
            """, service_id)

            if not service:
                return []

            # Build query based on criteria
            query = """
                SELECT l.*, lsm.match_score, lsm.status as match_status
                FROM discovered_leads l
                LEFT JOIN lead_service_matches lsm ON lsm.lead_id = l.id AND lsm.service_id = $1
                WHERE l.status != 'lost' AND l.status != 'invalid'
            """
            params = [service_id]
            param_count = 2

            # Apply criteria filters
            if criteria:
                if criteria.get('min_match_score'):
                    query += f" AND (lsm.match_score >= ${param_count} OR lsm.match_score IS NULL)"
                    params.append(criteria['min_match_score'])
                    param_count += 1

                if criteria.get('location'):
                    query += f" AND (l.city ILIKE ${param_count} OR l.state ILIKE ${param_count})"
                    params.append(f"%{criteria['location']}%")
                    param_count += 1

                if criteria.get('industry'):
                    query += f" AND l.industry ILIKE ${param_count}"
                    params.append(f"%{criteria['industry']}%")
                    param_count += 1

            query += " ORDER BY lsm.match_score DESC NULLS LAST, l.intent_score DESC, l.signal_strength DESC"
            query += f" LIMIT ${param_count}"
            params.append(limit)

            leads = await conn.fetch(query, *params)

            # Calculate match scores for leads without existing matches
            ranked_leads = []
            for lead in leads:
                lead_dict = dict(lead)

                if lead_dict.get('match_score') is None:
                    # Calculate match score
                    match_data = await self.calculate_match_score(
                        lead_dict,
                        dict(service)
                    )
                    lead_dict['match_score'] = match_data['match_score']
                    lead_dict['match_reasons'] = match_data['reasons']

                    # Store match
                    await self._store_match(str(lead['id']), {
                        'service_id': service_id,
                        **match_data
                    })

                ranked_leads.append(lead_dict)

            # Sort by match score
            ranked_leads.sort(key=lambda x: x.get('match_score', 0), reverse=True)

            return ranked_leads

    async def find_similar_leads(
        self,
        lead_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar leads for clustering.

        Args:
            lead_id: Lead UUID
            limit: Maximum similar leads to return

        Returns:
            List of similar leads
        """
        async with self.db_pool.acquire() as conn:
            # Get reference lead
            ref_lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, lead_id)

            if not ref_lead:
                return []

            # Find leads with similar attributes
            similar = await conn.fetch("""
                SELECT *,
                       (CASE WHEN industry = $2 THEN 30 ELSE 0 END) +
                       (CASE WHEN city = $3 THEN 20 ELSE 0 END) +
                       (CASE WHEN state = $4 THEN 10 ELSE 0 END) +
                       (CASE WHEN lead_category = $5 THEN 25 ELSE 0 END) +
                       (CASE WHEN company_size = $6 THEN 15 ELSE 0 END) as similarity_score
                FROM discovered_leads
                WHERE id != $1
                  AND status != 'lost'
                  AND status != 'invalid'
                ORDER BY similarity_score DESC, signal_strength DESC
                LIMIT $7
            """, lead_id, ref_lead['industry'], ref_lead['city'],
                ref_lead['state'], ref_lead['lead_category'],
                ref_lead['company_size'], limit)

            return [dict(lead) for lead in similar if lead['similarity_score'] > 0]

    async def match_by_location(
        self,
        service_id: str,
        location: str,
        radius_km: float = 50
    ) -> List[Dict[str, Any]]:
        """
        Match leads by geographic location.

        Args:
            service_id: Service UUID
            location: Location string
            radius_km: Search radius

        Returns:
            List of matched leads
        """
        # Parse location
        location_parts = location.split(',')
        city = location_parts[0].strip() if location_parts else None
        state = location_parts[1].strip() if len(location_parts) > 1 else None

        async with self.db_pool.acquire() as conn:
            query = """
                SELECT l.*, lsm.match_score
                FROM discovered_leads l
                LEFT JOIN lead_service_matches lsm ON lsm.lead_id = l.id AND lsm.service_id = $1
                WHERE l.status != 'lost' AND l.status != 'invalid'
            """
            params = [service_id]
            param_count = 2

            if city:
                query += f" AND l.city ILIKE ${param_count}"
                params.append(f"%{city}%")
                param_count += 1

            if state:
                query += f" AND l.state ILIKE ${param_count}"
                params.append(f"%{state}%")
                param_count += 1

            query += " ORDER BY lsm.match_score DESC NULLS LAST, l.signal_strength DESC"
            query += " LIMIT 100"

            leads = await conn.fetch(query, *params)
            return [dict(lead) for lead in leads]

    async def match_by_industry(
        self,
        service_id: str,
        industry: str
    ) -> List[Dict[str, Any]]:
        """
        Match leads by industry.

        Args:
            service_id: Service UUID
            industry: Industry name

        Returns:
            List of matched leads
        """
        async with self.db_pool.acquire() as conn:
            leads = await conn.fetch("""
                SELECT l.*, lsm.match_score
                FROM discovered_leads l
                LEFT JOIN lead_service_matches lsm ON lsm.lead_id = l.id AND lsm.service_id = $1
                WHERE l.industry ILIKE $2
                  AND l.status != 'lost'
                  AND l.status != 'invalid'
                ORDER BY lsm.match_score DESC NULLS LAST, l.signal_strength DESC
                LIMIT 100
            """, service_id, f"%{industry}%")

            return [dict(lead) for lead in leads]

    async def match_by_need(
        self,
        service_id: str,
        needs: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Match leads by identified needs.

        Args:
            service_id: Service UUID
            needs: List of needs

        Returns:
            List of matched leads
        """
        async with self.db_pool.acquire() as conn:
            leads = await conn.fetch("""
                SELECT l.*, lsm.match_score
                FROM discovered_leads l
                LEFT JOIN lead_service_matches lsm ON lsm.lead_id = l.id AND lsm.service_id = $1
                WHERE l.needs_identified && $2::text[]
                  AND l.status != 'lost'
                  AND l.status != 'invalid'
                ORDER BY lsm.match_score DESC NULLS LAST, l.signal_strength DESC
                LIMIT 100
            """, service_id, needs)

            return [dict(lead) for lead in leads]

    async def update_match_status(
        self,
        match_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update match status.

        Args:
            match_id: Match UUID
            status: New status
            notes: Optional notes

        Returns:
            Success status
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE lead_service_matches
                SET status = $1,
                    notes = COALESCE($2, notes),
                    updated_at = NOW()
                WHERE id = $3
            """, status, notes, match_id)

            # Log to history
            await conn.execute("""
                INSERT INTO match_history (match_id, event_type, notes)
                VALUES ($1, $2, $3)
            """, match_id, f"status_changed_{status}", notes)

            return True

    async def get_match_analytics(
        self,
        service_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get matchmaking analytics.

        Args:
            service_id: Optional service UUID to filter by

        Returns:
            Analytics data
        """
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT
                    COUNT(*) as total_matches,
                    AVG(match_score) as avg_match_score,
                    COUNT(CASE WHEN status = 'contacted' THEN 1 END) as contacted_count,
                    COUNT(CASE WHEN status = 'interested' THEN 1 END) as interested_count,
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_count,
                    COUNT(CASE WHEN match_score >= 80 THEN 1 END) as high_score_matches,
                    COUNT(CASE WHEN match_score >= 60 AND match_score < 80 THEN 1 END) as medium_score_matches,
                    COUNT(CASE WHEN match_score < 60 THEN 1 END) as low_score_matches
                FROM lead_service_matches
            """

            if service_id:
                query += " WHERE service_id = $1"
                result = await conn.fetchrow(query, service_id)
            else:
                result = await conn.fetchrow(query)

            return dict(result) if result else {}

    async def _store_match(
        self,
        lead_id: str,
        match_data: Dict[str, Any]
    ) -> str:
        """Store match in database."""
        async with self.db_pool.acquire() as conn:
            # Check if match already exists
            existing = await conn.fetchval("""
                SELECT id FROM lead_service_matches
                WHERE lead_id = $1 AND service_id = $2
            """, lead_id, match_data['service_id'])

            if existing:
                # Update existing match
                await conn.execute("""
                    UPDATE lead_service_matches
                    SET match_score = $1,
                        geographic_score = $2,
                        industry_score = $3,
                        need_score = $4,
                        profile_score = $5,
                        behavioral_score = $6,
                        match_reasons = $7,
                        confidence_level = $8,
                        updated_at = NOW()
                    WHERE id = $9
                """, match_data['match_score'],
                    match_data['geographic_score'],
                    match_data['industry_score'],
                    match_data['need_score'],
                    match_data['profile_score'],
                    match_data['behavioral_score'],
                    match_data['reasons'],
                    match_data['confidence_level'],
                    existing)
                return str(existing)

            # Create new match
            match_id = await conn.fetchval("""
                INSERT INTO lead_service_matches (
                    lead_id,
                    service_id,
                    match_score,
                    geographic_score,
                    industry_score,
                    need_score,
                    profile_score,
                    behavioral_score,
                    match_reasons,
                    confidence_level,
                    priority
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            """, lead_id,
                match_data['service_id'],
                match_data['match_score'],
                match_data['geographic_score'],
                match_data['industry_score'],
                match_data['need_score'],
                match_data['profile_score'],
                match_data['behavioral_score'],
                match_data['reasons'],
                match_data['confidence_level'],
                match_data.get('priority', 'medium'))

            # Log to history
            await conn.execute("""
                INSERT INTO match_history (match_id, event_type, event_data)
                VALUES ($1, 'matched', $2)
            """, match_id, json.dumps({'match_score': match_data['match_score']}))

            return str(match_id)
