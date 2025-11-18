"""
Geographic Targeting System

Location-based lead discovery and targeting.
"""

import re
import json
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncpg
from asyncpg.pool import Pool


class GeographicTargeting:
    """
    Geographic targeting system.

    Features:
    - Location-based discovery
    - Radius-based search
    - Local directory scraping
    - Regional business listings
    - City/state targeting
    - ZIP code targeting
    - Proximity calculation
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def discover_local_leads(
        self,
        investigation_id: str,
        location: str,
        radius_km: float,
        criteria: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Discover leads in specific geographic area.

        Args:
            investigation_id: Investigation UUID
            location: Location string (city, state or lat,lng)
            radius_km: Search radius in kilometers
            criteria: Additional discovery criteria

        Returns:
            List of lead IDs
        """
        criteria = criteria or {}

        # Parse location
        location_data = self._parse_location(location)

        if not location_data:
            return []

        # Get local businesses
        businesses = await self._find_local_businesses(
            location_data,
            radius_km,
            criteria.get('industry'),
            criteria.get('business_type')
        )

        # Create leads from businesses
        lead_ids = []
        for business in businesses:
            try:
                lead_id = await self._create_lead_from_business(
                    investigation_id,
                    business,
                    criteria
                )
                if lead_id:
                    lead_ids.append(lead_id)
            except Exception as e:
                print(f"Error creating lead from business: {e}")
                continue

        return lead_ids

    async def scrape_local_directories(
        self,
        location: str,
        investigation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape local business directories.

        Args:
            location: Location string
            investigation_id: Investigation UUID

        Returns:
            List of discovered businesses
        """
        # In production, this would scrape:
        # - Google Maps/Places
        # - Yelp
        # - Yellow Pages
        # - Chamber of Commerce
        # - Local directories

        businesses = []

        # Query existing local businesses
        location_data = self._parse_location(location)
        if location_data:
            existing = await self._find_local_businesses(
                location_data,
                radius_km=50
            )
            businesses.extend(existing)

        return businesses

    async def find_nearby_businesses(
        self,
        location: str,
        radius_km: float,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find businesses in radius.

        Args:
            location: Center location
            radius_km: Search radius
            industry: Optional industry filter

        Returns:
            List of businesses
        """
        location_data = self._parse_location(location)
        if not location_data:
            return []

        return await self._find_local_businesses(
            location_data,
            radius_km,
            industry
        )

    async def analyze_local_market(
        self,
        location: str
    ) -> Dict[str, Any]:
        """
        Analyze local market for opportunities.

        Args:
            location: Location string

        Returns:
            Market analysis data
        """
        location_data = self._parse_location(location)

        async with self.db_pool.acquire() as conn:
            # Get business count by industry
            industry_breakdown = await conn.fetch("""
                SELECT industry, COUNT(*) as count
                FROM local_businesses
                WHERE city = $1 OR state = $2
                GROUP BY industry
                ORDER BY count DESC
                LIMIT 20
            """, location_data.get('city'), location_data.get('state'))

            # Get total businesses
            total_businesses = await conn.fetchval("""
                SELECT COUNT(*)
                FROM local_businesses
                WHERE city = $1 OR state = $2
            """, location_data.get('city'), location_data.get('state'))

            # Get leads in area
            total_leads = await conn.fetchval("""
                SELECT COUNT(*)
                FROM discovered_leads
                WHERE city = $1 OR state = $2
            """, location_data.get('city'), location_data.get('state'))

            return {
                'location': location,
                'total_businesses': total_businesses,
                'total_leads': total_leads,
                'industry_breakdown': [dict(row) for row in industry_breakdown],
                'analyzed_at': datetime.now().isoformat()
            }

    async def add_local_business(
        self,
        business_data: Dict[str, Any]
    ) -> str:
        """
        Add local business to database.

        Args:
            business_data: Business information

        Returns:
            Business ID
        """
        async with self.db_pool.acquire() as conn:
            business_id = await conn.fetchval("""
                INSERT INTO local_businesses (
                    business_name,
                    business_type,
                    industry,
                    address,
                    city,
                    state,
                    country,
                    postal_code,
                    latitude,
                    longitude,
                    phone,
                    email,
                    website,
                    rating,
                    review_count,
                    business_hours,
                    source,
                    source_url,
                    metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                RETURNING id
            """, business_data.get('business_name'),
                business_data.get('business_type'),
                business_data.get('industry'),
                business_data.get('address'),
                business_data.get('city'),
                business_data.get('state'),
                business_data.get('country', 'US'),
                business_data.get('postal_code'),
                business_data.get('latitude'),
                business_data.get('longitude'),
                business_data.get('phone'),
                business_data.get('email'),
                business_data.get('website'),
                business_data.get('rating'),
                business_data.get('review_count'),
                json.dumps(business_data.get('business_hours', {})),
                business_data.get('source', 'manual'),
                business_data.get('source_url'),
                json.dumps(business_data.get('metadata', {})))

            return str(business_id)

    async def get_businesses_by_zip(
        self,
        postal_code: str,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get businesses by ZIP code.

        Args:
            postal_code: ZIP/postal code
            industry: Optional industry filter

        Returns:
            List of businesses
        """
        async with self.db_pool.acquire() as conn:
            if industry:
                businesses = await conn.fetch("""
                    SELECT * FROM local_businesses
                    WHERE postal_code = $1 AND industry ILIKE $2
                    LIMIT 100
                """, postal_code, f"%{industry}%")
            else:
                businesses = await conn.fetch("""
                    SELECT * FROM local_businesses
                    WHERE postal_code = $1
                    LIMIT 100
                """, postal_code)

            return [dict(b) for b in businesses]

    async def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate

        Returns:
            Distance in kilometers
        """
        return self._haversine_distance(lat1, lon1, lat2, lon2)

    def _parse_location(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Parse location string into components.

        Supports:
        - "City, State"
        - "City, State, Country"
        - "ZIP Code"
        - "lat,lng"
        """
        if not location:
            return None

        # Check if lat,lng
        lat_lng_match = re.match(r'^(-?\d+\.\d+),\s*(-?\d+\.\d+)$', location.strip())
        if lat_lng_match:
            return {
                'latitude': float(lat_lng_match.group(1)),
                'longitude': float(lat_lng_match.group(2)),
                'type': 'coordinates'
            }

        # Check if ZIP code
        zip_match = re.match(r'^\d{5}(-\d{4})?$', location.strip())
        if zip_match:
            return {
                'postal_code': location.strip(),
                'type': 'zip'
            }

        # Parse city, state, country
        parts = [p.strip() for p in location.split(',')]

        result = {'type': 'text'}
        if len(parts) >= 1:
            result['city'] = parts[0]
        if len(parts) >= 2:
            result['state'] = parts[1]
        if len(parts) >= 3:
            result['country'] = parts[2]
        else:
            result['country'] = 'US'  # Default

        return result

    async def _find_local_businesses(
        self,
        location_data: Dict[str, Any],
        radius_km: float = 50,
        industry: Optional[str] = None,
        business_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find local businesses matching criteria."""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM local_businesses WHERE 1=1"
            params = []
            param_count = 1

            # Location filters
            if location_data.get('postal_code'):
                query += f" AND postal_code = ${param_count}"
                params.append(location_data['postal_code'])
                param_count += 1
            elif location_data.get('city'):
                query += f" AND city ILIKE ${param_count}"
                params.append(f"%{location_data['city']}%")
                param_count += 1

                if location_data.get('state'):
                    query += f" AND state ILIKE ${param_count}"
                    params.append(f"%{location_data['state']}%")
                    param_count += 1

            # Industry filter
            if industry:
                query += f" AND industry ILIKE ${param_count}"
                params.append(f"%{industry}%")
                param_count += 1

            # Business type filter
            if business_type:
                query += f" AND business_type ILIKE ${param_count}"
                params.append(f"%{business_type}%")
                param_count += 1

            query += " LIMIT 100"

            businesses = await conn.fetch(query, *params)
            return [dict(b) for b in businesses]

    async def _create_lead_from_business(
        self,
        investigation_id: str,
        business: Dict[str, Any],
        criteria: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create lead from business data."""
        from .lead_discovery import LeadDiscoveryEngine

        engine = LeadDiscoveryEngine(self.db_pool)

        lead_data = {
            'lead_type': 'business',
            'name': business.get('business_name'),
            'company': business.get('business_name'),
            'phone': business.get('phone'),
            'email': business.get('email'),
            'website': business.get('website'),
            'location': business.get('address'),
            'city': business.get('city'),
            'state': business.get('state'),
            'country': business.get('country'),
            'postal_code': business.get('postal_code'),
            'industry': business.get('industry'),
            'lead_source': business.get('source', 'local_directory'),
            'source_url': business.get('source_url'),
            'lead_category': criteria.get('lead_category') if criteria else None,
        }

        try:
            return await engine.create_lead(investigation_id, lead_data)
        except Exception as e:
            print(f"Error creating lead: {e}")
            return None

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between coordinates using Haversine formula."""
        R = 6371  # Earth's radius in kilometers

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        return R * c
