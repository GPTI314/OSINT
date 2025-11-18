"""Smart automation features."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Finding, Target, Investigation


class SmartAutomation:
    """
    Intelligent automation:
    - Auto-categorization
    - Auto-tagging
    - Auto-correlation
    - Auto-prioritization
    - Auto-scheduling
    - Auto-reporting
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def auto_categorize(self, data: Dict[str, Any]) -> str:
        """
        Automatically categorize data based on content.

        Args:
            data: Data to categorize

        Returns:
            Category name
        """
        # Simple rule-based categorization
        # In production, this would use ML models

        content = str(data.get('title', '')) + ' ' + str(data.get('description', ''))
        content_lower = content.lower()

        # Security categories
        if any(word in content_lower for word in ['malware', 'virus', 'trojan', 'ransomware']):
            return 'malware'
        elif any(word in content_lower for word in ['phishing', 'spoof', 'fake']):
            return 'phishing'
        elif any(word in content_lower for word in ['breach', 'leak', 'exposed', 'dump']):
            return 'data_breach'
        elif any(word in content_lower for word in ['fraud', 'scam', 'fake']):
            return 'fraud'
        elif any(word in content_lower for word in ['vulnerability', 'exploit', 'cve']):
            return 'vulnerability'

        # Information gathering
        elif any(word in content_lower for word in ['email', 'contact', 'address']):
            return 'contact_information'
        elif any(word in content_lower for word in ['social', 'profile', 'account']):
            return 'social_media'
        elif any(word in content_lower for word in ['domain', 'dns', 'whois']):
            return 'domain_intelligence'
        elif any(word in content_lower for word in ['ip', 'address', 'network']):
            return 'network_intelligence'

        return 'general'

    async def auto_tag(self, content: str) -> List[str]:
        """
        Automatically generate tags for content.

        Args:
            content: Content to tag

        Returns:
            List of tags
        """
        tags = []
        content_lower = content.lower()

        # Technology tags
        tech_keywords = {
            'python': 'python',
            'javascript': 'javascript',
            'java': 'java',
            'php': 'php',
            'ruby': 'ruby',
            'node': 'nodejs',
            'docker': 'docker',
            'kubernetes': 'kubernetes',
            'aws': 'aws',
            'azure': 'azure',
            'gcp': 'google-cloud'
        }

        for keyword, tag in tech_keywords.items():
            if keyword in content_lower:
                tags.append(tag)

        # Platform tags
        platforms = ['linkedin', 'facebook', 'twitter', 'instagram', 'github', 'stackoverflow']
        for platform in platforms:
            if platform in content_lower:
                tags.append(platform)

        # Threat tags
        threats = ['malware', 'phishing', 'ransomware', 'ddos', 'botnet', 'exploit']
        for threat in threats:
            if threat in content_lower:
                tags.append(threat)

        return list(set(tags))  # Remove duplicates

    async def auto_correlate(self, investigation_id: int) -> List[Dict]:
        """
        Automatically correlate findings within an investigation.

        Args:
            investigation_id: Investigation ID

        Returns:
            List of correlations found
        """
        # Get all findings for the investigation
        result = await self.db.execute(
            select(Finding)
            .where(Finding.investigation_id == investigation_id)
            .order_by(Finding.created_at)
        )
        findings = result.scalars().all()

        correlations = []

        # Look for IP address correlations
        ip_findings = {}
        for finding in findings:
            evidence = finding.evidence or {}
            if 'ip_address' in evidence:
                ip = evidence['ip_address']
                if ip not in ip_findings:
                    ip_findings[ip] = []
                ip_findings[ip].append(finding.id)

        # Report IPs that appear in multiple findings
        for ip, finding_ids in ip_findings.items():
            if len(finding_ids) > 1:
                correlations.append({
                    'type': 'ip_address',
                    'value': ip,
                    'finding_ids': finding_ids,
                    'count': len(finding_ids),
                    'confidence': 0.9
                })

        # Look for email correlations
        email_findings = {}
        for finding in findings:
            evidence = finding.evidence or {}
            if 'email' in evidence:
                email = evidence['email']
                if email not in email_findings:
                    email_findings[email] = []
                email_findings[email].append(finding.id)

        for email, finding_ids in email_findings.items():
            if len(finding_ids) > 1:
                correlations.append({
                    'type': 'email',
                    'value': email,
                    'finding_ids': finding_ids,
                    'count': len(finding_ids),
                    'confidence': 0.95
                })

        # Look for domain correlations
        domain_findings = {}
        for finding in findings:
            evidence = finding.evidence or {}
            if 'domain' in evidence:
                domain = evidence['domain']
                if domain not in domain_findings:
                    domain_findings[domain] = []
                domain_findings[domain].append(finding.id)

        for domain, finding_ids in domain_findings.items():
            if len(finding_ids) > 1:
                correlations.append({
                    'type': 'domain',
                    'value': domain,
                    'finding_ids': finding_ids,
                    'count': len(finding_ids),
                    'confidence': 0.85
                })

        return correlations

    async def auto_prioritize(self, items: List[Dict]) -> List[Dict]:
        """
        Automatically prioritize items based on various factors.

        Args:
            items: List of items to prioritize

        Returns:
            Sorted list with priority scores
        """
        scored_items = []

        for item in items:
            score = 0

            # Factor 1: Severity
            severity_scores = {
                'critical': 100,
                'high': 75,
                'medium': 50,
                'low': 25,
                'info': 10
            }
            severity = item.get('severity', 'info')
            score += severity_scores.get(severity, 0)

            # Factor 2: Confidence
            confidence = item.get('confidence', 0)
            score += confidence * 50  # Max 50 points

            # Factor 3: Recency
            created_at = item.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
                # Newer items get higher scores
                recency_score = max(0, 30 - (age_hours / 24))  # Max 30 points
                score += recency_score

            # Factor 4: Category importance
            category_scores = {
                'malware': 20,
                'phishing': 20,
                'data_breach': 25,
                'vulnerability': 20,
                'fraud': 15,
                'general': 5
            }
            category = item.get('category', 'general')
            score += category_scores.get(category, 0)

            scored_items.append({
                **item,
                'priority_score': round(score, 2)
            })

        # Sort by priority score (highest first)
        scored_items.sort(key=lambda x: x['priority_score'], reverse=True)

        return scored_items

    async def auto_schedule(self, tasks: List[Dict]) -> Dict[str, Any]:
        """
        Automatically schedule tasks for optimal execution.

        Args:
            tasks: List of tasks to schedule

        Returns:
            Schedule with task assignments
        """
        # Simple scheduling algorithm
        # In production, this would be more sophisticated

        schedule = {
            'immediate': [],
            'short_term': [],  # Within 1 hour
            'medium_term': [],  # Within 24 hours
            'long_term': []  # More than 24 hours
        }

        for task in tasks:
            priority = task.get('priority', 'medium')
            estimated_time = task.get('estimated_time', 300)  # seconds

            if priority in ['critical', 'high']:
                schedule['immediate'].append(task)
            elif priority == 'medium':
                if estimated_time < 600:  # Less than 10 minutes
                    schedule['short_term'].append(task)
                else:
                    schedule['medium_term'].append(task)
            else:
                schedule['long_term'].append(task)

        # Add suggested execution times
        now = datetime.utcnow()
        for category in schedule:
            for idx, task in enumerate(schedule[category]):
                if category == 'immediate':
                    task['suggested_time'] = now
                elif category == 'short_term':
                    task['suggested_time'] = now.replace(minute=0) + timedelta(hours=1)
                elif category == 'medium_term':
                    task['suggested_time'] = now.replace(hour=0, minute=0) + timedelta(days=1)
                else:
                    task['suggested_time'] = now.replace(hour=0, minute=0) + timedelta(days=7)

        return schedule

    async def auto_report_findings(self, investigation_id: int) -> Dict[str, Any]:
        """
        Automatically generate a summary report of findings.

        Args:
            investigation_id: Investigation ID

        Returns:
            Report data
        """
        # Get investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            return {'error': 'Investigation not found'}

        # Get findings
        result = await self.db.execute(
            select(Finding)
            .where(Finding.investigation_id == investigation_id)
            .order_by(Finding.created_at.desc())
        )
        findings = result.scalars().all()

        # Categorize findings
        by_severity = {}
        by_category = {}

        for finding in findings:
            # By severity
            severity = finding.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append({
                'id': finding.id,
                'title': finding.title,
                'description': finding.description
            })

            # By category
            category = finding.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append({
                'id': finding.id,
                'title': finding.title
            })

        # Generate summary
        summary = {
            'investigation_id': investigation_id,
            'investigation_name': investigation.name,
            'total_findings': len(findings),
            'by_severity': by_severity,
            'by_category': by_category,
            'critical_count': len(by_severity.get('critical', [])),
            'high_count': len(by_severity.get('high', [])),
            'medium_count': len(by_severity.get('medium', [])),
            'low_count': len(by_severity.get('low', [])),
            'generated_at': datetime.utcnow().isoformat()
        }

        return summary

    async def suggest_similar_investigations(self, investigation_id: int, limit: int = 5) -> List[Dict]:
        """
        Suggest similar investigations based on targets and findings.

        Args:
            investigation_id: Investigation ID
            limit: Maximum number of suggestions

        Returns:
            List of similar investigations
        """
        # Get current investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        current_inv = result.scalar_one_or_none()

        if not current_inv:
            return []

        # Get all other investigations
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.id != investigation_id)
            .order_by(Investigation.created_at.desc())
            .limit(50)  # Check last 50 investigations
        )
        other_investigations = result.scalars().all()

        # Score based on similarity
        scored = []
        for inv in other_investigations:
            score = 0

            # Check target overlap
            current_targets = {t.value for t in current_inv.targets}
            inv_targets = {t.value for t in inv.targets}
            target_overlap = len(current_targets & inv_targets)
            score += target_overlap * 20

            # Check description similarity (simple keyword matching)
            if current_inv.description and inv.description:
                current_words = set(current_inv.description.lower().split())
                inv_words = set(inv.description.lower().split())
                word_overlap = len(current_words & inv_words)
                score += word_overlap

            if score > 0:
                scored.append({
                    'id': inv.id,
                    'name': inv.name,
                    'description': inv.description,
                    'similarity_score': score,
                    'created_at': inv.created_at.isoformat()
                })

        # Sort by score and return top results
        scored.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored[:limit]
