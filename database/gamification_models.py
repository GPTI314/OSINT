"""Gamification database models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Enum as SQLEnum, Float, BigInteger, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .models import Base


class AchievementCategory(enum.Enum):
    """Achievement category enumeration."""
    FIRST_STEPS = "first_steps"
    EXPLORER = "explorer"
    DETECTIVE = "detective"
    AUTOMATION = "automation"
    SOCIAL = "social"
    EXPERT = "expert"
    SPECIAL = "special"


class BadgeTier(enum.Enum):
    """Badge tier enumeration."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class TeamRole(enum.Enum):
    """Team role enumeration."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class VisibilityLevel(enum.Enum):
    """Visibility level enumeration."""
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class NotificationType(enum.Enum):
    """Notification type enumeration."""
    ACHIEVEMENT = "achievement"
    LEVEL_UP = "level_up"
    TEAM_INVITE = "team_invite"
    SHARE = "share"
    COLLABORATION = "collaboration"
    MILESTONE = "milestone"
    REWARD = "reward"


# Association tables
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role', SQLEnum(TeamRole), default=TeamRole.MEMBER),
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)


class UserProgress(Base):
    """User progress and gamification stats."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Points and Level
    total_points = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    current_level_xp = Column(Integer, default=0, nullable=False)
    next_level_xp = Column(Integer, default=100, nullable=False)

    # Streaks
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)

    # Statistics
    investigations_created = Column(Integer, default=0)
    scrapes_completed = Column(Integer, default=0)
    findings_discovered = Column(Integer, default=0)
    correlations_found = Column(Integer, default=0)
    threats_detected = Column(Integer, default=0)
    patterns_identified = Column(Integer, default=0)
    tasks_automated = Column(Integer, default=0)
    workflows_created = Column(Integer, default=0)
    ai_assists_used = Column(Integer, default=0)
    findings_shared = Column(Integer, default=0)
    collaborations = Column(Integer, default=0)

    # Timing stats
    fastest_investigation_time = Column(Integer, nullable=True)  # seconds
    total_time_saved = Column(Integer, default=0)  # seconds saved by automation

    # Settings
    profile_visibility = Column(SQLEnum(VisibilityLevel), default=VisibilityLevel.PRIVATE)
    leaderboard_opt_in = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    sound_effects_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="progress")
    achievements = relationship("UserAchievement", back_populates="user_progress", cascade="all, delete-orphan")
    point_history = relationship("PointHistory", back_populates="user_progress", cascade="all, delete-orphan")


