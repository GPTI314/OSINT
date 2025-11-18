"""Points and leveling system."""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import (
    UserProgress, PointHistory, UserNotification, NotificationType
)


class PointsSystem:
    """
    Points and leveling system:
    - Points for actions
    - Experience points (XP)
    - Levels and unlocks
    - Daily bonuses
    - Streak rewards
    """

    # Point values for different actions
    POINT_VALUES = {
        'create_investigation': 10,
        'complete_scrape': 5,
        'discover_finding': 20,
        'correlate_data': 15,
        'detect_threat': 50,
        'share_finding': 5,
        'complete_tutorial': 25,
        'daily_login': 5,
        'streak_bonus': 10,
        'join_team': 15,
        'collaborate': 20,
        'automate_task': 10,
        'create_workflow': 25,
        'use_ai_assist': 2,
        'complete_challenge': 50,
        'reach_milestone': 100,
    }

    # XP values (usually same or slightly higher than points)
    XP_VALUES = {
        'create_investigation': 25,
        'complete_scrape': 10,
        'discover_finding': 50,
        'correlate_data': 30,
        'detect_threat': 100,
        'share_finding': 10,
        'complete_tutorial': 50,
        'daily_login': 10,
        'streak_bonus': 20,
        'join_team': 30,
        'collaborate': 40,
        'automate_task': 20,
        'create_workflow': 50,
        'use_ai_assist': 5,
        'complete_challenge': 100,
        'reach_milestone': 200,
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_user_progress(self, user_id: int) -> UserProgress:
        """Ensure user progress record exists."""
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            user_progress = UserProgress(
                user_id=user_id,
                total_points=0,
                current_level=1,
                current_level_xp=0,
                next_level_xp=100
            )
            self.db.add(user_progress)
            await self.db.commit()
            await self.db.refresh(user_progress)

        return user_progress

    async def award_points(
        self,
        user_id: int,
        action: str,
        multiplier: float = 1.0,
        resource_type: str = None,
        resource_id: int = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Award points and XP for an action.

        Args:
            user_id: User ID
            action: Action performed
            multiplier: Multiplier for bonus events
            resource_type: Type of resource (investigation, scraping_job, etc.)
            resource_id: ID of the resource
            metadata: Additional metadata

        Returns:
            Dict with points awarded, XP awarded, level info
        """
        user_progress = await self.ensure_user_progress(user_id)

        # Get base points and XP
        base_points = self.POINT_VALUES.get(action, 0)
        base_xp = self.XP_VALUES.get(action, 0)

        # Apply multiplier
        points = int(base_points * multiplier)
        xp = int(base_xp * multiplier)

        # Update user progress
        user_progress.total_points += points
        user_progress.current_level_xp += xp

        # Record in history
        point_history = PointHistory(
            user_progress_id=user_progress.id,
            action=action,
            points=points,
            xp=xp,
            multiplier=multiplier,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {}
        )
        self.db.add(point_history)

        # Update activity stats
        await self._update_activity_stats(user_progress, action)

        # Check for streak bonus
        streak_bonus = await self._check_streak(user_progress)

        # Check for level up
        level_up_data = await self.check_level_up(user_progress.id)

        await self.db.commit()

        return {
            'points_awarded': points,
            'xp_awarded': xp,
            'total_points': user_progress.total_points,
            'current_level': user_progress.current_level,
            'current_level_xp': user_progress.current_level_xp,
            'next_level_xp': user_progress.next_level_xp,
            'level_up': level_up_data,
            'streak_bonus': streak_bonus
        }

    async def _update_activity_stats(self, user_progress: UserProgress, action: str):
        """Update user activity statistics."""
        if action == 'create_investigation':
            user_progress.investigations_created += 1
        elif action == 'complete_scrape':
            user_progress.scrapes_completed += 1
        elif action == 'discover_finding':
            user_progress.findings_discovered += 1
        elif action == 'correlate_data':
            user_progress.correlations_found += 1
        elif action == 'detect_threat':
            user_progress.threats_detected += 1
        elif action == 'share_finding':
            user_progress.findings_shared += 1
        elif action == 'collaborate':
            user_progress.collaborations += 1
        elif action == 'automate_task':
            user_progress.tasks_automated += 1
        elif action == 'create_workflow':
            user_progress.workflows_created += 1
        elif action == 'use_ai_assist':
            user_progress.ai_assists_used += 1

    async def _check_streak(self, user_progress: UserProgress) -> Optional[Dict]:
        """Check and update login streak."""
        today = datetime.utcnow().date()
        last_activity = user_progress.last_activity_date

        if last_activity:
            last_date = last_activity.date()
            days_diff = (today - last_date).days

            if days_diff == 0:
                # Same day, no change
                return None
            elif days_diff == 1:
                # Consecutive day, increment streak
                user_progress.current_streak += 1
                user_progress.last_activity_date = datetime.utcnow()

                # Update longest streak
                if user_progress.current_streak > user_progress.longest_streak:
                    user_progress.longest_streak = user_progress.current_streak

                # Award streak bonus
                if user_progress.current_streak % 7 == 0:  # Weekly bonus
                    bonus = {
                        'streak_days': user_progress.current_streak,
                        'bonus_points': 50,
                        'bonus_xp': 100
                    }
                    user_progress.total_points += bonus['bonus_points']
                    user_progress.current_level_xp += bonus['bonus_xp']
                    return bonus
            else:
                # Streak broken
                user_progress.current_streak = 1
                user_progress.last_activity_date = datetime.utcnow()
        else:
            # First activity
            user_progress.current_streak = 1
            user_progress.last_activity_date = datetime.utcnow()

        return None

    async def check_level_up(self, user_progress_id: int) -> Optional[Dict]:
        """Check if user should level up."""
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.id == user_progress_id)
        )
        user_progress = result.scalar_one()

        levels_gained = 0
        rewards = []

        while user_progress.current_level_xp >= user_progress.next_level_xp:
            # Level up!
            user_progress.current_level_xp -= user_progress.next_level_xp
            user_progress.current_level += 1
            levels_gained += 1

            # Calculate next level XP requirement (exponential growth)
            user_progress.next_level_xp = self.calculate_next_level_xp(user_progress.current_level)

            # Get level rewards
            level_rewards = await self.get_level_rewards(user_progress.current_level)
            rewards.extend(level_rewards)

            # Create notification
            notification = UserNotification(
                user_id=user_progress.user_id,
                notification_type=NotificationType.LEVEL_UP,
                title=f"Level Up! You're now level {user_progress.current_level}!",
                message=f"Congratulations! You've reached level {user_progress.current_level}!",
                data={
                    'new_level': user_progress.current_level,
                    'rewards': level_rewards
                }
            )
            self.db.add(notification)

        if levels_gained > 0:
            await self.db.commit()
            return {
                'levels_gained': levels_gained,
                'new_level': user_progress.current_level,
                'rewards': rewards
            }

        return None

    def calculate_next_level_xp(self, level: int) -> int:
        """Calculate XP required for next level."""
        # Exponential growth formula
        # Level 1-10: 100 * level
        # Level 11-25: 100 * level^1.2
        # Level 26+: 100 * level^1.5
        if level <= 10:
            return int(100 * level)
        elif level <= 25:
            return int(100 * (level ** 1.2))
        else:
            return int(100 * (level ** 1.5))

    async def get_level_rewards(self, level: int) -> List[Dict]:
        """Get rewards for reaching a level."""
        from .reward_system import RewardSystem

        rewards = []

        # Feature unlocks at specific levels
        feature_unlocks = {
            5: ['advanced_filters', 'custom_dashboards'],
            10: ['api_access', 'webhooks'],
            15: ['team_creation', 'collaboration_tools'],
            20: ['ml_models', 'automation_workflows'],
            25: ['advanced_analytics', 'custom_reports'],
            30: ['premium_themes', 'custom_integrations'],
            50: ['ai_copilot', 'unlimited_automations'],
            100: ['master_tools', 'exclusive_features']
        }

        if level in feature_unlocks:
            for feature in feature_unlocks[level]:
                rewards.append({
                    'type': 'feature_unlock',
                    'feature_id': feature,
                    'level': level
                })

        # Bonus points at milestone levels
        if level % 10 == 0:
            bonus_points = level * 10
            rewards.append({
                'type': 'bonus_points',
                'points': bonus_points
            })

        return rewards

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        user_progress = await self.ensure_user_progress(user_id)

        # Calculate level progress percentage
        level_progress = int((user_progress.current_level_xp / user_progress.next_level_xp) * 100)

        # Get recent point history
        result = await self.db.execute(
            select(PointHistory)
            .where(PointHistory.user_progress_id == user_progress.id)
            .order_by(PointHistory.earned_at.desc())
            .limit(10)
        )
        recent_history = result.scalars().all()

        return {
            'total_points': user_progress.total_points,
            'current_level': user_progress.current_level,
            'current_level_xp': user_progress.current_level_xp,
            'next_level_xp': user_progress.next_level_xp,
            'level_progress': level_progress,
            'current_streak': user_progress.current_streak,
            'longest_streak': user_progress.longest_streak,
            'statistics': {
                'investigations_created': user_progress.investigations_created,
                'scrapes_completed': user_progress.scrapes_completed,
                'findings_discovered': user_progress.findings_discovered,
                'correlations_found': user_progress.correlations_found,
                'threats_detected': user_progress.threats_detected,
                'patterns_identified': user_progress.patterns_identified,
                'tasks_automated': user_progress.tasks_automated,
                'workflows_created': user_progress.workflows_created,
                'ai_assists_used': user_progress.ai_assists_used,
                'findings_shared': user_progress.findings_shared,
                'collaborations': user_progress.collaborations,
            },
            'recent_activity': [
                {
                    'action': ph.action,
                    'points': ph.points,
                    'xp': ph.xp,
                    'earned_at': ph.earned_at.isoformat()
                }
                for ph in recent_history
            ]
        }

    async def award_daily_login_bonus(self, user_id: int) -> Dict[str, Any]:
        """Award daily login bonus if eligible."""
        user_progress = await self.ensure_user_progress(user_id)

        today = datetime.utcnow().date()
        last_activity = user_progress.last_activity_date

        # Check if already awarded today
        if last_activity and last_activity.date() == today:
            return {
                'awarded': False,
                'reason': 'already_claimed_today'
            }

        # Award daily login bonus
        result = await self.award_points(
            user_id=user_id,
            action='daily_login',
            metadata={'date': today.isoformat()}
        )

        result['awarded'] = True
        return result
