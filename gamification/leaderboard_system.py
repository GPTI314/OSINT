"""Leaderboard system for gamification."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import Leaderboard, UserProgress, Team
from database.models import User


class LeaderboardSystem:
    """
    Leaderboard system:
    - Global leaderboards
    - Team leaderboards
    - Category leaderboards
    - Weekly/monthly rankings
    - Historical rankings
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_leaderboard(
        self,
        user_id: int,
        category: str,
        score: int,
        period: str = 'all_time',
        metadata: Dict = None
    ):
        """
        Update leaderboard entry for a user.

        Args:
            user_id: User ID
            category: Leaderboard category (overall, investigations, scraping, etc.)
            score: User's score
            period: Time period (all_time, weekly, monthly, daily)
            metadata: Additional metadata
        """
        # Check if entry exists
        result = await self.db.execute(
            select(Leaderboard).where(
                and_(
                    Leaderboard.user_id == user_id,
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
        )
        entry = result.scalar_one_or_none()

        if entry:
            entry.score = score
            entry.metadata = metadata or {}
        else:
            entry = Leaderboard(
                user_id=user_id,
                category=category,
                period=period,
                score=score,
                metadata=metadata or {}
            )
            self.db.add(entry)

        await self.db.commit()

        # Update ranks
        await self._update_ranks(category, period)

    async def _update_ranks(self, category: str, period: str):
        """Update ranks for a category and period."""
        # Get all entries for this category and period, ordered by score
        result = await self.db.execute(
            select(Leaderboard)
            .where(
                and_(
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
            .order_by(desc(Leaderboard.score))
        )
        entries = result.scalars().all()

        # Update ranks
        for rank, entry in enumerate(entries, start=1):
            entry.rank = rank

        await self.db.commit()

    async def get_leaderboard(
        self,
        category: str = 'overall',
        period: str = 'all_time',
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get leaderboard entries.

        Args:
            category: Leaderboard category
            period: Time period
            limit: Number of entries to return
            offset: Offset for pagination

        Returns:
            Dict with leaderboard entries and metadata
        """
        # Get entries
        result = await self.db.execute(
            select(Leaderboard, User)
            .join(User)
            .where(
                and_(
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
            .order_by(Leaderboard.rank)
            .limit(limit)
            .offset(offset)
        )
        entries = result.all()

        # Get total count
        count_result = await self.db.execute(
            select(func.count(Leaderboard.id))
            .where(
                and_(
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
        )
        total_count = count_result.scalar()

        return {
            'category': category,
            'period': period,
            'total_entries': total_count,
            'entries': [
                {
                    'rank': entry.Leaderboard.rank,
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'score': entry.Leaderboard.score,
                    'metadata': entry.Leaderboard.metadata
                }
                for entry in entries
            ]
        }

    async def get_user_rank(
        self,
        user_id: int,
        category: str = 'overall',
        period: str = 'all_time'
    ) -> Optional[Dict[str, Any]]:
        """Get user's rank in a leaderboard."""
        result = await self.db.execute(
            select(Leaderboard)
            .where(
                and_(
                    Leaderboard.user_id == user_id,
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
        )
        entry = result.scalar_one_or_none()

        if not entry:
            return None

        # Get total entries
        count_result = await self.db.execute(
            select(func.count(Leaderboard.id))
            .where(
                and_(
                    Leaderboard.category == category,
                    Leaderboard.period == period
                )
            )
        )
        total_entries = count_result.scalar()

        # Calculate percentile
        percentile = 100 - ((entry.rank / total_entries) * 100) if total_entries > 0 else 0

        return {
            'rank': entry.rank,
            'score': entry.score,
            'total_entries': total_entries,
            'percentile': round(percentile, 2)
        }

    async def update_all_leaderboards(self, user_id: int):
        """Update all leaderboard categories for a user."""
        # Get user progress
        result = await self.db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        user_progress = result.scalar_one_or_none()

        if not user_progress:
            return

        # Update overall leaderboard
        await self.update_leaderboard(
            user_id=user_id,
            category='overall',
            score=user_progress.total_points,
            period='all_time'
        )

        # Update category-specific leaderboards
        categories = {
            'investigations': user_progress.investigations_created,
            'scraping': user_progress.scrapes_completed,
            'findings': user_progress.findings_discovered,
            'correlations': user_progress.correlations_found,
            'threats': user_progress.threats_detected,
            'automation': user_progress.tasks_automated,
            'collaboration': user_progress.collaborations
        }

        for category, score in categories.items():
            await self.update_leaderboard(
                user_id=user_id,
                category=category,
                score=score,
                period='all_time'
            )

    async def get_team_leaderboard(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get team leaderboard."""
        result = await self.db.execute(
            select(Team)
            .order_by(desc(Team.total_points))
            .limit(limit)
            .offset(offset)
        )
        teams = result.scalars().all()

        # Get total count
        count_result = await self.db.execute(
            select(func.count(Team.id))
        )
        total_count = count_result.scalar()

        return {
            'category': 'teams',
            'total_entries': total_count,
            'entries': [
                {
                    'rank': idx + 1 + offset,
                    'team_id': team.id,
                    'team_name': team.name,
                    'total_points': team.total_points,
                    'member_count': team.member_count
                }
                for idx, team in enumerate(teams)
            ]
        }

    async def get_nearby_ranks(
        self,
        user_id: int,
        category: str = 'overall',
        period: str = 'all_time',
        context_size: int = 5
    ) -> Dict[str, Any]:
        """Get leaderboard entries around user's rank."""
        # Get user's rank
        user_rank_data = await self.get_user_rank(user_id, category, period)

        if not user_rank_data:
            return {
                'user_rank': None,
                'entries': []
            }

        user_rank = user_rank_data['rank']

        # Get entries around user's rank
        start_rank = max(1, user_rank - context_size)
        end_rank = user_rank + context_size

        result = await self.db.execute(
            select(Leaderboard, User)
            .join(User)
            .where(
                and_(
                    Leaderboard.category == category,
                    Leaderboard.period == period,
                    Leaderboard.rank >= start_rank,
                    Leaderboard.rank <= end_rank
                )
            )
            .order_by(Leaderboard.rank)
        )
        entries = result.all()

        return {
            'user_rank': user_rank,
            'user_score': user_rank_data['score'],
            'percentile': user_rank_data['percentile'],
            'entries': [
                {
                    'rank': entry.Leaderboard.rank,
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'score': entry.Leaderboard.score,
                    'is_current_user': user.id == user_id
                }
                for entry in entries
            ]
        }
