# Database Migration Instructions

## Problem
The error occurs because the database doesn't have the new columns (`tenant_id`, `status`, `last_login`) that were added to the `UserModel`.

## Solution: Run the Migration

You have two options:

### Option 1: Run Migration Script (Recommended)

```bash
cd backend
python run_migration.py
```

This will:
- Add `tenant_id`, `status`, `last_login` columns to `users` table
- Create `user_sessions` table for refresh tokens
- Create `audit_logs` table for audit trail
- Set default values for existing users

### Option 2: Run SQL Manually

Connect to your PostgreSQL database and run:

```sql
-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Set default values
UPDATE users SET tenant_id = '00000000-0000-0000-0000-000000000000'::UUID WHERE tenant_id IS NULL;
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    refresh_token_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id UUID,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(36),
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
```

## After Migration

Once the migration is complete, restart your backend server. The error should be resolved.

## Verify Migration

To verify the migration was successful:

```sql
-- Check users table columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check if new tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('user_sessions', 'audit_logs');
```

## Troubleshooting

If you get permission errors:
- Make sure your database user has ALTER TABLE and CREATE TABLE permissions
- Check that you're connected to the correct database

If columns already exist:
- The migration script uses `IF NOT EXISTS` so it's safe to run multiple times
- Existing data will be preserved

