"""Gamification API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from auth.jwt_manager import get_current_user
from database.models import User
from gamification import (
    AchievementSystem,
    PointsSystem,
    LeaderboardSystem,
    MilestoneSystem,
    RewardSystem
)
from automation import AIAssistant, SmartAutomation, BatchOperations, TemplateSystem
from social import TeamSystem, SharingSystem

router = APIRouter()


# Pydantic models for request/response
class PointsAwardRequest(BaseModel):
    action: str
    multiplier: float = 1.0
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None


class MilestoneCreateRequest(BaseModel):
    title: str
    description: str
    goal_type: str
    target_value: int
    deadline: Optional[str] = None
    points_reward: int = 0
    xp_reward: int = 0


class TeamCreateRequest(BaseModel):
    name: str
    description: str
    visibility: str = "private"
    invite_only: bool = True


class ShareInvestigationRequest(BaseModel):
    investigation_id: int
    visibility: str = "public"
    title: Optional[str] = None
    description: Optional[str] = None


class CommentRequest(BaseModel):
    content: str


class TemplateCreateRequest(BaseModel):
    name: str
    description: str
    template_data: dict
    category: str
    tags: List[str] = []
    visibility: str = "private"


class BatchImportRequest(BaseModel):
    investigation_id: int
    targets: List[dict]


# ==================== GAMIFICATION ENDPOINTS ====================

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive user gamification profile."""
    points_system = PointsSystem(db)
    achievement_system = AchievementSystem(db)
    reward_system = RewardSystem(db)
    leaderboard_system = LeaderboardSystem(db)

    # Get all profile data
    stats = await points_system.get_user_stats(current_user.id)
    achievements = await achievement_system.get_user_achievements(current_user.id)
    unlocks = await reward_system.check_unlocks(current_user.id)
    rank = await leaderboard_system.get_user_rank(current_user.id)

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name
        },
        "stats": stats,
        "achievements": achievements,
        "unlocks": unlocks,
        "rank": rank
    }


