"""Reward and unlock system."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import (
    UnlockedFeature, UserProgress, UserNotification, NotificationType
)


class RewardSystem:
    """
    Reward and unlock system:
    - Unlock features as you level up
    - Premium features for achievements
    - Custom themes and skins
    - Advanced tools unlock
    - API access unlocks
    """

    # Feature unlocks by level
    LEVEL_UNLOCKS = {
        1: [],  # Everyone starts with basic features
        5: [
            {
                'id': 'advanced_filters',
                'name': 'Advanced Filters',
                'description': 'Use advanced filtering options in searches and reports'
            },
            {
                'id': 'custom_dashboards',
                'name': 'Custom Dashboards',
                'description': 'Create and customize your own dashboard layouts'
            }
        ],
        10: [
            {
                'id': 'api_access',
                'name': 'API Access',
                'description': 'Access the OSINT platform via REST API'
            },
            {
                'id': 'webhooks',
                'name': 'Webhooks',
                'description': 'Set up webhooks for automated notifications'
            },
            {
                'id': 'export_formats',
                'name': 'Additional Export Formats',
                'description': 'Export data in JSON, XML, and CSV formats'
            }
        ],
        15: [
            {
                'id': 'team_creation',
                'name': 'Team Creation',
                'description': 'Create and manage teams for collaboration'
            },
            {
                'id': 'collaboration_tools',
                'name': 'Collaboration Tools',
                'description': 'Access real-time collaboration features'
            }
        ],
        20: [
            {
                'id': 'ml_models',
                'name': 'Machine Learning Models',
                'description': 'Use ML models for pattern detection and analysis'
            },
            {
                'id': 'automation_workflows',
                'name': 'Automation Workflows',
                'description': 'Create complex automation workflows'
            },
            {
                'id': 'scheduled_tasks',
                'name': 'Scheduled Tasks',
                'description': 'Schedule investigations and reports'
            }
        ],
        25: [
            {
                'id': 'advanced_analytics',
                'name': 'Advanced Analytics',
                'description': 'Access advanced analytics and insights'
            },
            {
                'id': 'custom_reports',
                'name': 'Custom Report Templates',
                'description': 'Create custom report templates'
            }
        ],
        30: [
            {
                'id': 'premium_themes',
                'name': 'Premium Themes',
                'description': 'Access premium UI themes and customization'
            },
            {
                'id': 'custom_integrations',
                'name': 'Custom Integrations',
                'description': 'Build custom integrations with external tools'
            }
        ],
        50: [
            {
                'id': 'ai_copilot',
                'name': 'AI Copilot',
                'description': 'Advanced AI assistant for investigation guidance'
            },
            {
                'id': 'unlimited_automations',
                'name': 'Unlimited Automations',
                'description': 'Create unlimited automation workflows'
            },
            {
                'id': 'priority_support',
                'name': 'Priority Support',
                'description': 'Get priority support and assistance'
            }
        ],
        100: [
            {
                'id': 'master_tools',
                'name': 'Master Tools',
                'description': 'Access exclusive master-level analysis tools'
            },
            {
                'id': 'exclusive_features',
                'name': 'Exclusive Features',
                'description': 'Access to beta features and exclusive tools'
            },
            {
                'id': 'custom_branding',
                'name': 'Custom Branding',
                'description': 'Customize the platform with your own branding'
            }
        ]
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_unlocks(self, user_id: int) -> Dict[str, Any]:
        """Check what features a user can unlock."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return {
                'available_unlocks': [],
                'unlocked_features': [],
                'locked_features': []
            }

        # Get already unlocked features
        result = await self.db.execute(
            select(UnlockedFeature).where(UnlockedFeature.user_id == user_id)
        )
        unlocked = result.scalars().all()
        unlocked_ids = {f.feature_id for f in unlocked}

        # Check what's available to unlock
        available_unlocks = []
        locked_features = []

        for level, features in self.LEVEL_UNLOCKS.items():
            for feature in features:
                if feature['id'] not in unlocked_ids:
                    if user_progress.current_level >= level:
                        # Can unlock now
                        available_unlocks.append({
                            **feature,
                            'unlock_level': level,
                            'can_unlock': True
                        })
                    else:
                        # Locked, needs higher level
                        locked_features.append({
                            **feature,
                            'unlock_level': level,
                            'levels_needed': level - user_progress.current_level
                        })

        return {
            'current_level': user_progress.current_level,
            'available_unlocks': available_unlocks,
            'unlocked_features': [
                {
                    'id': f.feature_id,
                    'name': f.feature_name,
                    'description': f.feature_description,
                    'unlocked_at': f.unlocked_at.isoformat()
                }
                for f in unlocked
            ],
            'locked_features': locked_features
        }

    async def unlock_feature(self, user_id: int, feature_id: str) -> Dict[str, Any]:
        """Unlock a feature for a user."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return {
                'success': False,
                'error': 'User progress not found'
            }

        # Find feature in unlock definitions
        feature_data = None
        required_level = None

        for level, features in self.LEVEL_UNLOCKS.items():
            for feature in features:
                if feature['id'] == feature_id:
                    feature_data = feature
                    required_level = level
                    break
            if feature_data:
                break

        if not feature_data:
            return {
                'success': False,
                'error': 'Feature not found'
            }

        # Check if user meets requirements
        if user_progress.current_level < required_level:
            return {
                'success': False,
                'error': f'Requires level {required_level}',
                'required_level': required_level,
                'current_level': user_progress.current_level
            }

        # Check if already unlocked
        result = await self.db.execute(
            select(UnlockedFeature).where(
                and_(
                    UnlockedFeature.user_id == user_id,
                    UnlockedFeature.feature_id == feature_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {
                'success': False,
                'error': 'Feature already unlocked'
            }

        # Unlock feature
        unlocked_feature = UnlockedFeature(
            user_id=user_id,
            feature_id=feature_id,
            feature_name=feature_data['name'],
            feature_description=feature_data['description'],
            unlock_requirement=f'level_{required_level}'
        )
        self.db.add(unlocked_feature)

        # Create notification
        notification = UserNotification(
            user_id=user_id,
            notification_type=NotificationType.REWARD,
            title=f"Feature Unlocked: {feature_data['name']}!",
            message=f"You've unlocked a new feature: {feature_data['description']}",
            data={
                'feature_id': feature_id,
                'feature_name': feature_data['name']
            }
        )
        self.db.add(notification)

        await self.db.commit()

        return {
            'success': True,
            'feature': {
                'id': feature_id,
                'name': feature_data['name'],
                'description': feature_data['description']
            }
        }

    async def auto_unlock_features(self, user_id: int):
        """Automatically unlock features when user reaches required level."""
        unlocks = await self.check_unlocks(user_id)

        for feature in unlocks['available_unlocks']:
            if feature['can_unlock']:
                await self.unlock_feature(user_id, feature['id'])

    async def get_unlocked_features(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all unlocked features for a user."""
        result = await self.db.execute(
            select(UnlockedFeature)
            .where(UnlockedFeature.user_id == user_id)
            .order_by(UnlockedFeature.unlocked_at.desc())
        )
        features = result.scalars().all()

        return [
            {
                'id': f.feature_id,
                'name': f.feature_name,
                'description': f.feature_description,
                'unlocked_at': f.unlocked_at.isoformat(),
                'unlock_requirement': f.unlock_requirement
            }
            for f in features
        ]

    async def has_feature(self, user_id: int, feature_id: str) -> bool:
        """Check if user has a specific feature unlocked."""
        result = await self.db.execute(
            select(UnlockedFeature).where(
                and_(
                    UnlockedFeature.user_id == user_id,
                    UnlockedFeature.feature_id == feature_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
