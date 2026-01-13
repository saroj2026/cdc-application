-- Migration: Add offset/LSN/SCN tracking columns to pipelines table
-- Run this script to add the necessary columns for tracking database-specific offsets

-- Check if columns already exist before adding
DO $$
BEGIN
    -- Add current_lsn column (PostgreSQL/SQL Server LSN)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pipelines' AND column_name = 'current_lsn'
    ) THEN
        ALTER TABLE pipelines ADD COLUMN current_lsn VARCHAR;
    END IF;

    -- Add current_offset column (MySQL binlog position)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pipelines' AND column_name = 'current_offset'
    ) THEN
        ALTER TABLE pipelines ADD COLUMN current_offset VARCHAR;
    END IF;

    -- Add current_scn column (Oracle SCN)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pipelines' AND column_name = 'current_scn'
    ) THEN
        ALTER TABLE pipelines ADD COLUMN current_scn VARCHAR;
    END IF;

    -- Add last_offset_updated timestamp
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pipelines' AND column_name = 'last_offset_updated'
    ) THEN
        ALTER TABLE pipelines ADD COLUMN last_offset_updated TIMESTAMP;
    END IF;
END $$;

-- Verify columns were added
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'pipelines' 
    AND column_name IN ('current_lsn', 'current_offset', 'current_scn', 'last_offset_updated')
ORDER BY column_name;


