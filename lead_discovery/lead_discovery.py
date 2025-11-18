"""
Lead Discovery Engine

Discovers potential leads through scraping, crawling, and signal detection.
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
import asyncpg
from asyncpg.pool import Pool

from .signal_detector import LeadSignalDetector


class LeadDiscoveryEngine:
    """
    Lead discovery through scraping and signal detection.

    Capabilities:
    - Target website discovery
    - Content scraping for lead signals
    - Form detection and analysis
    - Search query analysis
    - Business listing analysis
    - Local directory scraping
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool
        self.signal_detector = LeadSignalDetector()

    async def discover_leads(
        self,
        investigation_id: str,
        criteria: Dict[str, Any]
    ) -> List[str]:
        """
        Discover potential leads based on criteria.

        Args:
            investigation_id: Investigation UUID
            criteria: Discovery criteria
                - geographic_area: Location to search
                - industry: Target industry
                - company_size: Target company size
                - service_needs: Service type needed

        Returns:
            List of discovered lead IDs
        """
        discovered_leads = []

        # Discover from different sources
        if criteria.get('geographic_area'):
            local_leads = await self.discover_local_leads(
                investigation_id,
                criteria['geographic_area'],
                criteria.get('radius_km', 50)
            )
            discovered_leads.extend(local_leads)

        if criteria.get('industry'):
            industry_leads = await self.discover_by_industry(
                investigation_id,
                criteria['industry']
            )
            discovered_leads.extend(industry_leads)

        if criteria.get('keywords'):
            keyword_leads = await self.discover_by_keywords(
                investigation_id,
                criteria['keywords']
            )
            discovered_leads.extend(keyword_leads)

        return discovered_leads

    async def scrape_for_signals(
        self,
        url: str,
        signal_types: List[str],
        investigation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape website for lead signals.

        Args:
            url: Target URL
            signal_types: Types of signals to detect
            investigation_id: Investigation UUID

        Returns:
            Dict with signals and lead data
        """
        # In production, this would use actual web scraping
        # For now, return structure for testing

        result = {
            'url': url,
            'signals': [],
            'lead_data': {},
            'forms': [],
            'contact_info': {}
        }

        # Placeholder for actual scraping logic
        # Would use libraries like playwright, selenium, or beautifulsoup

        return result

    async def detect_loan_signals(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect signals indicating need for loan.

        Args:
            content: Page content
            metadata: Additional metadata

        Returns:
            List of detected signals
        """
        return self.signal_detector.detect_loan_signals(content, metadata or {})

    async def detect_consulting_signals(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect signals indicating need for consulting.

        Args:
            content: Page content
            metadata: Additional metadata

        Returns:
            List of detected signals
        """
        return self.signal_detector.detect_consulting_signals(content, metadata or {})

    async def analyze_forms(
        self,
        forms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze forms for lead information.

        Args:
            forms: List of form data

        Returns:
            Analysis results
        """
        analysis = {
            'contact_forms': [],
            'quote_forms': [],
            'application_forms': [],
            'newsletter_forms': [],
            'lead_capture_forms': []
        }

        for form in forms:
            form_type = self._classify_form(form)
            if form_type:
                analysis[form_type].append(form)

        return analysis

    async def discover_local_leads(
        self,
        investigation_id: str,
        location: str,
        radius_km: float = 50
    ) -> List[str]:
        """
        Discover leads in specific geographic area.

        Args:
            investigation_id: Investigation UUID
            location: Location string (city, state, zip)
            radius_km: Search radius in kilometers

        Returns:
            List of lead IDs
        """
        # Parse location
        location_parts = self._parse_location(location)

        # Query local businesses
        async with self.db_pool.acquire() as conn:
            businesses = await conn.fetch("""
                SELECT * FROM local_businesses
                WHERE city = $1 OR state = $2 OR postal_code = $3
                LIMIT 100
            """, location_parts.get('city'),
                location_parts.get('state'),
                location_parts.get('postal_code'))

            lead_ids = []
            for business in businesses:
                # Create lead from business data
                lead_id = await self._create_lead_from_business(
                    investigation_id,
                    dict(business)
                )
                if lead_id:
                    lead_ids.append(lead_id)

            return lead_ids

    async def discover_by_industry(
        self,
        investigation_id: str,
        industry: str
    ) -> List[str]:
        """
        Discover leads by industry.

        Args:
            investigation_id: Investigation UUID
            industry: Industry name

        Returns:
            List of lead IDs
        """
        async with self.db_pool.acquire() as conn:
            businesses = await conn.fetch("""
                SELECT * FROM local_businesses
                WHERE industry ILIKE $1
                LIMIT 100
            """, f"%{industry}%")

            lead_ids = []
            for business in businesses:
                lead_id = await self._create_lead_from_business(
                    investigation_id,
                    dict(business)
                )
                if lead_id:
                    lead_ids.append(lead_id)

            return lead_ids

    async def discover_by_keywords(
        self,
        investigation_id: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Discover leads by keywords.

        Args:
            investigation_id: Investigation UUID
            keywords: Search keywords

        Returns:
            List of lead IDs
        """
        # In production, this would search various sources
        # For now, return empty list
        return []

    async def create_lead(
        self,
        investigation_id: str,
        lead_data: Dict[str, Any],
        signals: Optional[List[Dict]] = None
    ) -> str:
        """
        Create a discovered lead.

        Args:
            investigation_id: Investigation UUID
            lead_data: Lead information
            signals: Detected signals

        Returns:
            Lead ID
        """
        # Calculate signal strength
        signal_strength = 0
        if signals:
            signal_strength = sum(s.get('strength', 0) for s in signals) // len(signals)

        # Calculate intent score
        intent_score = self._calculate_intent_score(signals or [])

        # Extract needs
        needs = self._extract_needs(signals or [])

        async with self.db_pool.acquire() as conn:
            lead_id = await conn.fetchval("""
                INSERT INTO discovered_leads (
                    investigation_id,
                    lead_type,
                    lead_category,
                    name,
                    email,
                    phone,
                    company,
                    website,
                    location,
                    city,
                    state,
                    country,
                    postal_code,
                    industry,
                    company_size,
                    lead_source,
                    source_url,
                    signal_strength,
                    signals_detected,
                    needs_identified,
                    intent_score,
                    status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                RETURNING id
            """, investigation_id,
                lead_data.get('lead_type', 'unknown'),
                lead_data.get('lead_category'),
                lead_data.get('name'),
                lead_data.get('email'),
                lead_data.get('phone'),
                lead_data.get('company'),
                lead_data.get('website'),
                lead_data.get('location'),
                lead_data.get('city'),
                lead_data.get('state'),
                lead_data.get('country'),
                lead_data.get('postal_code'),
                lead_data.get('industry'),
                lead_data.get('company_size'),
                lead_data.get('lead_source', 'manual'),
                lead_data.get('source_url'),
                signal_strength,
                json.dumps(signals or []),
                needs,
                intent_score,
                'new')

            # Store individual signals
            if signals:
                for signal in signals:
                    await conn.execute("""
                        INSERT INTO lead_signals (
                            lead_id,
                            signal_type,
                            signal_category,
                            signal_source,
                            signal_content,
                            signal_strength,
                            confidence
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, lead_id,
                        signal.get('type'),
                        signal.get('category'),
                        signal.get('source'),
                        signal.get('content'),
                        signal.get('strength', 0),
                        signal.get('confidence', 0))

            return str(lead_id)

    async def enrich_lead(
        self,
        lead_id: str,
        enrichment_data: Dict[str, Any]
    ) -> bool:
        """
        Enrich lead with additional data.

        Args:
            lead_id: Lead UUID
            enrichment_data: Data to add to lead

        Returns:
            Success status
        """
        async with self.db_pool.acquire() as conn:
            # Build update query dynamically
            update_fields = []
            values = []
            param_count = 1

            for key, value in enrichment_data.items():
                if key in ['email', 'phone', 'company', 'website', 'industry',
                          'company_size', 'revenue_range', 'employee_count']:
                    update_fields.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1

            if not update_fields:
                return False

            update_fields.append(f"updated_at = NOW()")
            values.append(lead_id)

            query = f"""
                UPDATE discovered_leads
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
            """

            await conn.execute(query, *values)
            return True

    def _classify_form(self, form: Dict[str, Any]) -> Optional[str]:
        """Classify form type based on fields."""
        fields = [f.get('name', '').lower() for f in form.get('fields', [])]

        if any(f in fields for f in ['email', 'name', 'message']):
            return 'contact_forms'
        if any(f in fields for f in ['quote', 'budget', 'project']):
            return 'quote_forms'
        if any(f in fields for f in ['application', 'loan', 'amount']):
            return 'application_forms'
        if 'email' in fields and len(fields) <= 2:
            return 'newsletter_forms'

        return 'lead_capture_forms'

    def _parse_location(self, location: str) -> Dict[str, str]:
        """Parse location string into components."""
        parts = [p.strip() for p in location.split(',')]

        result = {}
        if len(parts) >= 1:
            result['city'] = parts[0]
        if len(parts) >= 2:
            result['state'] = parts[1]
        if len(parts) >= 3:
            result['country'] = parts[2]

        # Check if last part is zip code
        if parts and re.match(r'^\d{5}(-\d{4})?$', parts[-1]):
            result['postal_code'] = parts[-1]

        return result

    def _calculate_intent_score(self, signals: List[Dict]) -> int:
        """Calculate intent score from signals."""
        if not signals:
            return 0

        # Weight different signal types
        weights = {
            'loan_need': 1.5,
            'consulting_need': 1.3,
            'financial_distress': 1.8,
            'growth': 1.2,
            'expansion': 1.4
        }

        total_score = 0
        for signal in signals:
            signal_type = signal.get('type', '')
            strength = signal.get('strength', 0)
            weight = weights.get(signal_type, 1.0)
            total_score += strength * weight

        # Normalize to 0-100
        max_possible = len(signals) * 100 * 1.8  # Max weight is 1.8
        if max_possible > 0:
            return min(100, int((total_score / max_possible) * 100))

        return 0

    def _extract_needs(self, signals: List[Dict]) -> List[str]:
        """Extract identified needs from signals."""
        needs = set()

        for signal in signals:
            signal_type = signal.get('type', '')
            if signal_type == 'loan_need':
                needs.add('business_loan')
            elif signal_type == 'consulting_need':
                needs.add('business_consulting')
            elif signal_type == 'financial_distress':
                needs.add('financial_assistance')
            elif signal_type == 'growth':
                needs.add('growth_capital')
            elif signal_type == 'expansion':
                needs.add('expansion_financing')

        return list(needs)

    async def _create_lead_from_business(
        self,
        investigation_id: str,
        business_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create lead from business data."""
        lead_data = {
            'lead_type': 'business',
            'name': business_data.get('business_name'),
            'company': business_data.get('business_name'),
            'phone': business_data.get('phone'),
            'email': business_data.get('email'),
            'website': business_data.get('website'),
            'location': business_data.get('address'),
            'city': business_data.get('city'),
            'state': business_data.get('state'),
            'postal_code': business_data.get('postal_code'),
            'industry': business_data.get('industry'),
            'lead_source': business_data.get('source', 'local_directory'),
            'source_url': business_data.get('source_url')
        }

        try:
            return await self.create_lead(investigation_id, lead_data)
        except Exception as e:
            print(f"Error creating lead from business: {e}")
            return None
