"""Add ETL pipeline tables.

Revision ID: 003
Revises: 001
Create Date: 2025-01-XX

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003'
down_revision: Union[str, Sequence[str], None] = ('002', 'add_oracle_enum')  # Merge both heads
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ETLPipelineStatus enum if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE etlpipelinestatus AS ENUM ('draft', 'active', 'paused', 'failed', 'completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create etl_pipelines table
    op.create_table(
        'etl_pipelines',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('target_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('transformation_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'paused', 'failed', 'completed', name='etlpipelinestatus', create_type=False), nullable=True, server_default='draft'),
        sa.Column('schedule_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_etl_pipeline_status', 'etl_pipelines', ['status'])
    op.create_index('idx_etl_pipeline_created', 'etl_pipelines', ['created_at'])
    op.create_index(op.f('ix_etl_pipelines_name'), 'etl_pipelines', ['name'], unique=True)
    
    # Create etl_transformations table
    op.create_table(
        'etl_transformations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sql_query', sa.Text(), nullable=False),
        sa.Column('input_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_reusable', sa.Boolean(), default=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_etl_transform_name', 'etl_transformations', ['name'])
    
    # Create etl_runs table
    op.create_table(
        'etl_runs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('pipeline_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), default=0),
        sa.Column('records_failed', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('run_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['pipeline_id'], ['etl_pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_etl_run_pipeline', 'etl_runs', ['pipeline_id'])
    op.create_index('idx_etl_run_status', 'etl_runs', ['status'])
    op.create_index('idx_etl_run_started', 'etl_runs', ['started_at'])
    
    # Create data_quality_rules table
    op.create_table(
        'data_quality_rules',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('rule_type', sa.String(100), nullable=False),
        sa.Column('rule_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_columns', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pipeline_id', sa.String(36), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['etl_pipelines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dq_rule_pipeline', 'data_quality_rules', ['pipeline_id'])
    op.create_index('idx_dq_rule_category', 'data_quality_rules', ['category'])
    
    # Create etl_schedules table
    op.create_table(
        'etl_schedules',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('pipeline_id', sa.String(36), nullable=False),
        sa.Column('schedule_type', sa.String(50), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('max_retries', sa.Integer(), default=3),
        sa.Column('retry_delay_minutes', sa.Integer(), default=5),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['etl_pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_etl_schedule_pipeline', 'etl_schedules', ['pipeline_id'])
    op.create_index('idx_etl_schedule_enabled', 'etl_schedules', ['enabled'])


def downgrade() -> None:
    op.drop_table('etl_schedules')
    op.drop_table('data_quality_rules')
    op.drop_table('etl_runs')
    op.drop_table('etl_transformations')
    op.drop_table('etl_pipelines')
    op.execute("DROP TYPE IF EXISTS etlpipelinestatus;")

