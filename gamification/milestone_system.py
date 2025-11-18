"""Milestone and goal tracking system."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import (
    Milestone, UserProgress, UserNotification, NotificationType
)


class MilestoneSystem:
    """
    Milestone and goal system:
    - Set personal goals
    - Track progress
    - Celebrate achievements
    - Visual progress tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_milestone(
        self,
        user_id: int,
        title: str,
        description: str,
        goal_type: str,
        target_value: int,
        deadline: Optional[datetime] = None,
        points_reward: int = 0,
        xp_reward: int = 0
    ) -> Milestone:
        """
        Create a new milestone for a user.

        Args:
            user_id: User ID
            title: Milestone title
            description: Milestone description
            goal_type: Type of goal (investigations, scrapes, findings, etc.)
            target_value: Target value to reach
            deadline: Optional deadline
            points_reward: Points awarded on completion
            xp_reward: XP awarded on completion

        Returns:
            Created milestone
        """
        milestone = Milestone(
            user_id=user_id,
            title=title,
            description=description,
            goal_type=goal_type,
            target_value=target_value,
            current_value=0,
            deadline=deadline,
            points_reward=points_reward,
            xp_reward=xp_reward
        )
        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)

        return milestone

    async def update_milestone_progress(self, user_id: int):
        """Update progress for all user milestones."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return

        # Get active milestones
        result = await self.db.execute(
            select(Milestone).where(
                and_(
                    Milestone.user_id == user_id,
                    Milestone.is_completed == False
                )
            )
        )
        milestones = result.scalars().all()

        # Update each milestone
        for milestone in milestones:
            current_value = self._get_current_value(milestone.goal_type, user_progress)
            milestone.current_value = current_value

            # Check if completed
            if current_value >= milestone.target_value:
                await self._complete_milestone(milestone, user_progress)

        await self.db.commit()

    def _get_current_value(self, goal_type: str, user_progress: UserProgress) -> int:
        """Get current value for a goal type."""
        mapping = {
            'investigations': user_progress.investigations_created,
            'scrapes': user_progress.scrapes_completed,
            'findings': user_progress.findings_discovered,
            'correlations': user_progress.correlations_found,
            'threats': user_progress.threats_detected,
            'patterns': user_progress.patterns_identified,
            'automation': user_progress.tasks_automated,
            'workflows': user_progress.workflows_created,
            'ai_assists': user_progress.ai_assists_used,
            'shares': user_progress.findings_shared,
            'collaborations': user_progress.collaborations,
            'level': user_progress.current_level,
            'points': user_progress.total_points
        }
        return mapping.get(goal_type, 0)

    async def _complete_milestone(self, milestone: Milestone, user_progress: UserProgress):
        """Complete a milestone and award rewards."""
        milestone.is_completed = True
        milestone.completed_at = datetime.utcnow()

        # Award rewards
        if milestone.points_reward > 0:
            user_progress.total_points += milestone.points_reward

        if milestone.xp_reward > 0:
            user_progress.current_level_xp += milestone.xp_reward

        # Create notification
        notification = UserNotification(
            user_id=milestone.user_id,
            notification_type=NotificationType.MILESTONE,
            title=f"Milestone Completed: {milestone.title}!",
            message=f"Congratulations! You've completed the milestone: {milestone.title}",
            data={
                'milestone_id': milestone.id,
                'points_reward': milestone.points_reward,
                'xp_reward': milestone.xp_reward
            }
        )
        self.db.add(notification)

        # Check for level up
        from .points_system import PointsSystem
        points_system = PointsSystem(self.db)
        await points_system.check_level_up(user_progress.id)

    async def get_user_milestones(
        self,
        user_id: int,
        include_completed: bool = True
    ) -> Dict[str, Any]:
        """Get all milestones for a user."""
        query = select(Milestone).where(Milestone.user_id == user_id)

        if not include_completed:
            query = query.where(Milestone.is_completed == False)

        result = await self.db.execute(query.order_by(Milestone.created_at.desc()))
        milestones = result.scalars().all()

        active_milestones = [m for m in milestones if not m.is_completed]
        completed_milestones = [m for m in milestones if m.is_completed]

        return {
            'total': len(milestones),
            'active': len(active_milestones),
            'completed': len(completed_milestones),
            'milestones': [
                {
                    'id': m.id,
                    'title': m.title,
                    'description': m.description,
                    'goal_type': m.goal_type,
                    'target_value': m.target_value,
                    'current_value': m.current_value,
                    'progress_percentage': int((m.current_value / m.target_value) * 100) if m.target_value > 0 else 0,
                    'is_completed': m.is_completed,
                    'completed_at': m.completed_at.isoformat() if m.completed_at else None,
                    'deadline': m.deadline.isoformat() if m.deadline else None,
                    'points_reward': m.points_reward,
                    'xp_reward': m.xp_reward,
                    'created_at': m.created_at.isoformat()
                }
                for m in milestones
            ]
        }

    async def create_suggested_milestones(self, user_id: int) -> List[Milestone]:
        """Create suggested milestones based on user progress."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return []

        suggestions = []

        # Suggest investigation milestone
        if user_progress.investigations_created < 10:
            suggestions.append({
                'title': 'First 10 Investigations',
                'description': 'Create 10 investigations',
                'goal_type': 'investigations',
                'target_value': 10,
                'points_reward': 100,
                'xp_reward': 200
            })

        # Suggest scraping milestone
        if user_progress.scrapes_completed < 50:
            suggestions.append({
                'title': 'Data Collection Pro',
                'description': 'Complete 50 scraping jobs',
                'goal_type': 'scrapes',
                'target_value': 50,
                'points_reward': 100,
                'xp_reward': 200
            })

        # Suggest findings milestone
        if user_progress.findings_discovered < 25:
            suggestions.append({
                'title': 'Discovery Master',
                'description': 'Discover 25 findings',
                'goal_type': 'findings',
                'target_value': 25,
                'points_reward': 150,
                'xp_reward': 300
            })

        # Create suggested milestones
        created = []
        for suggestion in suggestions:
            milestone = await self.create_milestone(
                user_id=user_id,
                **suggestion
            )
            created.append(milestone)

        return created
