"""Add credit risk scoring tables

Revision ID: 001_credit_risk
Revises:
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_credit_risk'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create credit risk scoring tables."""

    # Consumer Applications
    op.create_table(
        'consumer_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('investigation_id', sa.Integer(), nullable=True),
        sa.Column('applicant_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('requested_amount', sa.Float(), nullable=True),
        sa.Column('loan_purpose', sa.String(length=100), nullable=True),
        sa.Column('employment_status', sa.String(length=50), nullable=True),
        sa.Column('monthly_income', sa.Float(), nullable=True),
        sa.Column('application_status', sa.Enum('PENDING', 'COLLECTING_DATA', 'ANALYZING', 'SCORED', 'APPROVED', 'REJECTED', 'MANUAL_REVIEW', name='applicationstatus'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_applications_id'), 'consumer_applications', ['id'], unique=False)
    op.create_index(op.f('ix_consumer_applications_applicant_name'), 'consumer_applications', ['applicant_name'], unique=False)
    op.create_index(op.f('ix_consumer_applications_email'), 'consumer_applications', ['email'], unique=False)
    op.create_index(op.f('ix_consumer_applications_application_status'), 'consumer_applications', ['application_status'], unique=False)

    # Consumer Risk Scores
    op.create_table(
        'consumer_risk_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=True),
        sa.Column('osint_score', sa.Integer(), nullable=True),
        sa.Column('traditional_score', sa.Integer(), nullable=True),
        sa.Column('behavioral_score', sa.Integer(), nullable=True),
        sa.Column('fraud_score', sa.Integer(), nullable=True),
        sa.Column('risk_tier', sa.Enum('EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HIGH_RISK', name='risktier'), nullable=True),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH', name='risklevel'), nullable=True),
        sa.Column('probability_of_default', sa.Float(), nullable=True),
        sa.Column('recommended_interest_rate', sa.Float(), nullable=True),
        sa.Column('recommended_loan_amount', sa.Float(), nullable=True),
        sa.Column('approval_recommendation', sa.String(length=20), nullable=True),
        sa.Column('score_components', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['consumer_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_risk_scores_id'), 'consumer_risk_scores', ['id'], unique=False)
    op.create_index(op.f('ix_consumer_risk_scores_risk_tier'), 'consumer_risk_scores', ['risk_tier'], unique=False)
    op.create_index(op.f('ix_consumer_risk_scores_risk_level'), 'consumer_risk_scores', ['risk_level'], unique=False)

    # Consumer OSINT Data
    op.create_table(
        'consumer_osint_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('risk_signals', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['consumer_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_osint_data_id'), 'consumer_osint_data', ['id'], unique=False)
    op.create_index(op.f('ix_consumer_osint_data_data_type'), 'consumer_osint_data', ['data_type'], unique=False)

    # Consumer Financial Data
    op.create_table(
        'consumer_financial_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('bank_accounts', sa.JSON(), nullable=True),
        sa.Column('credit_cards', sa.JSON(), nullable=True),
        sa.Column('loans', sa.JSON(), nullable=True),
        sa.Column('income_sources', sa.JSON(), nullable=True),
        sa.Column('expenses', sa.JSON(), nullable=True),
        sa.Column('debt_to_income_ratio', sa.Float(), nullable=True),
        sa.Column('credit_utilization', sa.Float(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['consumer_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_financial_data_id'), 'consumer_financial_data', ['id'], unique=False)

    # Consumer Behavioral Data
    op.create_table(
        'consumer_behavioral_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('online_activity', sa.JSON(), nullable=True),
        sa.Column('payment_patterns', sa.JSON(), nullable=True),
        sa.Column('social_media_activity', sa.JSON(), nullable=True),
        sa.Column('digital_footprint_score', sa.Integer(), nullable=True),
        sa.Column('behavioral_indicators', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['consumer_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_behavioral_data_id'), 'consumer_behavioral_data', ['id'], unique=False)

    # Consumer Fraud Indicators
    op.create_table(
        'consumer_fraud_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('indicator_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='fraudseverity'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['consumer_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consumer_fraud_indicators_id'), 'consumer_fraud_indicators', ['id'], unique=False)
    op.create_index(op.f('ix_consumer_fraud_indicators_indicator_type'), 'consumer_fraud_indicators', ['indicator_type'], unique=False)
    op.create_index(op.f('ix_consumer_fraud_indicators_severity'), 'consumer_fraud_indicators', ['severity'], unique=False)

    # Business Applications
    op.create_table(
        'business_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('investigation_id', sa.Integer(), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=True),
        sa.Column('registration_number', sa.String(length=100), nullable=True),
        sa.Column('tax_id', sa.String(length=100), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('business_type', sa.String(length=50), nullable=True),
        sa.Column('founded_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('number_of_employees', sa.Integer(), nullable=True),
        sa.Column('annual_revenue', sa.Float(), nullable=True),
        sa.Column('requested_amount', sa.Float(), nullable=True),
        sa.Column('loan_purpose', sa.Text(), nullable=True),
        sa.Column('application_status', sa.Enum('PENDING', 'COLLECTING_DATA', 'ANALYZING', 'SCORED', 'APPROVED', 'REJECTED', 'MANUAL_REVIEW', name='applicationstatus'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_applications_id'), 'business_applications', ['id'], unique=False)
    op.create_index(op.f('ix_business_applications_company_name'), 'business_applications', ['company_name'], unique=False)
    op.create_index(op.f('ix_business_applications_registration_number'), 'business_applications', ['registration_number'], unique=False)
    op.create_index(op.f('ix_business_applications_tax_id'), 'business_applications', ['tax_id'], unique=False)
    op.create_index(op.f('ix_business_applications_domain'), 'business_applications', ['domain'], unique=False)
    op.create_index(op.f('ix_business_applications_industry'), 'business_applications', ['industry'], unique=False)
    op.create_index(op.f('ix_business_applications_application_status'), 'business_applications', ['application_status'], unique=False)

    # Business Risk Scores
    op.create_table(
        'business_risk_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=True),
        sa.Column('osint_score', sa.Integer(), nullable=True),
        sa.Column('financial_score', sa.Integer(), nullable=True),
        sa.Column('operational_score', sa.Integer(), nullable=True),
        sa.Column('industry_score', sa.Integer(), nullable=True),
        sa.Column('management_score', sa.Integer(), nullable=True),
        sa.Column('risk_tier', sa.Enum('EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'HIGH_RISK', name='risktier'), nullable=True),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH', name='risklevel'), nullable=True),
        sa.Column('probability_of_default', sa.Float(), nullable=True),
        sa.Column('recommended_interest_rate', sa.Float(), nullable=True),
        sa.Column('recommended_loan_amount', sa.Float(), nullable=True),
        sa.Column('recommended_term_months', sa.Integer(), nullable=True),
        sa.Column('approval_recommendation', sa.String(length=20), nullable=True),
        sa.Column('score_components', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['business_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_risk_scores_id'), 'business_risk_scores', ['id'], unique=False)
    op.create_index(op.f('ix_business_risk_scores_risk_tier'), 'business_risk_scores', ['risk_tier'], unique=False)
    op.create_index(op.f('ix_business_risk_scores_risk_level'), 'business_risk_scores', ['risk_level'], unique=False)

    # Business OSINT Data
    op.create_table(
        'business_osint_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('risk_signals', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['business_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_osint_data_id'), 'business_osint_data', ['id'], unique=False)
    op.create_index(op.f('ix_business_osint_data_data_type'), 'business_osint_data', ['data_type'], unique=False)

    # Business Financial Data
    op.create_table(
        'business_financial_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('balance_sheet', sa.JSON(), nullable=True),
        sa.Column('income_statement', sa.JSON(), nullable=True),
        sa.Column('cash_flow_statement', sa.JSON(), nullable=True),
        sa.Column('financial_ratios', sa.JSON(), nullable=True),
        sa.Column('credit_history', sa.JSON(), nullable=True),
        sa.Column('trade_references', sa.JSON(), nullable=True),
        sa.Column('bank_statements', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['business_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_financial_data_id'), 'business_financial_data', ['id'], unique=False)

    # Business Operational Data
    op.create_table(
        'business_operational_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('management_team', sa.JSON(), nullable=True),
        sa.Column('business_model', sa.Text(), nullable=True),
        sa.Column('market_position', sa.String(length=50), nullable=True),
        sa.Column('competitive_analysis', sa.JSON(), nullable=True),
        sa.Column('operational_metrics', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['business_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_operational_data_id'), 'business_operational_data', ['id'], unique=False)

    # Business Fraud Indicators
    op.create_table(
        'business_fraud_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('indicator_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='fraudseverity'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['business_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_fraud_indicators_id'), 'business_fraud_indicators', ['id'], unique=False)
    op.create_index(op.f('ix_business_fraud_indicators_indicator_type'), 'business_fraud_indicators', ['indicator_type'], unique=False)
    op.create_index(op.f('ix_business_fraud_indicators_severity'), 'business_fraud_indicators', ['severity'], unique=False)


def downgrade() -> None:
    """Drop credit risk scoring tables."""
    op.drop_table('business_fraud_indicators')
    op.drop_table('business_operational_data')
    op.drop_table('business_financial_data')
    op.drop_table('business_osint_data')
    op.drop_table('business_risk_scores')
    op.drop_table('business_applications')
    op.drop_table('consumer_fraud_indicators')
    op.drop_table('consumer_behavioral_data')
    op.drop_table('consumer_financial_data')
    op.drop_table('consumer_osint_data')
    op.drop_table('consumer_risk_scores')
    op.drop_table('consumer_applications')
    op.execute('DROP TYPE IF EXISTS fraudseverity')
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS risktier')
    op.execute('DROP TYPE IF EXISTS applicationstatus')