@router.post("/points/award")
async def award_points(
    request: PointsAwardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Award points for an action."""
    points_system = PointsSystem(db)

    result = await points_system.award_points(
        user_id=current_user.id,
        action=request.action,
        multiplier=request.multiplier,
        resource_type=request.resource_type,
        resource_id=request.resource_id
    )

    # Check achievements
    achievement_system = AchievementSystem(db)
    await achievement_system.check_achievements(current_user.id, request.action)

    # Update leaderboards
    leaderboard_system = LeaderboardSystem(db)
    await leaderboard_system.update_all_leaderboards(current_user.id)

    return result


@router.get("/points/stats")
async def get_points_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user points and leveling stats."""
    points_system = PointsSystem(db)
    return await points_system.get_user_stats(current_user.id)


@router.post("/points/daily-bonus")
async def claim_daily_bonus(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Claim daily login bonus."""
    points_system = PointsSystem(db)
    return await points_system.award_daily_login_bonus(current_user.id)


# ==================== ACHIEVEMENTS ====================

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all achievements for user."""
    achievement_system = AchievementSystem(db)
    return await achievement_system.get_user_achievements(current_user.id)


@router.get("/achievements/{achievement_id}/progress")
async def get_achievement_progress(
    achievement_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get progress toward a specific achievement."""
    achievement_system = AchievementSystem(db)
    return await achievement_system.get_progress_to_achievement(current_user.id, achievement_id)


@router.post("/achievements/{achievement_id}/showcase")
async def showcase_achievement(
    achievement_id: str,
    showcase: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set achievement as showcased on profile."""
    achievement_system = AchievementSystem(db)
    result = await achievement_system.showcase_achievement(current_user.id, achievement_id, showcase)

    if result:
        return {"success": True, "achievement_id": achievement_id, "showcased": showcase}

    raise HTTPException(status_code=404, detail="Achievement not found or not unlocked")


# ==================== LEADERBOARDS ====================

@router.get("/leaderboards/{category}")
async def get_leaderboard(
    category: str = "overall",
    period: str = "all_time",
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard for a category."""
    leaderboard_system = LeaderboardSystem(db)
    return await leaderboard_system.get_leaderboard(category, period, limit, offset)


@router.get("/leaderboards/{category}/rank")
async def get_my_rank(
    category: str = "overall",
    period: str = "all_time",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's rank in leaderboard."""
    leaderboard_system = LeaderboardSystem(db)
    return await leaderboard_system.get_user_rank(current_user.id, category, period)


@router.get("/leaderboards/{category}/nearby")
async def get_nearby_ranks(
    category: str = "overall",
    period: str = "all_time",
    context_size: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard entries near user's rank."""
    leaderboard_system = LeaderboardSystem(db)
    return await leaderboard_system.get_nearby_ranks(current_user.id, category, period, context_size)


@router.get("/leaderboards/teams/top")
async def get_team_leaderboard(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get team leaderboard."""
    leaderboard_system = LeaderboardSystem(db)
    return await leaderboard_system.get_team_leaderboard(limit, offset)


# ==================== MILESTONES ====================

@router.get("/milestones")
async def get_milestones(
    include_completed: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user milestones."""
    milestone_system = MilestoneSystem(db)
    return await milestone_system.get_user_milestones(current_user.id, include_completed)


@router.post("/milestones")
async def create_milestone(
    request: MilestoneCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new milestone."""
    milestone_system = MilestoneSystem(db)

    milestone = await milestone_system.create_milestone(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        goal_type=request.goal_type,
        target_value=request.target_value,
        points_reward=request.points_reward,
        xp_reward=request.xp_reward
    )

    return {
        "id": milestone.id,
        "title": milestone.title,
        "goal_type": milestone.goal_type,
        "target_value": milestone.target_value
    }


@router.post("/milestones/suggested")
async def create_suggested_milestones(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create suggested milestones for user."""
    milestone_system = MilestoneSystem(db)
    milestones = await milestone_system.create_suggested_milestones(current_user.id)

    return {
        "created": len(milestones),
        "milestones": [
            {"id": m.id, "title": m.title, "goal_type": m.goal_type}
            for m in milestones
        ]
    }


# ==================== REWARDS & UNLOCKS ====================

@router.get("/rewards/unlocks")
async def get_unlocks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available and unlocked features."""
    reward_system = RewardSystem(db)
    return await reward_system.check_unlocks(current_user.id)


@router.post("/rewards/unlock/{feature_id}")
async def unlock_feature(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlock a feature."""
    reward_system = RewardSystem(db)
    return await reward_system.unlock_feature(current_user.id, feature_id)


@router.get("/rewards/features")
async def get_unlocked_features(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all unlocked features for user."""
    reward_system = RewardSystem(db)
    return await reward_system.get_unlocked_features(current_user.id)


# ==================== AI ASSISTANT ====================

@router.post("/ai/suggestions")
async def get_ai_suggestions(
    context: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered action suggestions."""
    ai_assistant = AIAssistant(db)
    return await ai_assistant.suggest_actions(current_user.id, context)


@router.get("/ai/quick-actions")
async def get_quick_actions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get quick action suggestions."""
    ai_assistant = AIAssistant(db)
    return await ai_assistant.get_quick_actions(current_user.id)


@router.post("/ai/autocomplete")
async def autocomplete(
    partial_input: str,
    context_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get autocomplete suggestions."""
    ai_assistant = AIAssistant(db)
    return await ai_assistant.auto_complete(partial_input, context_type)


@router.post("/ai/workflows/recommend")
async def recommend_workflows(
    task_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow recommendations."""
    ai_assistant = AIAssistant(db)
    return await ai_assistant.recommend_workflows(task_type)


# ==================== AUTOMATION ====================

@router.post("/automation/correlate/{investigation_id}")
async def auto_correlate(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Auto-correlate findings in an investigation."""
    automation = SmartAutomation(db)
    correlations = await automation.auto_correlate(investigation_id)

    # Award points for correlations found
    if correlations:
        points_system = PointsSystem(db)
        for _ in correlations:
            await points_system.award_points(current_user.id, 'correlate_data')

    return {"correlations": correlations, "count": len(correlations)}


@router.post("/automation/categorize/{investigation_id}")
async def auto_categorize_findings(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Auto-categorize findings."""
    from database.models import Investigation
    from sqlalchemy import select

    # Get investigation findings
    result = await db.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    finding_ids = [f.id for f in investigation.findings]

    batch_ops = BatchOperations(db)
    result = await batch_ops.bulk_categorize(finding_ids, auto_categorize=True)

    return result


@router.post("/automation/report/{investigation_id}")
async def auto_generate_report(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Auto-generate report summary."""
    automation = SmartAutomation(db)
    return await automation.auto_report_findings(investigation_id)


# ==================== BATCH OPERATIONS ====================

@router.post("/batch/import")
async def bulk_import(
    request: BatchImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk import targets."""
    batch_ops = BatchOperations(db)
    result = await batch_ops.bulk_import_targets(request.investigation_id, request.targets)

    # Award points
    if result['created'] > 0:
        points_system = PointsSystem(db)
        await points_system.award_points(
            current_user.id,
            'automate_task',
            metadata={'operation': 'bulk_import', 'count': result['created']}
        )

    return result


@router.get("/batch/export/{investigation_id}")
async def bulk_export(
    investigation_id: int,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk export investigation data."""
    batch_ops = BatchOperations(db)
    return await batch_ops.bulk_export(investigation_id, format)


# ==================== TEMPLATES ====================

@router.get("/templates")
async def get_templates(
    category: Optional[str] = None,
    include_public: bool = True,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available templates."""
    template_system = TemplateSystem(db)
    return await template_system.get_templates(current_user.id, category, include_public, limit)


@router.post("/templates")
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new template."""
    from database.gamification_models import VisibilityLevel

    template_system = TemplateSystem(db)
    visibility = VisibilityLevel(request.visibility)

    template = await template_system.create_template(
        name=request.name,
        description=request.description,
        template_data=request.template_data,
        category=request.category,
        created_by=current_user.id,
        tags=request.tags,
        visibility=visibility
    )

    return {"id": template.id, "name": template.name}


@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: int,
    customizations: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create investigation from template."""
    template_system = TemplateSystem(db)
    investigation = await template_system.create_from_template(
        template_id,
        current_user.id,
        customizations
    )

    # Award points
    points_system = PointsSystem(db)
    await points_system.award_points(current_user.id, 'create_investigation')

    return {"investigation_id": investigation.id, "name": investigation.name}


@router.get("/templates/popular")
async def get_popular_templates(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get popular templates."""
    template_system = TemplateSystem(db)
    return await template_system.get_popular_templates(limit)


# ==================== TEAMS ====================

@router.post("/teams")
async def create_team(
    request: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new team."""
    from database.gamification_models import VisibilityLevel

    team_system = TeamSystem(db)
    visibility = VisibilityLevel(request.visibility)

    team = await team_system.create_team(
        name=request.name,
        description=request.description,
        created_by=current_user.id,
        visibility=visibility,
        invite_only=request.invite_only
    )

    # Award achievement
    achievement_system = AchievementSystem(db)
    await achievement_system.check_achievements(current_user.id, 'join_team')

    return {"id": team.id, "name": team.name}


@router.get("/teams")
async def get_my_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's teams."""
    team_system = TeamSystem(db)
    return await team_system.get_user_teams(current_user.id)


@router.get("/teams/{team_id}")
async def get_team_details(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get team details and statistics."""
    team_system = TeamSystem(db)
    return await team_system.get_team_stats(team_id)


@router.get("/teams/{team_id}/members")
async def get_team_members(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get team members."""
    team_system = TeamSystem(db)
    return await team_system.get_team_members(team_id)


@router.post("/teams/{team_id}/members/{user_id}")
async def add_team_member(
    team_id: int,
    user_id: int,
    role: str = "member",
    db: AsyncSession = Depends(get_db)
):
    """Add member to team."""
    from database.gamification_models import TeamRole

    team_system = TeamSystem(db)
    team_role = TeamRole(role)

    return await team_system.add_member(team_id, user_id, team_role)


# ==================== SHARING & DISCOVERY ====================

@router.post("/share")
async def share_investigation(
    request: ShareInvestigationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Share an investigation."""
    from database.gamification_models import VisibilityLevel

    sharing_system = SharingSystem(db)
    visibility = VisibilityLevel(request.visibility)

    shared = await sharing_system.share_investigation(
        investigation_id=request.investigation_id,
        shared_by=current_user.id,
        visibility=visibility,
        title=request.title,
        description=request.description
    )

    # Award points
    points_system = PointsSystem(db)
    await points_system.award_points(current_user.id, 'share_finding')

    return {"shared_id": shared.id}


@router.get("/discover")
async def discover_investigations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Discover public shared investigations."""
    sharing_system = SharingSystem(db)
    return await sharing_system.discover_public({}, limit, offset)


@router.get("/discover/trending")
async def get_trending(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get trending shared investigations."""
    sharing_system = SharingSystem(db)
    return await sharing_system.get_trending(limit)


@router.post("/share/{shared_id}/like")
async def like_shared_investigation(
    shared_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Like a shared investigation."""
    sharing_system = SharingSystem(db)
    return await sharing_system.like_investigation(shared_id, current_user.id)


@router.delete("/share/{shared_id}/like")
async def unlike_shared_investigation(
    shared_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlike a shared investigation."""
    sharing_system = SharingSystem(db)
    return await sharing_system.unlike_investigation(shared_id, current_user.id)


@router.post("/share/{shared_id}/comment")
async def add_comment(
    shared_id: int,
    request: CommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add comment to shared investigation."""
    sharing_system = SharingSystem(db)
    comment = await sharing_system.comment_on_investigation(
        shared_id,
        current_user.id,
        request.content
    )

    return {"comment_id": comment.id}


@router.get("/share/{shared_id}/comments")
async def get_comments(
    shared_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get comments for shared investigation."""
    sharing_system = SharingSystem(db)
    return await sharing_system.get_comments(shared_id, limit)


@router.post("/share/{shared_id}/clone")
async def clone_shared_investigation(
    shared_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clone a shared investigation."""
    sharing_system = SharingSystem(db)
    investigation = await sharing_system.clone_investigation(shared_id, current_user.id)

    # Award points
    points_system = PointsSystem(db)
    await points_system.award_points(current_user.id, 'create_investigation')

    return {"investigation_id": investigation.id, "name": investigation.name}


# ==================== NOTIFICATIONS ====================

@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications."""
    from database.gamification_models import UserNotification
    from sqlalchemy import select, desc

    query = select(UserNotification).where(UserNotification.user_id == current_user.id)

    if unread_only:
        query = query.where(UserNotification.is_read == False)

    query = query.order_by(desc(UserNotification.created_at)).limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type.value,
                "title": n.title,
                "message": n.message,
                "data": n.data,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ]
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    from database.gamification_models import UserNotification
    from sqlalchemy import select
    from datetime import datetime

    result = await db.execute(
        select(UserNotification).where(
            UserNotification.id == notification_id,
            UserNotification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()

    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await db.commit()
        return {"success": True}

    raise HTTPException(status_code=404, detail="Notification not found")
