"""Add enhanced OSINT features: SEO/SEM, LinkedIn, Lists, Zoning, and Health.

Revision ID: add_enhanced_features
Create Date: 2024-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_enhanced_features'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Create new tables for enhanced features."""

    # SEO Analysis Table
    op.create_table(
        'seo_analysis',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('target_url', sa.Text(), nullable=False, index=True),
        sa.Column('analysis_type', sa.String(50), nullable=False, index=True),
        sa.Column('score', sa.Float()),
        sa.Column('issues', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Keyword Rankings Table
    op.create_table(
        'keyword_rankings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('domain', sa.String(255), nullable=False, index=True),
        sa.Column('keyword', sa.String(255), nullable=False, index=True),
        sa.Column('position', sa.Integer()),
        sa.Column('search_volume', sa.Integer()),
        sa.Column('difficulty', sa.Float()),
        sa.Column('cpc', sa.Float()),
        sa.Column('tracked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('location', sa.String(100)),
        sa.Column('device_type', sa.String(20)),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Backlinks Table
    op.create_table(
        'backlinks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('target_domain', sa.String(255), nullable=False, index=True),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('source_domain', sa.String(255), index=True),
        sa.Column('anchor_text', sa.Text()),
        sa.Column('link_type', sa.String(20)),
        sa.Column('domain_authority', sa.Integer()),
        sa.Column('page_authority', sa.Integer()),
        sa.Column('discovered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Competitor Analysis Table
    op.create_table(
        'competitor_analysis',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('target_domain', sa.String(255), nullable=False, index=True),
        sa.Column('competitor_domain', sa.String(255), nullable=False, index=True),
        sa.Column('comparison_metrics', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('shared_keywords', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('backlink_overlap', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # LinkedIn Profiles Table
    op.create_table(
        'linkedin_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('profile_url', sa.Text(), unique=True, nullable=False, index=True),
        sa.Column('full_name', sa.String(255)),
        sa.Column('headline', sa.Text()),
        sa.Column('location', sa.String(255)),
        sa.Column('industry', sa.String(100)),
        sa.Column('current_company', sa.String(255)),
        sa.Column('current_position', sa.String(255)),
        sa.Column('company_size', sa.String(50)),
        sa.Column('experience', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('education', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('connections_count', sa.Integer()),
        sa.Column('recommendations_count', sa.Integer()),
        sa.Column('posts_count', sa.Integer()),
        sa.Column('extracted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # LinkedIn Companies Table
    op.create_table(
        'linkedin_companies',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('company_url', sa.Text(), unique=True, nullable=False, index=True),
        sa.Column('company_name', sa.String(255), index=True),
        sa.Column('industry', sa.String(100)),
        sa.Column('company_size', sa.String(50)),
        sa.Column('headquarters', sa.String(255)),
        sa.Column('website', sa.Text()),
        sa.Column('description', sa.Text()),
        sa.Column('employee_count', sa.Integer()),
        sa.Column('followers_count', sa.Integer()),
        sa.Column('specialties', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('extracted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # LinkedIn Verticals Table
    op.create_table(
        'linkedin_verticals',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('vertical_name', sa.String(255), nullable=False, index=True),
        sa.Column('vertical_type', sa.String(50), nullable=False),
        sa.Column('criteria', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('profile_ids', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('company_ids', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Vertical Filters Table
    op.create_table(
        'vertical_filters',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('vertical_id', sa.Integer(), sa.ForeignKey('linkedin_verticals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filter_type', sa.String(50), nullable=False),
        sa.Column('filter_value', sa.Text()),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Configurable Lists Table
    op.create_table(
        'configurable_lists',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('list_name', sa.String(255), nullable=False, index=True),
        sa.Column('list_type', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('columns', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('sort_config', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('filter_config', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('view_config', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # List Items Table
    op.create_table(
        'list_items',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('list_id', sa.Integer(), sa.ForeignKey('configurable_lists.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('position', sa.Integer()),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # List Integrations Table
    op.create_table(
        'list_integrations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('list_id', sa.Integer(), sa.ForeignKey('configurable_lists.id', ondelete='CASCADE'), nullable=False),
        sa.Column('integration_type', sa.String(50), nullable=False),
        sa.Column('integration_config', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('sync_status', sa.String(50)),
        sa.Column('last_synced_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )

    # Zoning Searches Table
    op.create_table(
        'zoning_searches',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('investigation_id', sa.Integer(), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('street_name', sa.String(255), nullable=False, index=True),
        sa.Column('house_number', sa.String(50), nullable=False),
        sa.Column('city', sa.String(255)),
        sa.Column('search_result', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('plantextbestimmungen', sa.Text()),
        sa.Column('parsed_data', postgresql.JSON(astext_type=sa.Text()), default={}),
        sa.Column('searched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), default={})
    )


def downgrade():
    """Drop all new tables."""
    op.drop_table('zoning_searches')
    op.drop_table('list_integrations')
    op.drop_table('list_items')
    op.drop_table('configurable_lists')
    op.drop_table('vertical_filters')
    op.drop_table('linkedin_verticals')
    op.drop_table('linkedin_companies')
    op.drop_table('linkedin_profiles')
    op.drop_table('competitor_analysis')
    op.drop_table('backlinks')
    op.drop_table('keyword_rankings')
    op.drop_table('seo_analysis')
