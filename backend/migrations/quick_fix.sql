-- Quick fix: Add missing columns to users table
-- Run this directly in your PostgreSQL database

-- Add tenant_id column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'tenant_id') THEN
        ALTER TABLE users ADD COLUMN tenant_id UUID;
    END IF;
END $$;

-- Add status column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'status') THEN
        ALTER TABLE users ADD COLUMN status VARCHAR(20);
    END IF;
END $$;

-- Add last_login column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'last_login') THEN
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
    END IF;
END $$;

-- Set default values for existing users
UPDATE users 
SET tenant_id = '00000000-0000-0000-0000-000000000000'::UUID 
WHERE tenant_id IS NULL;

UPDATE users 
SET status = 'active' 
WHERE status IS NULL;

-- Create index on tenant_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);

-- Verify columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name IN ('tenant_id', 'status', 'last_login')
ORDER BY column_name;

