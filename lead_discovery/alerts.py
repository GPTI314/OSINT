"""
Lead Alert System

Real-time alerting for lead discovery events.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncpg
from asyncpg.pool import Pool


class LeadAlertSystem:
    """
    Real-time lead alert system.

    Alert types:
    - New lead alerts
    - High-score match alerts
    - Geographic alerts
    - Industry alerts
    - Behavior change alerts
    - Signal strength alerts
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def send_lead_alert(
        self,
        lead_id: str,
        alert_type: str,
        title: str,
        message: str,
        priority: str = 'medium',
        alert_data: Optional[Dict] = None
    ) -> str:
        """
        Send lead alert.

        Args:
            lead_id: Lead UUID
            alert_type: Type of alert
            title: Alert title
            message: Alert message
            priority: Alert priority (low, medium, high, urgent)
            alert_data: Additional alert data

        Returns:
            Alert ID
        """
        async with self.db_pool.acquire() as conn:
            alert_id = await conn.fetchval("""
                INSERT INTO lead_alerts (
                    lead_id,
                    alert_type,
                    title,
                    message,
                    priority,
                    alert_data,
                    status
                ) VALUES ($1, $2, $3, $4, $5, $6, 'new')
                RETURNING id
            """, lead_id, alert_type, title, message, priority,
                json.dumps(alert_data or {}))

            # Check if there are alert rules for this type
            await self._process_alert_rules(alert_id, alert_type, alert_data or {})

            return str(alert_id)

    async def send_match_alert(
        self,
        match_id: str,
        lead_id: str,
        service_id: str,
        match_score: float
    ) -> str:
        """
        Send alert for new match.

        Args:
            match_id: Match UUID
            lead_id: Lead UUID
            service_id: Service UUID
            match_score: Match score

        Returns:
            Alert ID
        """
        async with self.db_pool.acquire() as conn:
            # Get lead and service info
            lead = await conn.fetchrow("""
                SELECT name, company FROM discovered_leads WHERE id = $1
            """, lead_id)

            service = await conn.fetchrow("""
                SELECT service_name FROM services_catalog WHERE id = $1
            """, service_id)

            if not lead or not service:
                return ""

            title = f"High Score Match: {match_score:.0f}%"
            message = (f"Lead '{lead['name'] or lead['company']}' matched with "
                      f"service '{service['service_name']}' at {match_score:.0f}% confidence")

            priority = 'urgent' if match_score >= 90 else 'high' if match_score >= 75 else 'medium'

            return await self.send_lead_alert(
                lead_id,
                'high_score_match',
                title,
                message,
                priority,
                {
                    'match_id': str(match_id),
                    'service_id': str(service_id),
                    'match_score': match_score
                }
            )

    async def send_geographic_alert(
        self,
        lead_id: str,
        location: str
    ) -> str:
        """
        Send alert for lead in targeted geographic area.

        Args:
            lead_id: Lead UUID
            location: Location string

        Returns:
            Alert ID
        """
        return await self.send_lead_alert(
            lead_id,
            'geographic',
            f"New Lead in {location}",
            f"New lead discovered in targeted area: {location}",
            'medium',
            {'location': location}
        )

    async def send_industry_alert(
        self,
        lead_id: str,
        industry: str
    ) -> str:
        """
        Send alert for lead in targeted industry.

        Args:
            lead_id: Lead UUID
            industry: Industry name

        Returns:
            Alert ID
        """
        return await self.send_lead_alert(
            lead_id,
            'industry',
            f"New Lead in {industry}",
            f"New lead discovered in targeted industry: {industry}",
            'medium',
            {'industry': industry}
        )

    async def send_behavior_alert(
        self,
        profile_id: str,
        behavior_type: str,
        behavior_data: Dict[str, Any]
    ) -> str:
        """
        Send alert for significant behavior change.

        Args:
            profile_id: Profile UUID
            behavior_type: Type of behavior
            behavior_data: Behavior data

        Returns:
            Alert ID
        """
        async with self.db_pool.acquire() as conn:
            # Find lead associated with profile
            lead = await conn.fetchrow("""
                SELECT id FROM discovered_leads WHERE profile_id = $1
                LIMIT 1
            """, profile_id)

            if not lead:
                return ""

            return await self.send_lead_alert(
                str(lead['id']),
                'behavior_change',
                f"Behavior Alert: {behavior_type}",
                f"Significant behavior detected: {behavior_type}",
                'medium',
                {'behavior_type': behavior_type, **behavior_data}
            )

    async def setup_alert_rules(
        self,
        rules: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Setup alert rules.

        Args:
            rules: List of alert rule configurations

        Returns:
            List of rule IDs
        """
        rule_ids = []

        async with self.db_pool.acquire() as conn:
            for rule in rules:
                rule_id = await conn.fetchval("""
                    INSERT INTO alert_rules (
                        rule_name,
                        rule_type,
                        conditions,
                        alert_channels,
                        recipients,
                        webhook_url,
                        is_active,
                        priority
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id
                """, rule.get('rule_name'),
                    rule.get('rule_type'),
                    json.dumps(rule.get('conditions', {})),
                    rule.get('alert_channels', ['dashboard']),
                    rule.get('recipients', []),
                    rule.get('webhook_url'),
                    rule.get('is_active', True),
                    rule.get('priority', 'medium'))

                rule_ids.append(str(rule_id))

        return rule_ids

    async def get_alerts(
        self,
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filters.

        Args:
            status: Filter by status
            alert_type: Filter by type
            priority: Filter by priority
            limit: Maximum alerts to return

        Returns:
            List of alerts
        """
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM lead_alerts WHERE 1=1"
            params = []
            param_count = 1

            if status:
                query += f" AND status = ${param_count}"
                params.append(status)
                param_count += 1

            if alert_type:
                query += f" AND alert_type = ${param_count}"
                params.append(alert_type)
                param_count += 1

            if priority:
                query += f" AND priority = ${param_count}"
                params.append(priority)
                param_count += 1

            query += f" ORDER BY created_at DESC LIMIT ${param_count}"
            params.append(limit)

            alerts = await conn.fetch(query, *params)
            return [dict(a) for a in alerts]

    async def mark_alert_read(self, alert_id: str) -> bool:
        """Mark alert as read."""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE lead_alerts
                SET status = 'read', read_at = NOW()
                WHERE id = $1
            """, alert_id)
            return True

    async def mark_alert_actioned(self, alert_id: str) -> bool:
        """Mark alert as actioned."""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE lead_alerts
                SET status = 'actioned', actioned_at = NOW()
                WHERE id = $1
            """, alert_id)
            return True

    async def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss alert."""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE lead_alerts
                SET status = 'dismissed'
                WHERE id = $1
            """, alert_id)
            return True

    async def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get alert summary statistics.

        Returns:
            Summary data
        """
        async with self.db_pool.acquire() as conn:
            summary = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_alerts,
                    COUNT(*) FILTER (WHERE status = 'new') as new_alerts,
                    COUNT(*) FILTER (WHERE status = 'read') as read_alerts,
                    COUNT(*) FILTER (WHERE status = 'actioned') as actioned_alerts,
                    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_alerts,
                    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_alerts
                FROM lead_alerts
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)

            type_breakdown = await conn.fetch("""
                SELECT alert_type, COUNT(*) as count
                FROM lead_alerts
                WHERE created_at > NOW() - INTERVAL '7 days'
                GROUP BY alert_type
                ORDER BY count DESC
            """)

            return {
                'total_alerts': summary['total_alerts'],
                'new_alerts': summary['new_alerts'],
                'read_alerts': summary['read_alerts'],
                'actioned_alerts': summary['actioned_alerts'],
                'urgent_alerts': summary['urgent_alerts'],
                'high_priority_alerts': summary['high_priority_alerts'],
                'type_breakdown': [dict(t) for t in type_breakdown]
            }

    async def _process_alert_rules(
        self,
        alert_id: str,
        alert_type: str,
        alert_data: Dict[str, Any]
    ) -> None:
        """Process alert against rules."""
        async with self.db_pool.acquire() as conn:
            # Get active rules for this alert type
            rules = await conn.fetch("""
                SELECT * FROM alert_rules
                WHERE rule_type = $1 AND is_active = TRUE
            """, alert_type)

            for rule in rules:
                # Check conditions
                conditions = json.loads(rule['conditions']) if rule['conditions'] else {}

                if self._check_conditions(alert_data, conditions):
                    # Link alert to rule
                    await conn.execute("""
                        UPDATE lead_alerts
                        SET alert_rule_id = $1
                        WHERE id = $2
                    """, rule['id'], alert_id)

                    # Send via configured channels
                    await self._send_via_channels(
                        dict(rule),
                        alert_id,
                        alert_type,
                        alert_data
                    )

    def _check_conditions(
        self,
        alert_data: Dict[str, Any],
        conditions: Dict[str, Any]
    ) -> bool:
        """Check if alert data meets rule conditions."""
        for key, value in conditions.items():
            if key.startswith('min_'):
                field = key[4:]
                if alert_data.get(field, 0) < value:
                    return False
            elif key.startswith('max_'):
                field = key[4:]
                if alert_data.get(field, 0) > value:
                    return False
            elif alert_data.get(key) != value:
                return False

        return True

    async def _send_via_channels(
        self,
        rule: Dict[str, Any],
        alert_id: str,
        alert_type: str,
        alert_data: Dict[str, Any]
    ) -> None:
        """Send alert via configured channels."""
        channels = rule.get('alert_channels', [])

        # Dashboard is default, already stored in DB

        # Email (would integrate with email service)
        if 'email' in channels and rule.get('recipients'):
            # TODO: Implement email sending
            pass

        # Webhook
        if 'webhook' in channels and rule.get('webhook_url'):
            # TODO: Implement webhook posting
            pass
