-- Create ETL Pipeline Status Enum
DO $$ BEGIN
    CREATE TYPE etlpipelinestatus AS ENUM ('draft', 'active', 'paused', 'failed', 'completed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create etl_pipelines table
CREATE TABLE IF NOT EXISTS etl_pipelines (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    source_type VARCHAR(50) NOT NULL,
    source_config JSONB DEFAULT '{}',
    target_type VARCHAR(50) NOT NULL,
    target_config JSONB DEFAULT '{}',
    transformation_ids JSONB DEFAULT '[]',
    status etlpipelinestatus DEFAULT 'draft',
    schedule_config JSONB DEFAULT '{}',
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etl_pipeline_status ON etl_pipelines(status);
CREATE INDEX IF NOT EXISTS idx_etl_pipeline_created ON etl_pipelines(created_at);
CREATE UNIQUE INDEX IF NOT EXISTS ix_etl_pipelines_name ON etl_pipelines(name);

-- Create etl_transformations table
CREATE TABLE IF NOT EXISTS etl_transformations (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sql_query TEXT NOT NULL,
    input_schema JSONB DEFAULT '{}',
    output_schema JSONB DEFAULT '{}',
    is_reusable BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    tags JSONB DEFAULT '[]',
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etl_transform_name ON etl_transformations(name);

-- Create etl_runs table
CREATE TABLE IF NOT EXISTS etl_runs (
    id VARCHAR(36) PRIMARY KEY,
    pipeline_id VARCHAR(36) NOT NULL REFERENCES etl_pipelines(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    run_metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_etl_run_pipeline ON etl_runs(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_etl_run_status ON etl_runs(status);
CREATE INDEX IF NOT EXISTS idx_etl_run_started ON etl_runs(started_at);

-- Create data_quality_rules table
CREATE TABLE IF NOT EXISTS data_quality_rules (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    rule_type VARCHAR(100) NOT NULL,
    rule_config JSONB DEFAULT '{}',
    target_columns JSONB DEFAULT '[]',
    pipeline_id VARCHAR(36) REFERENCES etl_pipelines(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50),
    last_run_at TIMESTAMP,
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dq_rule_pipeline ON data_quality_rules(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_dq_rule_category ON data_quality_rules(category);

-- Create etl_schedules table
CREATE TABLE IF NOT EXISTS etl_schedules (
    id VARCHAR(36) PRIMARY KEY,
    pipeline_id VARCHAR(36) NOT NULL REFERENCES etl_pipelines(id) ON DELETE CASCADE,
    schedule_type VARCHAR(50) NOT NULL,
    cron_expression VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    max_retries INTEGER DEFAULT 3,
    retry_delay_minutes INTEGER DEFAULT 5,
    enabled BOOLEAN DEFAULT TRUE,
    next_run_at TIMESTAMP,
    last_run_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etl_schedule_pipeline ON etl_schedules(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_etl_schedule_enabled ON etl_schedules(enabled);

