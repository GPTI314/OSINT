"""Add gamification tables.

Revision ID: gamification_001
Create Date: 2025-01-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'gamification_001'
down_revision = 'add_enhanced_features'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database with gamification tables."""

    # Create enums
    op.execute("""
        CREATE TYPE achievementcategory AS ENUM (
            'first_steps', 'explorer', 'detective', 'automation', 'social', 'expert', 'special'
        );
    """)

    op.execute("""
        CREATE TYPE badgetier AS ENUM (
            'bronze', 'silver', 'gold', 'platinum', 'diamond'
        );
    """)

    op.execute("""
        CREATE TYPE teamrole AS ENUM (
            'owner', 'admin', 'member', 'viewer'
        );
    """)

    op.execute("""
        CREATE TYPE visibilitylevel AS ENUM (
            'private', 'team', 'public'
        );
    """)

    op.execute("""
        CREATE TYPE notificationtype AS ENUM (
            'achievement', 'level_up', 'team_invite', 'share', 'collaboration', 'milestone', 'reward'
        );
    """)

    # User Progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_level_xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_level_xp', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('investigations_created', sa.Integer(), server_default='0'),
        sa.Column('scrapes_completed', sa.Integer(), server_default='0'),
        sa.Column('findings_discovered', sa.Integer(), server_default='0'),
        sa.Column('correlations_found', sa.Integer(), server_default='0'),
        sa.Column('threats_detected', sa.Integer(), server_default='0'),
        sa.Column('patterns_identified', sa.Integer(), server_default='0'),
        sa.Column('tasks_automated', sa.Integer(), server_default='0'),
        sa.Column('workflows_created', sa.Integer(), server_default='0'),
        sa.Column('ai_assists_used', sa.Integer(), server_default='0'),
        sa.Column('findings_shared', sa.Integer(), server_default='0'),
        sa.Column('collaborations', sa.Integer(), server_default='0'),
        sa.Column('fastest_investigation_time', sa.Integer(), nullable=True),
        sa.Column('total_time_saved', sa.Integer(), server_default='0'),
        sa.Column('profile_visibility', sa.Enum('private', 'team', 'public', name='visibilitylevel'),
                  server_default='private'),
        sa.Column('leaderboard_opt_in', sa.Boolean(), server_default='true'),
        sa.Column('notifications_enabled', sa.Boolean(), server_default='true'),
        sa.Column('sound_effects_enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'])

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum('first_steps', 'explorer', 'detective', 'automation', 'social', 'expert', 'special',
                                      name='achievementcategory'), nullable=False),
        sa.Column('tier', sa.Enum('bronze', 'silver', 'gold', 'platinum', 'diamond', name='badgetier'),
                  server_default='bronze'),
        sa.Column('points_reward', sa.Integer(), server_default='0'),
        sa.Column('xp_reward', sa.Integer(), server_default='0'),
        sa.Column('requirement_type', sa.String(50), nullable=False),
        sa.Column('requirement_value', sa.Integer(), nullable=True),
        sa.Column('requirement_data', sa.JSON(), server_default='{}'),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('badge_color', sa.String(20), nullable=True),
        sa.Column('is_secret', sa.Boolean(), server_default='false'),
        sa.Column('unlock_message', sa.Text(), nullable=True),
        sa.Column('total_awarded', sa.Integer(), server_default='0'),
        sa.Column('rarity_score', sa.Float(), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('achievement_id')
    )
    op.create_index('ix_achievements_achievement_id', 'achievements', ['achievement_id'])
    op.create_index('ix_achievements_category', 'achievements', ['category'])

    # User Achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_progress_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('progress', sa.Integer(), server_default='0'),
        sa.Column('is_showcased', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_progress_id', 'achievement_id', name='unique_user_achievement')
    )
    op.create_index('ix_user_achievements_user_progress_id', 'user_achievements', ['user_progress_id'])
    op.create_index('ix_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])

    # Point History table
    op.create_table(
        'point_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_progress_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('xp', sa.Integer(), nullable=False),
        sa.Column('multiplier', sa.Float(), server_default='1.0'),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), server_default='{}'),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_progress_id'], ['user_progress.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_point_history_user_progress_id', 'point_history', ['user_progress_id'])
    op.create_index('ix_point_history_action', 'point_history', ['action'])
    op.create_index('ix_point_history_earned_at', 'point_history', ['earned_at'])

    # Leaderboards table
    op.create_table(
        'leaderboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), server_default='{}'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'category', 'period', name='unique_leaderboard_entry')
    )
    op.create_index('ix_leaderboards_user_id', 'leaderboards', ['user_id'])
    op.create_index('ix_leaderboards_category', 'leaderboards', ['category'])
    op.create_index('ix_leaderboards_period', 'leaderboards', ['period'])

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_points', sa.Integer(), server_default='0'),
        sa.Column('member_count', sa.Integer(), server_default='0'),
        sa.Column('visibility', sa.Enum('private', 'team', 'public', name='visibilitylevel'), server_default='private'),
        sa.Column('invite_only', sa.Boolean(), server_default='true'),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('banner_url', sa.String(500), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_name', 'teams', ['name'])

    # Team Members association table
    op.create_table(
        'team_members',
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('owner', 'admin', 'member', 'viewer', name='teamrole'), server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Continue with other tables...
    # (Milestones, UnlockedFeatures, SharedInvestigations, etc.)

    # Milestones table
    op.create_table(
        'milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal_type', sa.String(50), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Integer(), server_default='0'),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('points_reward', sa.Integer(), server_default='0'),
        sa.Column('xp_reward', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_milestones_user_id', 'milestones', ['user_id'])

    # User Notifications table
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.Enum('achievement', 'level_up', 'team_invite', 'share',
                                               'collaboration', 'milestone', 'reward', name='notificationtype')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.JSON(), server_default='{}'),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_notifications_user_id', 'user_notifications', ['user_id'])
    op.create_index('ix_user_notifications_notification_type', 'user_notifications', ['notification_type'])
    op.create_index('ix_user_notifications_is_read', 'user_notifications', ['is_read'])
    op.create_index('ix_user_notifications_created_at', 'user_notifications', ['created_at'])


def downgrade():
    """Downgrade - remove gamification tables."""
    op.drop_table('user_notifications')
    op.drop_table('milestones')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('leaderboards')
    op.drop_table('point_history')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('user_progress')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS notificationtype;")
    op.execute("DROP TYPE IF EXISTS visibilitylevel;")
    op.execute("DROP TYPE IF EXISTS teamrole;")
    op.execute("DROP TYPE IF EXISTS badgetier;")
    op.execute("DROP TYPE IF EXISTS achievementcategory;")
