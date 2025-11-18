"""Template system for investigations and workflows."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import InvestigationTemplate, VisibilityLevel
from database.models import Investigation, Target


class TemplateSystem:
    """
    Templates and presets:
    - Investigation templates
    - Workflow templates
    - Report templates
    - Dashboard presets
    - Quick start templates
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(
        self,
        name: str,
        description: str,
        template_data: Dict[str, Any],
        category: str,
        created_by: int,
        tags: List[str] = None,
        visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    ) -> InvestigationTemplate:
        """
        Create a new investigation template.

        Args:
            name: Template name
            description: Template description
            template_data: Template configuration
            category: Template category
            created_by: User ID who created it
            tags: Template tags
            visibility: Template visibility

        Returns:
            Created template
        """
        template = InvestigationTemplate(
            name=name,
            description=description,
            template_data=template_data,
            category=category,
            tags=tags or [],
            created_by=created_by,
            visibility=visibility
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def create_from_template(
        self,
        template_id: int,
        user_id: int,
        customizations: Dict[str, Any] = None
    ) -> Investigation:
        """
        Create a new investigation from a template.

        Args:
            template_id: Template ID
            user_id: User creating the investigation
            customizations: Custom values to override template

        Returns:
            Created investigation
        """
        # Get template
        result = await self.db.execute(
            select(InvestigationTemplate).where(InvestigationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template not found")

        # Merge template data with customizations
        data = {**template.template_data}
        if customizations:
            data.update(customizations)

        # Create investigation
        investigation = Investigation(
            name=data.get('name', template.name),
            description=data.get('description', template.description),
            status=data.get('status', 'draft'),
            priority=data.get('priority', 0),
            metadata=data.get('metadata', {}),
            created_by=user_id
        )

        self.db.add(investigation)
        await self.db.flush()

        # Add targets if specified in template
        if 'targets' in data:
            for target_data in data['targets']:
                target = Target(
                    type=target_data.get('type'),
                    value=target_data.get('value'),
                    name=target_data.get('name'),
                    description=target_data.get('description')
                )
                self.db.add(target)
                await self.db.flush()
                investigation.targets.append(target)

        # Update template usage count
        template.usage_count += 1

        await self.db.commit()
        await self.db.refresh(investigation)

        return investigation

    async def save_as_template(
        self,
        investigation_id: int,
        template_name: str,
        template_description: str,
        user_id: int,
        category: str = 'custom'
    ) -> InvestigationTemplate:
        """
        Save an existing investigation as a template.

        Args:
            investigation_id: Investigation to save as template
            template_name: Name for the template
            template_description: Template description
            user_id: User creating the template
            category: Template category

        Returns:
            Created template
        """
        # Get investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            raise ValueError("Investigation not found")

        # Build template data
        template_data = {
            'name': investigation.name,
            'description': investigation.description,
            'status': investigation.status.value,
            'priority': investigation.priority,
            'metadata': investigation.metadata,
            'targets': [
                {
                    'type': t.type.value,
                    'value': t.value,
                    'name': t.name,
                    'description': t.description
                }
                for t in investigation.targets
            ]
        }

        # Create template
        template = await self.create_template(
            name=template_name,
            description=template_description,
            template_data=template_data,
            category=category,
            created_by=user_id
        )

        return template

    async def get_templates(
        self,
        user_id: int,
        category: Optional[str] = None,
        include_public: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get available templates for a user.

        Args:
            user_id: User ID
            category: Filter by category
            include_public: Include public templates
            limit: Maximum results

        Returns:
            List of templates
        """
        # Build query
        query = select(InvestigationTemplate)

        # Filter by visibility
        if include_public:
            query = query.where(
                (InvestigationTemplate.created_by == user_id) |
                (InvestigationTemplate.visibility == VisibilityLevel.PUBLIC)
            )
        else:
            query = query.where(InvestigationTemplate.created_by == user_id)

        # Filter by category
        if category:
            query = query.where(InvestigationTemplate.category == category)

        # Order by usage and creation date
        query = query.order_by(
            InvestigationTemplate.usage_count.desc(),
            InvestigationTemplate.created_at.desc()
        ).limit(limit)

        result = await self.db.execute(query)
        templates = result.scalars().all()

        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category,
                'tags': t.tags,
                'usage_count': t.usage_count,
                'rating': t.rating,
                'created_at': t.created_at.isoformat(),
                'visibility': t.visibility.value
            }
            for t in templates
        ]

    async def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular public templates."""
        result = await self.db.execute(
            select(InvestigationTemplate)
            .where(InvestigationTemplate.visibility == VisibilityLevel.PUBLIC)
            .order_by(InvestigationTemplate.usage_count.desc())
            .limit(limit)
        )
        templates = result.scalars().all()

        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category,
                'usage_count': t.usage_count,
                'rating': t.rating
            }
            for t in templates
        ]

    async def rate_template(
        self,
        template_id: int,
        rating: float
    ) -> Dict[str, Any]:
        """
        Rate a template.

        Args:
            template_id: Template ID
            rating: Rating value (0-5)

        Returns:
            Updated rating info
        """
        result = await self.db.execute(
            select(InvestigationTemplate).where(InvestigationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            return {'error': 'Template not found'}

        # Simple rating update (in production, track individual ratings)
        if template.rating == 0:
            template.rating = rating
        else:
            # Average with existing rating
            template.rating = (template.rating + rating) / 2

        await self.db.commit()

        return {
            'template_id': template_id,
            'rating': template.rating
        }

    async def get_suggested_templates(
        self,
        user_id: int,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get template suggestions based on user activity.

        Args:
            user_id: User ID
            context: Context for suggestions

        Returns:
            List of suggested templates
        """
        # Get user's recent investigations
        result = await self.db.execute(
            select(Investigation)
            .where(Investigation.created_by == user_id)
            .order_by(Investigation.created_at.desc())
            .limit(5)
        )
        recent_investigations = result.scalars().all()

        # Determine common categories/patterns
        # For now, return popular templates
        return await self.get_popular_templates(limit=5)