class Achievement(Base):
    """Achievement definitions."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(AchievementCategory), nullable=False, index=True)
    tier = Column(SQLEnum(BadgeTier), default=BadgeTier.BRONZE, nullable=False)

    # Requirements
    points_reward = Column(Integer, default=0, nullable=False)
    xp_reward = Column(Integer, default=0, nullable=False)
    requirement_type = Column(String(50), nullable=False)  # count, streak, time, special
    requirement_value = Column(Integer, nullable=True)
    requirement_data = Column(JSON, default={})

    # Display
    icon = Column(String(100))  # emoji or icon name
    badge_color = Column(String(20))
    is_secret = Column(Boolean, default=False)  # Hidden until unlocked
    unlock_message = Column(Text)

    # Metadata
    total_awarded = Column(Integer, default=0)
    rarity_score = Column(Float, default=0.0)  # calculated based on how many have it

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    """User's unlocked achievements."""
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint('user_progress_id', 'achievement_id', name='unique_user_achievement'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    progress = Column(Integer, default=0)  # for tracking progress toward achievement
    is_showcased = Column(Boolean, default=False)  # display on profile

    # Relationships
    user_progress = relationship("UserProgress", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


class PointHistory(Base):
    """History of points earned."""
    __tablename__ = "point_history"

    id = Column(BigInteger, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id", ondelete="CASCADE"), nullable=False, index=True)

    action = Column(String(100), nullable=False, index=True)
    points = Column(Integer, nullable=False)
    xp = Column(Integer, nullable=False)
    multiplier = Column(Float, default=1.0)

    # Context
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    metadata = Column(JSON, default={})

    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user_progress = relationship("UserProgress", back_populates="point_history")


class Leaderboard(Base):
    """Leaderboard entries."""
    __tablename__ = "leaderboards"
    __table_args__ = (
        UniqueConstraint('user_id', 'category', 'period', name='unique_leaderboard_entry'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    category = Column(String(50), nullable=False, index=True)  # overall, weekly, monthly, category-specific
    period = Column(String(20), nullable=False, index=True)  # all_time, weekly, monthly, daily

    score = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=True)

    # Metadata
    metadata = Column(JSON, default={})

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="leaderboard_entries")


class Team(Base):
    """Teams for collaboration."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Team stats
    total_points = Column(Integer, default=0)
    member_count = Column(Integer, default=0)

    # Settings
    visibility = Column(SQLEnum(VisibilityLevel), default=VisibilityLevel.PRIVATE)
    invite_only = Column(Boolean, default=True)

    # Display
    avatar_url = Column(String(500))
    banner_url = Column(String(500))
    color = Column(String(20))

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    members = relationship("User", secondary=team_members, backref="teams")
    team_achievements = relationship("TeamAchievement", back_populates="team", cascade="all, delete-orphan")


class TeamAchievement(Base):
    """Team achievements."""
    __tablename__ = "team_achievements"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    contributed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    team = relationship("Team", back_populates="team_achievements")
    achievement = relationship("Achievement")


class Milestone(Base):
    """User milestones and goals."""
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)
    goal_type = Column(String(50), nullable=False)  # investigations, scrapes, findings, etc.
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)

    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Rewards
    points_reward = Column(Integer, default=0)
    xp_reward = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="milestones")


class UnlockedFeature(Base):
    """Features unlocked by users through progression."""
    __tablename__ = "unlocked_features"
    __table_args__ = (
        UniqueConstraint('user_id', 'feature_id', name='unique_user_feature'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    feature_id = Column(String(100), nullable=False, index=True)
    feature_name = Column(String(255), nullable=False)
    feature_description = Column(Text)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    unlock_requirement = Column(String(100))  # level_5, achievement_xyz, etc.

    # Relationships
    user = relationship("User", backref="unlocked_features")


class SharedInvestigation(Base):
    """Shared investigations."""
    __tablename__ = "shared_investigations"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    visibility = Column(SQLEnum(VisibilityLevel), default=VisibilityLevel.PRIVATE, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Stats
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    clone_count = Column(Integer, default=0)

    shared_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    investigation = relationship("Investigation")
    shared_by_user = relationship("User", foreign_keys=[shared_by])
    likes = relationship("InvestigationLike", back_populates="shared_investigation", cascade="all, delete-orphan")
    comments = relationship("InvestigationComment", back_populates="shared_investigation", cascade="all, delete-orphan")


class InvestigationLike(Base):
    """Likes on shared investigations."""
    __tablename__ = "investigation_likes"
    __table_args__ = (
        UniqueConstraint('shared_investigation_id', 'user_id', name='unique_investigation_like'),
    )

    id = Column(Integer, primary_key=True, index=True)
    shared_investigation_id = Column(Integer, ForeignKey("shared_investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    liked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    shared_investigation = relationship("SharedInvestigation", back_populates="likes")
    user = relationship("User")


class InvestigationComment(Base):
    """Comments on shared investigations."""
    __tablename__ = "investigation_comments"

    id = Column(Integer, primary_key=True, index=True)
    shared_investigation_id = Column(Integer, ForeignKey("shared_investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    shared_investigation = relationship("SharedInvestigation", back_populates="comments")
    user = relationship("User")


class InvestigationTemplate(Base):
    """Investigation templates."""
    __tablename__ = "investigation_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Template data
    template_data = Column(JSON, nullable=False)
    category = Column(String(100), index=True)
    tags = Column(JSON, default=[])

    # Stats
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    visibility = Column(SQLEnum(VisibilityLevel), default=VisibilityLevel.PRIVATE)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User")


class UserNotification(Base):
    """User notifications."""
    __tablename__ = "user_notifications"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Data
    data = Column(JSON, default={})
    action_url = Column(String(500))

    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="notifications")


class DailyChallenge(Base):
    """Daily challenges for users."""
    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(DateTime(timezone=True), nullable=False, index=True)
    challenge_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Requirements
    requirement_type = Column(String(50), nullable=False)
    requirement_value = Column(Integer, nullable=False)

    # Rewards
    points_reward = Column(Integer, default=50)
    xp_reward = Column(Integer, default=25)

    # Stats
    participants = Column(Integer, default=0)
    completions = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserChallenge(Base):
    """User participation in challenges."""
    __tablename__ = "user_challenges"
    __table_args__ = (
        UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id", ondelete="CASCADE"), nullable=False, index=True)

    progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    challenge = relationship("DailyChallenge")


class AIAssistantSession(Base):
    """AI Assistant interaction sessions."""
    __tablename__ = "ai_assistant_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    session_type = Column(String(50), nullable=False)  # suggestion, autocomplete, workflow, etc.
    context = Column(JSON, default={})

    suggestions_provided = Column(Integer, default=0)
    suggestions_accepted = Column(Integer, default=0)
    time_saved = Column(Integer, default=0)  # estimated seconds saved

    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
