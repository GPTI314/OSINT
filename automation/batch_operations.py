"""Batch operations for time-saving."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Investigation, Target, Finding, TargetType
from database.gamification_models import InvestigationTemplate


class BatchOperations:
    """
    Batch operations to save time:
    - Bulk import
    - Bulk export
    - Bulk tagging
    - Bulk categorization
    - Bulk sharing
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_import_targets(
        self,
        investigation_id: int,
        targets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk import targets into an investigation.

        Args:
            investigation_id: Investigation ID
            targets: List of target dictionaries

        Returns:
            Import results
        """
        # Get investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            return {'success': False, 'error': 'Investigation not found'}

        created_targets = []
        errors = []

        for idx, target_data in enumerate(targets):
            try:
                # Validate target type
                target_type = target_data.get('type')
                if isinstance(target_type, str):
                    target_type = TargetType(target_type)

                # Create target
                target = Target(
                    type=target_type,
                    value=target_data.get('value'),
                    name=target_data.get('name'),
                    description=target_data.get('description'),
                    metadata=target_data.get('metadata', {})
                )
                self.db.add(target)
                await self.db.flush()

                # Associate with investigation
                investigation.targets.append(target)

                created_targets.append({
                    'index': idx,
                    'id': target.id,
                    'value': target.value
                })

            except Exception as e:
                errors.append({
                    'index': idx,
                    'error': str(e),
                    'data': target_data
                })

        await self.db.commit()

        return {
            'success': True,
            'created': len(created_targets),
            'failed': len(errors),
            'targets': created_targets,
            'errors': errors
        }

    async def bulk_export(
        self,
        investigation_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Bulk export investigation data.

        Args:
            investigation_id: Investigation ID
            format: Export format (json, csv, etc.)

        Returns:
            Exported data
        """
        # Get investigation with all related data
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            return {'error': 'Investigation not found'}

        # Prepare export data
        export_data = {
            'investigation': {
                'id': investigation.id,
                'name': investigation.name,
                'description': investigation.description,
                'status': investigation.status.value,
                'created_at': investigation.created_at.isoformat(),
            },
            'targets': [
                {
                    'id': t.id,
                    'type': t.type.value,
                    'value': t.value,
                    'name': t.name,
                    'description': t.description,
                    'metadata': t.metadata
                }
                for t in investigation.targets
            ],
            'findings': [
                {
                    'id': f.id,
                    'title': f.title,
                    'description': f.description,
                    'severity': f.severity.value,
                    'category': f.category,
                    'evidence': f.evidence,
                    'confidence': f.confidence,
                    'created_at': f.created_at.isoformat()
                }
                for f in investigation.findings
            ]
        }

        if format == 'csv':
            # Convert to CSV format (simplified)
            csv_data = {
                'findings_csv': self._convert_to_csv(export_data['findings']),
                'targets_csv': self._convert_to_csv(export_data['targets'])
            }
            return csv_data

        return export_data

    def _convert_to_csv(self, data: List[Dict]) -> str:
        """Convert list of dictionaries to CSV string."""
        if not data:
            return ""

        # Get headers from first item
        headers = list(data[0].keys())
        csv_lines = [','.join(headers)]

        # Add data rows
        for item in data:
            row = [str(item.get(h, '')) for h in headers]
            csv_lines.append(','.join(row))

        return '\n'.join(csv_lines)

    async def bulk_update_findings(
        self,
        finding_ids: List[int],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Bulk update multiple findings.

        Args:
            finding_ids: List of finding IDs
            updates: Update data

        Returns:
            Update results
        """
        result = await self.db.execute(
            select(Finding).where(Finding.id.in_(finding_ids))
        )
        findings = result.scalars().all()

        updated = []
        for finding in findings:
            # Apply updates
            if 'severity' in updates:
                finding.severity = updates['severity']
            if 'category' in updates:
                finding.category = updates['category']
            if 'is_verified' in updates:
                finding.is_verified = updates['is_verified']

            updated.append(finding.id)

        await self.db.commit()

        return {
            'success': True,
            'updated': len(updated),
            'finding_ids': updated
        }

    async def bulk_tag(
        self,
        resource_type: str,
        resource_ids: List[int],
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Bulk add tags to resources.

        Args:
            resource_type: Type of resource (investigation, finding, etc.)
            resource_ids: List of resource IDs
            tags: List of tags to add

        Returns:
            Tagging results
        """
        # This would update metadata JSON field with tags
        updated_count = 0

        if resource_type == 'investigation':
            result = await self.db.execute(
                select(Investigation).where(Investigation.id.in_(resource_ids))
            )
            resources = result.scalars().all()

            for resource in resources:
                metadata = resource.metadata or {}
                existing_tags = metadata.get('tags', [])
                # Add new tags
                metadata['tags'] = list(set(existing_tags + tags))
                resource.metadata = metadata
                updated_count += 1

        elif resource_type == 'finding':
            result = await self.db.execute(
                select(Finding).where(Finding.id.in_(resource_ids))
            )
            resources = result.scalars().all()

            for resource in resources:
                evidence = resource.evidence or {}
                existing_tags = evidence.get('tags', [])
                evidence['tags'] = list(set(existing_tags + tags))
                resource.evidence = evidence
                updated_count += 1

        await self.db.commit()

        return {
            'success': True,
            'updated': updated_count,
            'tags_added': tags
        }

    async def bulk_categorize(
        self,
        finding_ids: List[int],
        auto_categorize: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk categorize findings.

        Args:
            finding_ids: List of finding IDs
            auto_categorize: Use automatic categorization

        Returns:
            Categorization results
        """
        from .smart_automation import SmartAutomation

        automation = SmartAutomation(self.db)

        result = await self.db.execute(
            select(Finding).where(Finding.id.in_(finding_ids))
        )
        findings = result.scalars().all()

        categorized = []
        for finding in findings:
            if auto_categorize:
                # Auto-categorize based on content
                category = await automation.auto_categorize({
                    'title': finding.title,
                    'description': finding.description
                })
                finding.category = category

            categorized.append({
                'id': finding.id,
                'category': finding.category
            })

        await self.db.commit()

        return {
            'success': True,
            'categorized': len(categorized),
            'results': categorized
        }

    async def bulk_delete(
        self,
        resource_type: str,
        resource_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Bulk delete resources.

        Args:
            resource_type: Type of resource
            resource_ids: List of resource IDs

        Returns:
            Deletion results
        """
        deleted_count = 0

        if resource_type == 'finding':
            result = await self.db.execute(
                select(Finding).where(Finding.id.in_(resource_ids))
            )
            findings = result.scalars().all()

            for finding in findings:
                await self.db.delete(finding)
                deleted_count += 1

        elif resource_type == 'target':
            result = await self.db.execute(
                select(Target).where(Target.id.in_(resource_ids))
            )
            targets = result.scalars().all()

            for target in targets:
                await self.db.delete(target)
                deleted_count += 1

        await self.db.commit()

        return {
            'success': True,
            'deleted': deleted_count
        }
