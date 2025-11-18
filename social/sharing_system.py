"""Sharing and discovery system."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import (
    SharedInvestigation, InvestigationLike, InvestigationComment,
    VisibilityLevel, UserNotification, NotificationType
)
from database.models import Investigation, User


class SharingSystem:
    """
    Sharing and discovery:
    - Share findings
    - Discover public investigations
    - Follow other users
    - Like and comment
    - Templates marketplace
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def share_investigation(
        self,
        investigation_id: int,
        shared_by: int,
        visibility: VisibilityLevel = VisibilityLevel.PUBLIC,
        title: str = None,
        description: str = None
    ) -> SharedInvestigation:
        """
        Share an investigation.

        Args:
            investigation_id: Investigation ID to share
            shared_by: User ID sharing the investigation
            visibility: Visibility level
            title: Custom title (optional)
            description: Custom description (optional)

        Returns:
            Shared investigation object
        """
        # Get investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            raise ValueError("Investigation not found")

        # Use investigation details if not provided
        if not title:
            title = investigation.name
        if not description:
            description = investigation.description

        # Create shared investigation
        shared = SharedInvestigation(
            investigation_id=investigation_id,
            shared_by=shared_by,
            visibility=visibility,
            title=title,
            description=description
        )

        self.db.add(shared)
        await self.db.commit()
        await self.db.refresh(shared)

        return shared

    async def discover_public(
        self,
        filters: Dict[str, Any] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Discover public shared investigations.

        Args:
            filters: Filter criteria
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Discovery results
        """
        # Build query
        query = (
            select(SharedInvestigation, User)
            .join(User, SharedInvestigation.shared_by == User.id)
            .where(SharedInvestigation.visibility == VisibilityLevel.PUBLIC)
        )

        # Apply filters
        if filters:
            if 'min_likes' in filters:
                query = query.where(SharedInvestigation.like_count >= filters['min_likes'])
            if 'category' in filters:
                # Would need to join with Investigation to filter by category
                pass

        # Order by popularity
        query = query.order_by(
            desc(SharedInvestigation.like_count),
            desc(SharedInvestigation.view_count)
        ).limit(limit).offset(offset)

        result = await self.db.execute(query)
        shared_investigations = result.all()

        # Get total count
        count_result = await self.db.execute(
            select(func.count(SharedInvestigation.id))
            .where(SharedInvestigation.visibility == VisibilityLevel.PUBLIC)
        )
        total_count = count_result.scalar()

        return {
            'total': total_count,
            'results': [
                {
                    'id': shared.id,
                    'investigation_id': shared.investigation_id,
                    'title': shared.title,
                    'description': shared.description,
                    'shared_by': {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name
                    },
                    'view_count': shared.view_count,
                    'like_count': shared.like_count,
                    'clone_count': shared.clone_count,
                    'shared_at': shared.shared_at.isoformat()
                }
                for shared, user in shared_investigations
            ]
        }

    async def like_investigation(
        self,
        shared_investigation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Like a shared investigation."""
        # Check if already liked
        result = await self.db.execute(
            select(InvestigationLike).where(
                and_(
                    InvestigationLike.shared_investigation_id == shared_investigation_id,
                    InvestigationLike.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {'success': False, 'error': 'Already liked'}

        # Create like
        like = InvestigationLike(
            shared_investigation_id=shared_investigation_id,
            user_id=user_id
        )
        self.db.add(like)

        # Update like count
        result = await self.db.execute(
            select(SharedInvestigation).where(SharedInvestigation.id == shared_investigation_id)
        )
        shared = result.scalar_one_or_none()

        if shared:
            shared.like_count += 1

            # Notify the owner
            notification = UserNotification(
                user_id=shared.shared_by,
                notification_type=NotificationType.SHARE,
                title="Someone liked your shared investigation!",
                message=f"Your investigation '{shared.title}' received a like",
                data={
                    'shared_investigation_id': shared_investigation_id,
                    'liked_by': user_id
                }
            )
            self.db.add(notification)

        await self.db.commit()

        return {'success': True, 'like_count': shared.like_count if shared else 0}

    async def unlike_investigation(
        self,
        shared_investigation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Unlike a shared investigation."""
        # Find like
        result = await self.db.execute(
            select(InvestigationLike).where(
                and_(
                    InvestigationLike.shared_investigation_id == shared_investigation_id,
                    InvestigationLike.user_id == user_id
                )
            )
        )
        like = result.scalar_one_or_none()

        if not like:
            return {'success': False, 'error': 'Not liked'}

        # Delete like
        await self.db.delete(like)

        # Update like count
        result = await self.db.execute(
            select(SharedInvestigation).where(SharedInvestigation.id == shared_investigation_id)
        )
        shared = result.scalar_one_or_none()

        if shared:
            shared.like_count = max(0, shared.like_count - 1)

        await self.db.commit()

        return {'success': True, 'like_count': shared.like_count if shared else 0}

    async def comment_on_investigation(
        self,
        shared_investigation_id: int,
        user_id: int,
        content: str
    ) -> InvestigationComment:
        """Add a comment to a shared investigation."""
        comment = InvestigationComment(
            shared_investigation_id=shared_investigation_id,
            user_id=user_id,
            content=content
        )

        self.db.add(comment)

        # Notify the owner
        result = await self.db.execute(
            select(SharedInvestigation).where(SharedInvestigation.id == shared_investigation_id)
        )
        shared = result.scalar_one_or_none()

        if shared and shared.shared_by != user_id:
            notification = UserNotification(
                user_id=shared.shared_by,
                notification_type=NotificationType.SHARE,
                title="New comment on your shared investigation!",
                message=f"Someone commented on '{shared.title}'",
                data={
                    'shared_investigation_id': shared_investigation_id,
                    'comment_id': comment.id
                }
            )
            self.db.add(notification)

        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    async def get_comments(
        self,
        shared_investigation_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get comments for a shared investigation."""
        result = await self.db.execute(
            select(InvestigationComment, User)
            .join(User, InvestigationComment.user_id == User.id)
            .where(InvestigationComment.shared_investigation_id == shared_investigation_id)
            .order_by(desc(InvestigationComment.created_at))
            .limit(limit)
        )
        comments = result.all()

        return [
            {
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                },
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat()
            }
            for comment, user in comments
        ]

    async def clone_investigation(
        self,
        shared_investigation_id: int,
        user_id: int
    ) -> Investigation:
        """Clone a shared investigation."""
        # Get shared investigation
        result = await self.db.execute(
            select(SharedInvestigation, Investigation)
            .join(Investigation)
            .where(SharedInvestigation.id == shared_investigation_id)
        )
        data = result.first()

        if not data:
            raise ValueError("Shared investigation not found")

        shared, original = data

        # Create new investigation (clone)
        cloned = Investigation(
            name=f"{original.name} (Cloned)",
            description=original.description,
            status=original.status,
            priority=original.priority,
            metadata={
                **original.metadata,
                'cloned_from': original.id,
                'cloned_from_shared': shared_investigation_id
            },
            created_by=user_id
        )

        self.db.add(cloned)
        await self.db.flush()

        # Clone targets
        for target in original.targets:
            from database.models import Target
            cloned_target = Target(
                type=target.type,
                value=target.value,
                name=target.name,
                description=target.description,
                metadata=target.metadata
            )
            self.db.add(cloned_target)
            await self.db.flush()
            cloned.targets.append(cloned_target)

        # Update clone count
        shared.clone_count += 1

        await self.db.commit()
        await self.db.refresh(cloned)

        return cloned

    async def increment_view_count(self, shared_investigation_id: int):
        """Increment view count for a shared investigation."""
        result = await self.db.execute(
            select(SharedInvestigation).where(SharedInvestigation.id == shared_investigation_id)
        )
        shared = result.scalar_one_or_none()

        if shared:
            shared.view_count += 1
            await self.db.commit()

    async def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending shared investigations (based on recent activity)."""
        # Calculate trend score based on recent likes, views, and comments
        result = await self.db.execute(
            select(SharedInvestigation, User)
            .join(User, SharedInvestigation.shared_by == User.id)
            .where(SharedInvestigation.visibility == VisibilityLevel.PUBLIC)
            .order_by(
                desc(SharedInvestigation.like_count + SharedInvestigation.view_count)
            )
            .limit(limit)
        )
        trending = result.all()

        return [
            {
                'id': shared.id,
                'title': shared.title,
                'description': shared.description,
                'shared_by': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                },
                'like_count': shared.like_count,
                'view_count': shared.view_count,
                'trend_score': shared.like_count + shared.view_count
            }
            for shared, user in trending
        ]
