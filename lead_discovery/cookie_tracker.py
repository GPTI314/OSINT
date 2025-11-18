"""
Cookie and Identifier Tracking System

WARNING: For authorized security testing only.
This module demonstrates cookie tracking techniques for security research.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import asyncpg
from asyncpg.pool import Pool


class CookieTracker:
    """
    Cookie and identifier tracking system for security testing.

    Tracks cookies, identifiers, and user sessions to identify
    tracking vulnerabilities and privacy leaks.
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def track_cookies(
        self,
        investigation_id: str,
        url: str,
        cookies: List[Dict[str, Any]],
        metadata: Optional[Dict] = None
    ) -> List[str]:
        """
        Track and store cookies from websites.

        Args:
            investigation_id: Investigation UUID
            url: Source URL
            cookies: List of cookie dictionaries
            metadata: Additional metadata

        Returns:
            List of cookie tracking IDs
        """
        tracking_ids = []
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        for cookie in cookies:
            try:
                # Extract identifier from cookie
                identifier_id = await self._track_identifier(
                    identifier_type='cookie',
                    identifier_value=f"{cookie.get('name')}={cookie.get('value')}",
                    sites=[url]
                )

                # Store cookie tracking data
                async with self.db_pool.acquire() as conn:
                    tracking_id = await conn.fetchval("""
                        INSERT INTO cookie_tracking (
                            identifier_id,
                            investigation_id,
                            cookie_name,
                            cookie_value,
                            cookie_domain,
                            cookie_path,
                            expires_at,
                            is_secure,
                            is_http_only,
                            same_site,
                            site_url,
                            metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        RETURNING id
                    """, identifier_id, investigation_id, cookie.get('name'),
                        cookie.get('value'), cookie.get('domain', domain),
                        cookie.get('path', '/'), cookie.get('expires'),
                        cookie.get('secure', False), cookie.get('httpOnly', False),
                        cookie.get('sameSite', 'None'), url,
                        json.dumps(metadata or {}))

                    tracking_ids.append(str(tracking_id))

            except Exception as e:
                print(f"Error tracking cookie: {e}")
                continue

        return tracking_ids

    async def extract_identifiers(
        self,
        page_content: str,
        cookies: List[Dict],
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract identifiers from page content and cookies.

        Looks for:
        - Email addresses
        - Phone numbers
        - User IDs
        - Tracking IDs
        - Session tokens
        """
        import re

        identifiers = []

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_content)
        for email in set(emails):
            identifiers.append({
                'type': 'email',
                'value': email,
                'source': 'content'
            })

        # Extract phone numbers (US format)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, page_content)
        for phone in set(phones):
            identifiers.append({
                'type': 'phone',
                'value': phone,
                'source': 'content'
            })

        # Extract user IDs from common patterns
        user_id_patterns = [
            r'user[_-]?id["\s:=]+([a-zA-Z0-9-]+)',
            r'userId["\s:=]+([a-zA-Z0-9-]+)',
            r'customer[_-]?id["\s:=]+([a-zA-Z0-9-]+)',
        ]
        for pattern in user_id_patterns:
            user_ids = re.findall(pattern, page_content, re.IGNORECASE)
            for user_id in set(user_ids):
                identifiers.append({
                    'type': 'user_id',
                    'value': user_id,
                    'source': 'content'
                })

        # Extract tracking IDs from cookies
        tracking_cookie_names = [
            '_ga', '_gid', 'fbp', 'fr', '_fbp', 'IDE', 'id',
            'visitor_id', 'session_id', 'tracking_id'
        ]
        for cookie in cookies:
            if any(name in cookie.get('name', '').lower() for name in tracking_cookie_names):
                identifiers.append({
                    'type': 'tracking_id',
                    'value': cookie.get('value'),
                    'source': f"cookie:{cookie.get('name')}",
                    'cookie_name': cookie.get('name')
                })

        # Store identifiers
        stored_identifiers = []
        for ident in identifiers:
            try:
                identifier_id = await self._track_identifier(
                    identifier_type=ident['type'],
                    identifier_value=ident['value'],
                    metadata={'source': ident.get('source'), **(metadata or {})}
                )
                stored_identifiers.append({
                    'id': identifier_id,
                    **ident
                })
            except Exception as e:
                print(f"Error storing identifier: {e}")
                continue

        return stored_identifiers

    async def build_user_profile(
        self,
        identifiers: List[str],
        investigation_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Build user profile from tracked identifiers.

        Args:
            identifiers: List of identifier IDs
            investigation_id: Investigation UUID

        Returns:
            Profile ID
        """
        if not identifiers:
            return None

        # Generate profile hash from identifiers
        profile_hash = self._generate_profile_hash(identifiers)

        # Check if profile already exists
        async with self.db_pool.acquire() as conn:
            existing_profile = await conn.fetchval("""
                SELECT id FROM user_profiles WHERE profile_hash = $1
            """, profile_hash)

            if existing_profile:
                # Update existing profile
                await conn.execute("""
                    UPDATE user_profiles
                    SET identifiers = array_cat(identifiers, $1::UUID[]),
                        updated_at = NOW()
                    WHERE id = $2
                """, identifiers, existing_profile)
                return str(existing_profile)

            # Create new profile
            profile_id = await conn.fetchval("""
                INSERT INTO user_profiles (
                    investigation_id,
                    profile_hash,
                    identifiers,
                    created_at,
                    updated_at
                ) VALUES ($1, $2, $3, NOW(), NOW())
                RETURNING id
            """, investigation_id, profile_hash, identifiers)

            # Link identifiers to profile
            await conn.execute("""
                UPDATE tracked_identifiers
                SET associated_profile_id = $1
                WHERE id = ANY($2::UUID[])
            """, profile_id, identifiers)

            return str(profile_id)

    async def track_cross_site(
        self,
        identifier_id: str,
        site_url: str,
        pages_visited: Optional[List[str]] = None,
        time_spent: int = 0,
        actions: Optional[List[Dict]] = None
    ) -> str:
        """
        Track user across multiple sites.

        Args:
            identifier_id: Identifier UUID
            site_url: Site URL
            pages_visited: List of pages visited
            time_spent: Time spent in seconds
            actions: Actions taken on site

        Returns:
            Tracking ID
        """
        parsed_url = urlparse(site_url)
        domain = parsed_url.netloc

        async with self.db_pool.acquire() as conn:
            # Check if tracking entry exists
            existing = await conn.fetchval("""
                SELECT id FROM cross_site_tracking
                WHERE identifier_id = $1 AND site_domain = $2
            """, identifier_id, domain)

            if existing:
                # Update existing entry
                await conn.execute("""
                    UPDATE cross_site_tracking
                    SET visit_count = visit_count + 1,
                        last_visit_at = NOW(),
                        pages_visited = array_cat(pages_visited, $1),
                        time_spent = time_spent + $2,
                        actions_taken = actions_taken || $3::jsonb
                    WHERE id = $4
                """, pages_visited or [], time_spent,
                    json.dumps(actions or []), existing)
                return str(existing)

            # Create new tracking entry
            tracking_id = await conn.fetchval("""
                INSERT INTO cross_site_tracking (
                    identifier_id,
                    site_url,
                    site_domain,
                    pages_visited,
                    time_spent,
                    actions_taken
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, identifier_id, site_url, domain,
                pages_visited or [], time_spent,
                json.dumps(actions or []))

            # Update identifier sites_seen_on
            await conn.execute("""
                UPDATE tracked_identifiers
                SET sites_seen_on = array_append(sites_seen_on, $1),
                    last_seen_at = NOW(),
                    seen_count = seen_count + 1
                WHERE id = $2
            """, site_url, identifier_id)

            return str(tracking_id)

    async def fingerprint_device(
        self,
        browser_data: Dict[str, Any],
        profile_id: Optional[str] = None
    ) -> str:
        """
        Create device fingerprint from browser data.

        Args:
            browser_data: Browser fingerprinting data
            profile_id: User profile ID

        Returns:
            Fingerprint ID
        """
        # Generate fingerprint hash
        fingerprint_components = [
            browser_data.get('userAgent', ''),
            browser_data.get('screenResolution', ''),
            str(browser_data.get('colorDepth', '')),
            browser_data.get('timezone', ''),
            browser_data.get('language', ''),
            ','.join(sorted(browser_data.get('plugins', []))),
            ','.join(sorted(browser_data.get('fonts', []))),
            browser_data.get('canvasFingerprint', ''),
            browser_data.get('webglFingerprint', ''),
        ]

        fingerprint_string = '|'.join(fingerprint_components)
        fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()

        async with self.db_pool.acquire() as conn:
            # Check if fingerprint exists
            existing = await conn.fetchval("""
                SELECT id FROM device_fingerprints
                WHERE fingerprint_hash = $1
            """, fingerprint_hash)

            if existing:
                # Update last seen
                await conn.execute("""
                    UPDATE device_fingerprints
                    SET last_seen_at = NOW()
                    WHERE id = $1
                """, existing)
                return str(existing)

            # Create new fingerprint
            fingerprint_id = await conn.fetchval("""
                INSERT INTO device_fingerprints (
                    profile_id,
                    fingerprint_hash,
                    user_agent,
                    screen_resolution,
                    color_depth,
                    timezone,
                    language,
                    plugins,
                    fonts,
                    canvas_fingerprint,
                    webgl_fingerprint,
                    audio_fingerprint,
                    platform,
                    cpu_cores,
                    device_memory
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id
            """, profile_id, fingerprint_hash,
                browser_data.get('userAgent'),
                browser_data.get('screenResolution'),
                browser_data.get('colorDepth'),
                browser_data.get('timezone'),
                browser_data.get('language'),
                browser_data.get('plugins', []),
                browser_data.get('fonts', []),
                browser_data.get('canvasFingerprint'),
                browser_data.get('webglFingerprint'),
                browser_data.get('audioFingerprint'),
                browser_data.get('platform'),
                browser_data.get('cpuCores'),
                browser_data.get('deviceMemory'))

            # Update profile if provided
            if profile_id:
                await conn.execute("""
                    UPDATE user_profiles
                    SET device_fingerprint = $1,
                        updated_at = NOW()
                    WHERE id = $2
                """, fingerprint_hash, profile_id)

            return str(fingerprint_id)

    async def track_behavior(
        self,
        profile_id: str,
        behavior_type: str,
        behavior_data: Dict[str, Any],
        site_url: Optional[str] = None
    ) -> str:
        """
        Track user behavior patterns.

        Args:
            profile_id: User profile ID
            behavior_type: Type of behavior (page_view, click, form_submit, etc.)
            behavior_data: Behavior data
            site_url: Site URL

        Returns:
            Behavior tracking ID
        """
        async with self.db_pool.acquire() as conn:
            behavior_id = await conn.fetchval("""
                INSERT INTO behavioral_tracking (
                    profile_id,
                    behavior_type,
                    behavior_data,
                    site_url,
                    page_path,
                    element_id,
                    element_class,
                    element_text,
                    session_id,
                    timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
                RETURNING id
            """, profile_id, behavior_type, json.dumps(behavior_data),
                site_url, behavior_data.get('page_path'),
                behavior_data.get('element_id'),
                behavior_data.get('element_class'),
                behavior_data.get('element_text'),
                behavior_data.get('session_id'))

            # Update profile behaviors
            await conn.execute("""
                UPDATE user_profiles
                SET behaviors = jsonb_set(
                    COALESCE(behaviors, '{}'::jsonb),
                    ARRAY[$1],
                    COALESCE(behaviors->$1, '0')::int + 1,
                    true
                ),
                updated_at = NOW()
                WHERE id = $2
            """, behavior_type, profile_id)

            return str(behavior_id)

    async def get_profile_by_identifier(
        self,
        identifier_type: str,
        identifier_value: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user profile by identifier.

        Args:
            identifier_type: Type of identifier
            identifier_value: Identifier value

        Returns:
            Profile data or None
        """
        identifier_hash = self._hash_identifier(identifier_value)

        async with self.db_pool.acquire() as conn:
            profile = await conn.fetchrow("""
                SELECT p.*, ti.identifier_value
                FROM user_profiles p
                JOIN tracked_identifiers ti ON ti.associated_profile_id = p.id
                WHERE ti.identifier_type = $1 AND ti.identifier_hash = $2
                LIMIT 1
            """, identifier_type, identifier_hash)

            if profile:
                return dict(profile)
            return None

    async def _track_identifier(
        self,
        identifier_type: str,
        identifier_value: str,
        sites: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Track an identifier and return its ID."""
        identifier_hash = self._hash_identifier(identifier_value)

        async with self.db_pool.acquire() as conn:
            # Check if identifier exists
            existing = await conn.fetchval("""
                SELECT id FROM tracked_identifiers
                WHERE identifier_type = $1 AND identifier_hash = $2
            """, identifier_type, identifier_hash)

            if existing:
                # Update existing identifier
                await conn.execute("""
                    UPDATE tracked_identifiers
                    SET last_seen_at = NOW(),
                        seen_count = seen_count + 1,
                        sites_seen_on = array_cat(sites_seen_on, $1)
                    WHERE id = $2
                """, sites or [], existing)
                return str(existing)

            # Insert new identifier
            identifier_id = await conn.fetchval("""
                INSERT INTO tracked_identifiers (
                    identifier_type,
                    identifier_value,
                    identifier_hash,
                    sites_seen_on,
                    metadata
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, identifier_type, identifier_value, identifier_hash,
                sites or [], json.dumps(metadata or {}))

            return str(identifier_id)

    def _hash_identifier(self, identifier_value: str) -> str:
        """Generate SHA-256 hash of identifier for privacy."""
        return hashlib.sha256(identifier_value.encode()).hexdigest()

    def _generate_profile_hash(self, identifiers: List[str]) -> str:
        """Generate hash for user profile from identifiers."""
        sorted_identifiers = sorted(identifiers)
        profile_string = '|'.join(sorted_identifiers)
        return hashlib.sha256(profile_string.encode()).hexdigest()
