"""Team and collaboration system."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.gamification_models import Team, TeamRole, VisibilityLevel, UserNotification, NotificationType, team_members
from database.models import User, Investigation


class TeamSystem:
    """
    Team and collaboration features:
    - Team creation
    - Shared investigations
    - Team achievements
    - Team leaderboards
    - Collaboration tools
    - Team chat
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_team(
        self,
        name: str,
        description: str,
        created_by: int,
        visibility: VisibilityLevel = VisibilityLevel.PRIVATE,
        invite_only: bool = True
    ) -> Team:
        """
        Create a new team.

        Args:
            name: Team name
            description: Team description
            created_by: User ID creating the team
            visibility: Team visibility
            invite_only: Whether team is invite-only

        Returns:
            Created team
        """
        team = Team(
            name=name,
            description=description,
            created_by=created_by,
            visibility=visibility,
            invite_only=invite_only,
            member_count=1
        )

        self.db.add(team)
        await self.db.flush()

        # Add creator as owner
        # Note: Using raw SQL for association table
        from sqlalchemy import insert
        stmt = team_members.insert().values(
            team_id=team.id,
            user_id=created_by,
            role=TeamRole.OWNER
        )
        await self.db.execute(stmt)

        await self.db.commit()
        await self.db.refresh(team)

        return team

    async def add_member(
        self,
        team_id: int,
        user_id: int,
        role: TeamRole = TeamRole.MEMBER
    ) -> Dict[str, Any]:
        """
        Add a member to a team.

        Args:
            team_id: Team ID
            user_id: User ID to add
            role: Role to assign

        Returns:
            Result dictionary
        """
        # Get team
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return {'success': False, 'error': 'Team not found'}

        # Check if user already a member
        from sqlalchemy import select as sa_select
        stmt = sa_select(team_members).where(
            and_(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        existing = result.first()

        if existing:
            return {'success': False, 'error': 'User already a member'}

        # Add member
        from sqlalchemy import insert
        stmt = team_members.insert().values(
            team_id=team_id,
            user_id=user_id,
            role=role
        )
        await self.db.execute(stmt)

        # Update member count
        team.member_count += 1

        # Create notification
        notification = UserNotification(
            user_id=user_id,
            notification_type=NotificationType.TEAM_INVITE,
            title=f"Welcome to {team.name}!",
            message=f"You've been added to the team {team.name}",
            data={'team_id': team_id, 'team_name': team.name}
        )
        self.db.add(notification)

        await self.db.commit()

        return {
            'success': True,
            'team_id': team_id,
            'user_id': user_id,
            'role': role.value
        }

    async def remove_member(
        self,
        team_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Remove a member from a team."""
        # Delete from association table
        from sqlalchemy import delete
        stmt = delete(team_members).where(
            and_(
                team_members.c.team_id == team_id,
                team_members.c.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)

        if result.rowcount > 0:
            # Update member count
            team_result = await self.db.execute(
                select(Team).where(Team.id == team_id)
            )
            team = team_result.scalar_one_or_none()
            if team:
                team.member_count -= 1

            await self.db.commit()

            return {'success': True}

        return {'success': False, 'error': 'Member not found'}

    async def get_team_members(self, team_id: int) -> List[Dict[str, Any]]:
        """Get all members of a team."""
        from sqlalchemy import select as sa_select

        # Join team_members with users
        stmt = (
            sa_select(User, team_members.c.role, team_members.c.joined_at)
            .join(team_members, User.id == team_members.c.user_id)
            .where(team_members.c.team_id == team_id)
        )

        result = await self.db.execute(stmt)
        members = result.all()

        return [
            {
                'user_id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'role': role.value,
                'joined_at': joined_at.isoformat()
            }
            for user, role, joined_at in members
        ]

    async def share_investigation_with_team(
        self,
        investigation_id: int,
        team_id: int
    ) -> Dict[str, Any]:
        """Share an investigation with a team."""
        # Get investigation
        result = await self.db.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()

        if not investigation:
            return {'success': False, 'error': 'Investigation not found'}

        # Get team
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return {'success': False, 'error': 'Team not found'}

        # Add team_id to investigation metadata
        metadata = investigation.metadata or {}
        shared_teams = metadata.get('shared_teams', [])
        if team_id not in shared_teams:
            shared_teams.append(team_id)
            metadata['shared_teams'] = shared_teams
            investigation.metadata = metadata

        await self.db.commit()

        return {
            'success': True,
            'investigation_id': investigation_id,
            'team_id': team_id
        }

    async def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics."""
        # Get team
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return {'error': 'Team not found'}

        # Get shared investigations
        result = await self.db.execute(
            select(func.count(Investigation.id))
            .where(Investigation.metadata.op('@>')('{"shared_teams": [' + str(team_id) + ']}'))
        )
        shared_investigations = result.scalar() or 0

        return {
            'team_id': team.id,
            'name': team.name,
            'member_count': team.member_count,
            'total_points': team.total_points,
            'shared_investigations': shared_investigations,
            'created_at': team.created_at.isoformat()
        }

    async def get_user_teams(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all teams a user is a member of."""
        from sqlalchemy import select as sa_select

        stmt = (
            sa_select(Team, team_members.c.role)
            .join(team_members, Team.id == team_members.c.team_id)
            .where(team_members.c.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        teams = result.all()

        return [
            {
                'id': team.id,
                'name': team.name,
                'description': team.description,
                'member_count': team.member_count,
                'total_points': team.total_points,
                'role': role.value,
                'created_at': team.created_at.isoformat()
            }
            for team, role in teams
        ]

    async def update_team_points(self, team_id: int, points: int):
        """Update team's total points."""
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if team:
            team.total_points += points
            await self.db.commit()
