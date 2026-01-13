# User Management Implementation Guide

## Overview

This document describes the production-grade User Management system implemented for the CDC Replication Application, including RBAC, audit logging, tenant isolation, and refresh tokens.

## Architecture Components

### 1. Database Models

#### Enhanced User Model
- Added `tenant_id` for multi-tenant isolation
- Added `status` field (INVITED, ACTIVE, SUSPENDED, DEACTIVATED)
- Enhanced `role_name` with enum support (SUPER_ADMIN, ORG_ADMIN, DATA_ENGINEER, OPERATOR, VIEWER)
- Added `last_login` tracking

#### User Session Model
- Stores refresh tokens
- Tracks IP address and user agent
- Expiration management

#### Audit Log Model
- Immutable audit trail
- Tracks all user actions
- Stores old/new values for changes
- Includes IP address and user agent

### 2. RBAC System (`backend/ingestion/rbac.py`)

#### Permission Matrix
- **SUPER_ADMIN**: Full access to everything
- **ORG_ADMIN**: User management, pipeline/connection management
- **DATA_ENGINEER**: Create pipelines and connections, trigger full loads
- **OPERATOR**: Start/stop/pause pipelines, view metrics
- **VIEWER**: Read-only access to dashboards and logs

#### Dependency Functions
- `require_roles(*roles)`: Require specific roles
- `require_permission(permission)`: Require specific permission
- `require_sensitive_action()`: For sensitive operations (reset offsets, delete pipeline)

### 3. Audit Logging (`backend/ingestion/audit.py`)

#### Features
- Automatic logging of all user actions
- Sensitive data masking (passwords, tokens)
- IP address and user agent tracking
- Tenant isolation

#### Usage
```python
from ingestion.audit import log_audit_event

log_audit_event(
    db=db,
    user=current_user,
    action="create_pipeline",
    resource_type="pipeline",
    resource_id=pipeline.id,
    new_value=mask_sensitive_data(pipeline_dict),
    request=request
)
```

## Implementation Steps

### Step 1: Database Migration

Run these SQL commands to add new columns and tables:

```sql
-- Add new columns to users table (if not exists)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS tenant_id UUID,
ADD COLUMN IF NOT EXISTS status VARCHAR(20),
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create index on tenant_id
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
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
```

### Step 2: Update Existing Users

Set default values for existing users:

```sql
-- Set default tenant_id (use a default UUID or generate one)
UPDATE users SET tenant_id = '00000000-0000-0000-0000-000000000000'::UUID WHERE tenant_id IS NULL;

-- Set default status
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Set default role if needed
UPDATE users SET role_name = 'viewer' WHERE role_name IS NULL OR role_name = '';
```

### Step 3: Update Auth Router

The auth router needs to be updated to:
1. Support refresh tokens
2. Include tenant_id in JWT
3. Track last_login
4. Support user status checks

### Step 4: Add RBAC to Endpoints

Update sensitive endpoints to use RBAC:

```python
from ingestion.rbac import require_roles, require_permission, require_sensitive_action
from ingestion.database.models_db import UserRole

@router.post("/pipelines")
async def create_pipeline(
    pipeline_data: PipelineCreate,
    current_user: UserModel = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.DATA_ENGINEER)),
    db: Session = Depends(get_db)
):
    # Implementation
    pass

@router.post("/pipelines/{pipeline_id}/reset-offsets")
async def reset_offsets(
    pipeline_id: str,
    current_user: UserModel = Depends(require_sensitive_action),
    db: Session = Depends(get_db)
):
    # Sensitive action - requires step-up auth
    pass
```

### Step 5: Add Audit Logging

Add audit logging to all write operations:

```python
from ingestion.audit import log_audit_event, mask_sensitive_data
from fastapi import Request

@router.post("/pipelines")
async def create_pipeline(
    pipeline_data: PipelineCreate,
    current_user: UserModel = Depends(get_current_user),
    request: Request,
    db: Session = Depends(get_db)
):
    # Create pipeline
    pipeline = create_pipeline_logic(pipeline_data, db)
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="create_pipeline",
        resource_type="pipeline",
        resource_id=str(pipeline.id),
        new_value=mask_sensitive_data(pipeline_to_dict(pipeline)),
        request=request
    )
    
    return pipeline
```

## Security Best Practices

### 1. Password Security
- Use bcrypt or argon2 (currently using SHA256 with salt - should upgrade)
- Enforce password complexity rules
- Implement password expiration

### 2. Token Security
- Short-lived access tokens (15-30 minutes)
- Long-lived refresh tokens (24 hours - 7 days)
- Token rotation on refresh
- Store refresh tokens hashed in database

### 3. Sensitive Actions
- Require password re-entry for:
  - Reset offsets
  - Delete pipeline
  - Change user roles
  - View connection credentials (never allowed)

### 4. Audit Logging
- Never log passwords or tokens (masked)
- Log all write operations
- Make audit logs immutable
- Regular audit log review

## Frontend Integration

### 1. Permission-Based UI
- Hide/show buttons based on user permissions
- Disable actions user can't perform
- Show appropriate error messages

### 2. Redux Slices
- `authSlice`: Authentication state
- `userSlice`: Current user info
- `permissionSlice`: User permissions
- `auditSlice`: Audit log viewing

### 3. API Client Updates
- Handle refresh token rotation
- Include tenant_id in requests
- Handle 403 errors gracefully

## Testing

### Unit Tests
- Test RBAC permission checks
- Test audit logging
- Test token refresh flow

### Integration Tests
- Test role-based endpoint access
- Test tenant isolation
- Test audit log creation

## Migration Checklist

- [ ] Run database migration SQL
- [ ] Update existing users with default values
- [ ] Update auth router with refresh tokens
- [ ] Add RBAC to all endpoints
- [ ] Add audit logging to write operations
- [ ] Update frontend with permission checks
- [ ] Test all role-based access
- [ ] Review and test audit logs
- [ ] Update documentation

## Next Steps (Optional Enhancements)

1. **SSO Integration**: OIDC/SAML support
2. **SCIM Provisioning**: Automated user provisioning
3. **Just-in-Time Access**: Temporary elevated permissions
4. **Password Policies**: Complexity, expiration, history
5. **MFA**: Multi-factor authentication
6. **Session Management**: View and revoke active sessions

