"""
Identifier Management System

Manages and organizes tracked identifiers.
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncpg
from asyncpg.pool import Pool


class IdentifierManager:
    """
    Centralized identifier management.

    Features:
    - Identifier storage and retrieval
    - Profile merging
    - Identifier linking
    - Duplicate detection
    - Data privacy controls
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def get_identifier(
        self,
        identifier_type: str,
        identifier_value: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get identifier by type and value.

        Args:
            identifier_type: Type of identifier
            identifier_value: Identifier value

        Returns:
            Identifier data or None
        """
        identifier_hash = self._hash_value(identifier_value)

        async with self.db_pool.acquire() as conn:
            identifier = await conn.fetchrow("""
                SELECT * FROM tracked_identifiers
                WHERE identifier_type = $1 AND identifier_hash = $2
            """, identifier_type, identifier_hash)

            if identifier:
                return dict(identifier)
            return None

    async def get_profile_identifiers(
        self,
        profile_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all identifiers for a profile.

        Args:
            profile_id: Profile UUID

        Returns:
            List of identifiers
        """
        async with self.db_pool.acquire() as conn:
            identifiers = await conn.fetch("""
                SELECT * FROM tracked_identifiers
                WHERE associated_profile_id = $1
                ORDER BY last_seen_at DESC
            """, profile_id)

            return [dict(i) for i in identifiers]

    async def merge_profiles(
        self,
        source_profile_id: str,
        target_profile_id: str
    ) -> bool:
        """
        Merge two user profiles.

        Args:
            source_profile_id: Source profile UUID (will be merged into target)
            target_profile_id: Target profile UUID

        Returns:
            Success status
        """
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Get source profile
                source = await conn.fetchrow("""
                    SELECT * FROM user_profiles WHERE id = $1
                """, source_profile_id)

                target = await conn.fetchrow("""
                    SELECT * FROM user_profiles WHERE id = $1
                """, target_profile_id)

                if not source or not target:
                    return False

                # Merge identifiers
                await conn.execute("""
                    UPDATE tracked_identifiers
                    SET associated_profile_id = $1
                    WHERE associated_profile_id = $2
                """, target_profile_id, source_profile_id)

                # Merge profile data
                merged_identifiers = list(set(
                    (target['identifiers'] or []) +
                    (source['identifiers'] or [])
                ))

                merged_sites = list(set(
                    (target['sites_visited'] or []) +
                    (source['sites_visited'] or [])
                ))

                merged_ips = list(set(
                    (target['ip_addresses'] or []) +
                    (source['ip_addresses'] or [])
                ))

                # Update target profile
                await conn.execute("""
                    UPDATE user_profiles
                    SET identifiers = $1,
                        sites_visited = $2,
                        ip_addresses = $3,
                        visit_count = visit_count + $4,
                        email = COALESCE(email, $5),
                        phone = COALESCE(phone, $6),
                        name = COALESCE(name, $7),
                        company = COALESCE(company, $8),
                        updated_at = NOW()
                    WHERE id = $9
                """, merged_identifiers, merged_sites, merged_ips,
                    source['visit_count'] or 0,
                    source['email'], source['phone'],
                    source['name'], source['company'],
                    target_profile_id)

                # Update behavioral tracking
                await conn.execute("""
                    UPDATE behavioral_tracking
                    SET profile_id = $1
                    WHERE profile_id = $2
                """, target_profile_id, source_profile_id)

                # Update cross-site tracking
                await conn.execute("""
                    UPDATE cross_site_tracking
                    SET profile_id = $1
                    WHERE profile_id = $2
                """, target_profile_id, source_profile_id)

                # Update leads
                await conn.execute("""
                    UPDATE discovered_leads
                    SET profile_id = $1
                    WHERE profile_id = $2
                """, target_profile_id, source_profile_id)

                # Delete source profile
                await conn.execute("""
                    DELETE FROM user_profiles WHERE id = $1
                """, source_profile_id)

                return True

    async def link_identifiers(
        self,
        identifier_ids: List[str],
        profile_id: Optional[str] = None
    ) -> str:
        """
        Link multiple identifiers to same profile.

        Args:
            identifier_ids: List of identifier UUIDs
            profile_id: Optional existing profile UUID

        Returns:
            Profile ID
        """
        if not identifier_ids:
            raise ValueError("No identifiers provided")

        async with self.db_pool.acquire() as conn:
            if profile_id:
                # Link to existing profile
                await conn.execute("""
                    UPDATE tracked_identifiers
                    SET associated_profile_id = $1
                    WHERE id = ANY($2::UUID[])
                """, profile_id, identifier_ids)

                # Update profile identifiers array
                await conn.execute("""
                    UPDATE user_profiles
                    SET identifiers = array_cat(identifiers, $1::UUID[]),
                        updated_at = NOW()
                    WHERE id = $2
                """, identifier_ids, profile_id)

                return profile_id

            else:
                # Create new profile
                from .cookie_tracker import CookieTracker
                tracker = CookieTracker(self.db_pool)
                return await tracker.build_user_profile(identifier_ids)

    async def find_duplicate_profiles(
        self,
        threshold: int = 2
    ) -> List[Tuple[str, str, int]]:
        """
        Find duplicate profiles based on shared identifiers.

        Args:
            threshold: Minimum shared identifiers to consider duplicates

        Returns:
            List of (profile1_id, profile2_id, shared_count) tuples
        """
        async with self.db_pool.acquire() as conn:
            duplicates = await conn.fetch("""
                WITH profile_pairs AS (
                    SELECT
                        ti1.associated_profile_id as profile1,
                        ti2.associated_profile_id as profile2,
                        COUNT(*) as shared_identifiers
                    FROM tracked_identifiers ti1
                    JOIN tracked_identifiers ti2
                        ON ti1.identifier_hash = ti2.identifier_hash
                        AND ti1.identifier_type = ti2.identifier_type
                        AND ti1.associated_profile_id < ti2.associated_profile_id
                    WHERE ti1.associated_profile_id IS NOT NULL
                      AND ti2.associated_profile_id IS NOT NULL
                    GROUP BY ti1.associated_profile_id, ti2.associated_profile_id
                    HAVING COUNT(*) >= $1
                )
                SELECT profile1, profile2, shared_identifiers
                FROM profile_pairs
                ORDER BY shared_identifiers DESC
            """, threshold)

            return [(str(d['profile1']), str(d['profile2']), d['shared_identifiers'])
                    for d in duplicates]

    async def delete_identifier(
        self,
        identifier_id: str
    ) -> bool:
        """
        Delete an identifier (GDPR compliance).

        Args:
            identifier_id: Identifier UUID

        Returns:
            Success status
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM tracked_identifiers WHERE id = $1
            """, identifier_id)
            return True

    async def anonymize_identifier(
        self,
        identifier_id: str
    ) -> bool:
        """
        Anonymize an identifier (keep hash, remove value).

        Args:
            identifier_id: Identifier UUID

        Returns:
            Success status
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE tracked_identifiers
                SET identifier_value = 'ANONYMIZED',
                    metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{anonymized}',
                        'true'
                    )
                WHERE id = $1
            """, identifier_id)
            return True

    async def get_identifier_stats(self) -> Dict[str, Any]:
        """
        Get identifier statistics.

        Returns:
            Statistics data
        """
        async with self.db_pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_identifiers,
                    COUNT(DISTINCT identifier_type) as unique_types,
                    COUNT(DISTINCT associated_profile_id) as linked_profiles,
                    COUNT(*) FILTER (WHERE associated_profile_id IS NULL) as unlinked,
                    AVG(seen_count) as avg_seen_count
                FROM tracked_identifiers
            """)

            type_breakdown = await conn.fetch("""
                SELECT identifier_type, COUNT(*) as count
                FROM tracked_identifiers
                GROUP BY identifier_type
                ORDER BY count DESC
            """)

            return {
                'total_identifiers': stats['total_identifiers'],
                'unique_types': stats['unique_types'],
                'linked_profiles': stats['linked_profiles'],
                'unlinked_identifiers': stats['unlinked'],
                'avg_seen_count': float(stats['avg_seen_count']) if stats['avg_seen_count'] else 0,
                'type_breakdown': [dict(t) for t in type_breakdown]
            }

    async def cleanup_old_identifiers(
        self,
        days: int = 90
    ) -> int:
        """
        Clean up old identifiers (data retention).

        Args:
            days: Delete identifiers not seen in this many days

        Returns:
            Number of deleted identifiers
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM tracked_identifiers
                WHERE last_seen_at < NOW() - INTERVAL '%s days'
                  AND associated_profile_id IS NULL
            """ % days)

            # Parse result like "DELETE 42"
            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count

    def _hash_value(self, value: str) -> str:
        """Generate SHA-256 hash of value."""
        return hashlib.sha256(value.encode()).hexdigest()
