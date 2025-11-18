"""Achievement system for gamification."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import (
    Achievement, UserAchievement, UserProgress,
    AchievementCategory, BadgeTier, UserNotification, NotificationType
)
from .achievement_definitions import ACHIEVEMENT_DEFINITIONS


class AchievementSystem:
    """
    Comprehensive achievement system:
    - Badges for milestones
    - Points for actions
    - Levels and progression
    - Unlockable features
    - Streaks and daily challenges
    - Leaderboards
    - Rewards and perks
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_achievements(self):
        """Initialize achievement definitions in database."""
        for achievement_data in ACHIEVEMENT_DEFINITIONS:
            # Check if achievement exists
            result = await self.db.execute(
                select(Achievement).where(Achievement.achievement_id == achievement_data["achievement_id"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                achievement = Achievement(**achievement_data)
                self.db.add(achievement)

        await self.db.commit()

    async def check_achievements(self, user_id: int, action: str, context: Dict[str, Any] = None):
        """
        Check and award achievements based on actions.

        Args:
            user_id: User ID
            action: Action performed (e.g., 'create_investigation', 'complete_scrape')
            context: Additional context data
        """
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return

        # Check for achievements based on action
        achievements_to_check = self._get_achievements_for_action(action, user_progress)

        for achievement_def in achievements_to_check:
            # Check if already unlocked
            result = await self.db.execute(
                select(UserAchievement).join(Achievement).where(
                    and_(
                        UserAchievement.user_progress_id == user_progress.id,
                        Achievement.achievement_id == achievement_def["achievement_id"]
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if not existing:
                # Check if requirements met
                if self._check_requirements(achievement_def, user_progress, context):
                    await self.award_achievement(user_progress.id, achievement_def["achievement_id"])

    def _get_achievements_for_action(self, action: str, user_progress: UserProgress) -> List[Dict]:
        """Get achievements that could be unlocked by this action."""
        action_achievement_map = {
            'create_investigation': ['first_investigation', '10_investigations', '50_investigations', '100_investigations'],
            'complete_scrape': ['first_scrape', '100_scrapes', '500_scrapes', '1000_scrapes'],
            'discover_finding': ['first_finding', '50_findings', '200_findings', '500_findings'],
            'correlate_data': ['first_correlation', 'correlation_master', 'correlation_expert'],
            'detect_threat': ['first_threat', 'threat_hunter', 'threat_master'],
            'identify_pattern': ['pattern_finder', 'pattern_master'],
            'automate_task': ['automation_starter', 'auto_100', 'auto_500'],
            'create_workflow': ['workflow_creator', 'workflow_master'],
            'use_ai': ['ai_assistant', 'ai_power_user'],
            'join_team': ['team_player'],
            'share_finding': ['sharing_is_caring', 'share_master'],
            'collaborate': ['collaborator', 'collaboration_master'],
            'level_up': ['level_10', 'level_25', 'level_50', 'osint_master'],
        }

        achievement_ids = action_achievement_map.get(action, [])
        return [a for a in ACHIEVEMENT_DEFINITIONS if a['achievement_id'] in achievement_ids]

    def _check_requirements(self, achievement_def: Dict, user_progress: UserProgress, context: Dict = None) -> bool:
        """Check if achievement requirements are met."""
        req_type = achievement_def['requirement_type']
        req_value = achievement_def.get('requirement_value', 0)

        if req_type == 'count_investigations':
            return user_progress.investigations_created >= req_value
        elif req_type == 'count_scrapes':
            return user_progress.scrapes_completed >= req_value
        elif req_type == 'count_findings':
            return user_progress.findings_discovered >= req_value
        elif req_type == 'count_correlations':
            return user_progress.correlations_found >= req_value
        elif req_type == 'count_threats':
            return user_progress.threats_detected >= req_value
        elif req_type == 'count_patterns':
            return user_progress.patterns_identified >= req_value
        elif req_type == 'count_automation':
            return user_progress.tasks_automated >= req_value
        elif req_type == 'count_workflows':
            return user_progress.workflows_created >= req_value
        elif req_type == 'count_ai_assists':
            return user_progress.ai_assists_used >= req_value
        elif req_type == 'count_shares':
            return user_progress.findings_shared >= req_value
        elif req_type == 'count_collaborations':
            return user_progress.collaborations >= req_value
        elif req_type == 'level':
            return user_progress.current_level >= req_value
        elif req_type == 'streak':
            return user_progress.current_streak >= req_value
        elif req_type == 'time':
            if context and 'investigation_time' in context:
                return context['investigation_time'] <= req_value
            return False
        elif req_type == 'special':
            # Handle special achievements
            req_data = achievement_def.get('requirement_data', {})
            return self._check_special_requirement(req_data, user_progress, context)

        return False

    def _check_special_requirement(self, req_data: Dict, user_progress: UserProgress, context: Dict = None) -> bool:
        """Check special achievement requirements."""
        # Implement custom logic for special achievements
        return True

    async def award_achievement(self, user_progress_id: int, achievement_id: str):
        """Award achievement to user."""
        # Get achievement
        result = await self.db.execute(
            select(Achievement).where(Achievement.achievement_id == achievement_id)
        )
        achievement = result.scalar_one_or_none()

        if not achievement:
            return

        # Create user achievement
        user_achievement = UserAchievement(
            user_progress_id=user_progress_id,
            achievement_id=achievement.id,
            unlocked_at=datetime.utcnow(),
            progress=100
        )
        self.db.add(user_achievement)

        # Update achievement stats
        achievement.total_awarded += 1

        # Get user progress to get user_id
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.id == user_progress_id)
        )
        user_progress = result.scalar_one()

        # Award points and XP
        user_progress.total_points += achievement.points_reward
        user_progress.current_level_xp += achievement.xp_reward

        # Check for level up
        from .points_system import PointsSystem
        points_system = PointsSystem(self.db)
        await points_system.check_level_up(user_progress_id)

        # Create notification
        notification = UserNotification(
            user_id=user_progress.user_id,
            notification_type=NotificationType.ACHIEVEMENT,
            title=f"Achievement Unlocked: {achievement.name}!",
            message=achievement.unlock_message or achievement.description,
            data={
                'achievement_id': achievement.achievement_id,
                'points': achievement.points_reward,
                'xp': achievement.xp_reward,
                'icon': achievement.icon,
                'tier': achievement.tier.value
            }
        )
        self.db.add(notification)

        await self.db.commit()

        return {
            'achievement': achievement,
            'unlocked_at': user_achievement.unlocked_at
        }

    async def get_user_achievements(self, user_id: int) -> Dict[str, Any]:
        """Get all achievements for a user."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return {
                'total': 0,
                'unlocked': [],
                'locked': []
            }

        # Get unlocked achievements
        result = await self.db.execute(
            select(UserAchievement, Achievement)
            .join(Achievement)
            .where(UserAchievement.user_progress_id == user_progress.id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        unlocked_achievements = result.all()

        # Get all achievements
        result = await self.db.execute(select(Achievement))
        all_achievements = result.scalars().all()

        unlocked_ids = {ua.achievement_id for ua, _ in unlocked_achievements}
        locked_achievements = [a for a in all_achievements if a.id not in unlocked_ids]

        return {
            'total': len(all_achievements),
            'unlocked_count': len(unlocked_achievements),
            'unlocked': [
                {
                    'id': achievement.achievement_id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'category': achievement.category.value,
                    'tier': achievement.tier.value,
                    'icon': achievement.icon,
                    'unlocked_at': user_achievement.unlocked_at.isoformat(),
                    'points_reward': achievement.points_reward,
                    'xp_reward': achievement.xp_reward
                }
                for user_achievement, achievement in unlocked_achievements
            ],
            'locked': [
                {
                    'id': achievement.achievement_id,
                    'name': achievement.name if not achievement.is_secret else "???",
                    'description': achievement.description if not achievement.is_secret else "Secret achievement - unlock to reveal!",
                    'category': achievement.category.value,
                    'tier': achievement.tier.value,
                    'icon': achievement.icon if not achievement.is_secret else "🔒",
                    'points_reward': achievement.points_reward,
                    'xp_reward': achievement.xp_reward,
                    'is_secret': achievement.is_secret
                }
                for achievement in locked_achievements
            ]
        }

    async def get_progress_to_achievement(self, user_id: int, achievement_id: str) -> Dict[str, Any]:
        """Get user's progress toward a specific achievement."""
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return None

        result = await self.db.execute(
            select(Achievement).where(Achievement.achievement_id == achievement_id)
        )
        achievement = result.scalar_one_or_none()

        if not achievement:
            return None

        # Calculate current progress
        current_value = 0
        target_value = achievement.requirement_value

        if achievement.requirement_type == 'count_investigations':
            current_value = user_progress.investigations_created
        elif achievement.requirement_type == 'count_scrapes':
            current_value = user_progress.scrapes_completed
        elif achievement.requirement_type == 'count_findings':
            current_value = user_progress.findings_discovered
        # ... add more as needed

        progress_percentage = min(100, int((current_value / target_value) * 100)) if target_value > 0 else 0

        return {
            'achievement_id': achievement.achievement_id,
            'name': achievement.name,
            'current_value': current_value,
            'target_value': target_value,
            'progress_percentage': progress_percentage,
            'is_unlocked': progress_percentage >= 100
        }

    async def showcase_achievement(self, user_id: int, achievement_id: str, showcase: bool = True):
        """Set whether to showcase an achievement on profile."""
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return False

        result = await self.db.execute(
            select(UserAchievement, Achievement)
            .join(Achievement)
            .where(
                and_(
                    UserAchievement.user_progress_id == user_progress.id,
                    Achievement.achievement_id == achievement_id
                )
            )
        )
        user_achievement = result.scalar_one_or_none()

        if user_achievement:
            ua, _ = user_achievement
            ua.is_showcased = showcase
            await self.db.commit()
            return True

        return False
