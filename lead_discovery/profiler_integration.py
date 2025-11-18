"""
OSINT Profiler Integration

Integrates lead discovery with existing OSINT profiler.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncpg
from asyncpg.pool import Pool


class ProfilerIntegration:
    """
    Integration with OSINT profiler.

    Features:
    - Use profiler data for lead enrichment
    - Enhance lead profiles with OSINT data
    - Cross-reference profiler findings
    - Combine tracking data with profiler data
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def enrich_lead_with_profiler(
        self,
        lead_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich lead with profiler data.

        Args:
            lead_id: Lead UUID
            username: Optional username to profile
            email: Optional email to profile

        Returns:
            Enrichment results
        """
        enrichment_data = {}

        # Get lead data
        async with self.db_pool.acquire() as conn:
            lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, lead_id)

            if not lead:
                return {'error': 'Lead not found'}

            # Use lead's email if not provided
            email = email or lead['email']
            username = username or self._extract_username_from_email(email)

        # Get profiler data
        if username:
            profiler_data = await self.get_profiler_data(username)
            enrichment_data.update(profiler_data)

        # Get profiler data by email
        if email:
            email_data = await self.get_profiler_data_by_email(email)
            enrichment_data.update(email_data)

        # Merge with lead profile
        if enrichment_data:
            merged = await self.merge_profiles(
                dict(lead),
                enrichment_data
            )

            # Update lead with enriched data
            await self._update_lead_with_enrichment(lead_id, merged)

            return {
                'lead_id': lead_id,
                'enriched': True,
                'data_sources': list(enrichment_data.keys()),
                'enrichment_data': merged
            }

        return {
            'lead_id': lead_id,
            'enriched': False,
            'message': 'No profiler data found'
        }

    async def get_profiler_data(
        self,
        username: str
    ) -> Dict[str, Any]:
        """
        Get profiler data for username.

        Args:
            username: Username to profile

        Returns:
            Profiler data
        """
        async with self.db_pool.acquire() as conn:
            # Get profile from profiles table
            profile = await conn.fetchrow("""
                SELECT * FROM profiles
                WHERE username = $1
                ORDER BY created_at DESC
                LIMIT 1
            """, username)

            if not profile:
                return {}

            profile_dict = dict(profile)

            # Get social media accounts
            social_accounts = await conn.fetch("""
                SELECT * FROM social_media_accounts
                WHERE profile_id = $1
            """, profile['id'])

            # Get email accounts
            email_accounts = await conn.fetch("""
                SELECT * FROM email_accounts
                WHERE profile_id = $1
            """, profile['id'])

            # Get phone numbers
            phone_numbers = await conn.fetch("""
                SELECT * FROM phone_numbers
                WHERE profile_id = $1
            """, profile['id'])

            return {
                'profile': profile_dict,
                'social_accounts': [dict(s) for s in social_accounts],
                'email_accounts': [dict(e) for e in email_accounts],
                'phone_numbers': [dict(p) for p in phone_numbers]
            }

    async def get_profiler_data_by_email(
        self,
        email: str
    ) -> Dict[str, Any]:
        """
        Get profiler data by email.

        Args:
            email: Email address

        Returns:
            Profiler data
        """
        async with self.db_pool.acquire() as conn:
            # Find profile by email
            email_account = await conn.fetchrow("""
                SELECT * FROM email_accounts
                WHERE email = $1
                LIMIT 1
            """, email)

            if not email_account:
                return {}

            # Get associated profile
            profile = await conn.fetchrow("""
                SELECT * FROM profiles
                WHERE id = $1
            """, email_account['profile_id'])

            if not profile:
                return {}

            # Get full profiler data
            return await self.get_profiler_data(profile['username'])

    async def merge_profiles(
        self,
        lead_profile: Dict[str, Any],
        profiler_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge lead profile with profiler data.

        Args:
            lead_profile: Lead profile data
            profiler_data: Profiler data

        Returns:
            Merged profile
        """
        merged = lead_profile.copy()

        # Extract from profiler data
        if 'profile' in profiler_data:
            prof = profiler_data['profile']

            # Update fields if not already set
            merged['name'] = merged.get('name') or prof.get('full_name')
            merged['company'] = merged.get('company') or prof.get('company')
            merged['location'] = merged.get('location') or prof.get('location')
            merged['industry'] = merged.get('industry') or prof.get('industry')

        # Add social media links
        if 'social_accounts' in profiler_data:
            social_links = [s.get('profile_url') for s in profiler_data['social_accounts']
                          if s.get('profile_url')]
            merged['social_media_links'] = social_links

        # Add additional emails
        if 'email_accounts' in profiler_data:
            emails = [e.get('email') for e in profiler_data['email_accounts']
                     if e.get('email')]
            if emails:
                merged['additional_emails'] = emails

        # Add phone numbers
        if 'phone_numbers' in profiler_data:
            phones = [p.get('number') for p in profiler_data['phone_numbers']
                     if p.get('number')]
            if phones:
                merged['additional_phones'] = phones

        return merged

    async def cross_reference_findings(
        self,
        lead_id: str,
        investigation_id: str
    ) -> Dict[str, Any]:
        """
        Cross-reference lead with investigation findings.

        Args:
            lead_id: Lead UUID
            investigation_id: Investigation UUID

        Returns:
            Cross-reference results
        """
        async with self.db_pool.acquire() as conn:
            # Get lead
            lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, lead_id)

            if not lead:
                return {'error': 'Lead not found'}

            # Find matching profiles in investigation
            matches = []

            if lead['email']:
                email_matches = await conn.fetch("""
                    SELECT p.*, ea.email
                    FROM profiles p
                    JOIN email_accounts ea ON ea.profile_id = p.id
                    WHERE p.investigation_id = $1 AND ea.email = $2
                """, investigation_id, lead['email'])
                matches.extend([dict(m) for m in email_matches])

            if lead['phone']:
                phone_matches = await conn.fetch("""
                    SELECT p.*, pn.number
                    FROM profiles p
                    JOIN phone_numbers pn ON pn.profile_id = p.id
                    WHERE p.investigation_id = $1 AND pn.number = $2
                """, investigation_id, lead['phone'])
                matches.extend([dict(m) for m in phone_matches])

            return {
                'lead_id': lead_id,
                'investigation_id': investigation_id,
                'matches_found': len(matches),
                'matches': matches
            }

    async def create_investigation_from_lead(
        self,
        lead_id: str,
        investigation_name: Optional[str] = None
    ) -> str:
        """
        Create OSINT investigation from lead.

        Args:
            lead_id: Lead UUID
            investigation_name: Optional investigation name

        Returns:
            Investigation ID
        """
        async with self.db_pool.acquire() as conn:
            # Get lead
            lead = await conn.fetchrow("""
                SELECT * FROM discovered_leads WHERE id = $1
            """, lead_id)

            if not lead:
                raise ValueError('Lead not found')

            # Create investigation
            name = investigation_name or f"Lead Investigation: {lead['name'] or lead['company']}"

            inv_id = await conn.fetchval("""
                INSERT INTO investigations (name, description, status, created_at)
                VALUES ($1, $2, 'active', NOW())
                RETURNING id
            """, name, f"Investigation created from lead {lead_id}")

            # Create initial profile if we have username or email
            if lead['email']:
                username = self._extract_username_from_email(lead['email'])

                await conn.execute("""
                    INSERT INTO profiles (
                        investigation_id,
                        username,
                        full_name,
                        company,
                        location,
                        industry
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, inv_id, username, lead['name'], lead['company'],
                    lead['location'], lead['industry'])

            # Link lead to investigation
            await conn.execute("""
                UPDATE discovered_leads
                SET investigation_id = $1
                WHERE id = $2
            """, inv_id, lead_id)

            return str(inv_id)

    async def _update_lead_with_enrichment(
        self,
        lead_id: str,
        enrichment_data: Dict[str, Any]
    ) -> bool:
        """Update lead with enrichment data."""
        async with self.db_pool.acquire() as conn:
            # Build update
            updates = []
            values = []
            param_count = 1

            field_mapping = {
                'name': 'name',
                'company': 'company',
                'location': 'location',
                'industry': 'industry',
            }

            for enrich_field, db_field in field_mapping.items():
                if enrichment_data.get(enrich_field):
                    updates.append(f"{db_field} = COALESCE({db_field}, ${param_count})")
                    values.append(enrichment_data[enrich_field])
                    param_count += 1

            if not updates:
                return False

            # Add metadata
            updates.append(f"metadata = COALESCE(metadata, '{{}}'::jsonb) || ${param_count}::jsonb")
            values.append(json.dumps({
                'enriched': True,
                'enriched_at': datetime.now().isoformat(),
                'enrichment_source': 'profiler'
            }))
            param_count += 1

            updates.append("updated_at = NOW()")

            # Add lead_id
            values.append(lead_id)

            query = f"""
                UPDATE discovered_leads
                SET {', '.join(updates)}
                WHERE id = ${param_count}
            """

            await conn.execute(query, *values)
            return True

    def _extract_username_from_email(self, email: Optional[str]) -> Optional[str]:
        """Extract username from email address."""
        if not email:
            return None

        return email.split('@')[0] if '@' in email else email
