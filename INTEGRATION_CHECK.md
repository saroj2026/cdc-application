# Frontend-Backend Integration Check Report

## Executive Summary

This document provides a comprehensive check of the frontend-backend integration status, identifying what's working, what's missing, and what needs to be fixed.

## Current Status

### ✅ Working Components

1. **Backend API Server**
   - FastAPI server running on port 8000
   - CORS configured for `http://localhost:3000` and `http://localhost:3001`
   - All endpoints use `/api/v1/` prefix

2. **Frontend Configuration**
   - Next.js app configured with API URL: `http://localhost:8000`
   - Environment variables set in `next.config.mjs`

3. **Backend Endpoints Available**
   - Connection management endpoints (CRUD operations)
   - Pipeline management endpoints
   - Monitoring endpoints
   - Discovery endpoints

### ⚠️ Issues Found

1. **Missing Frontend API Client**
   - Frontend code references `@/lib/store/slices/connectionSlice` but `lib` directory doesn't exist
   - No API client implementation found
   - Redux slices are referenced but not present

2. **API Endpoint Mismatch**
   - Backend uses `/api/v1/connections`
   - Documentation mentions `/api/connections` (without v1)
   - Need to verify frontend expectations

3. **Authentication**
   - Frontend has mock authentication in `/app/api/auth/login/route.ts`
   - Backend has JWT authentication endpoints but may not be fully integrated
   - Need to verify auth flow

## Detailed Analysis

### Backend API Endpoints

#### Connection Endpoints (All use `/api/v1/` prefix)
```
POST   /api/v1/connections              - Create connection
GET    /api/v1/connections               - List connections
GET    /api/v1/connections/{id}          - Get connection
PUT    /api/v1/connections/{id}         - Update connection
DELETE /api/v1/connections/{id}          - Delete connection
POST   /api/v1/connections/test          - Test connection (with data)
POST   /api/v1/connections/{id}/test     - Test connection (by ID)
GET    /api/v1/connections/{id}/test/history - Get test history
GET    /api/v1/connections/{id}/databases    - List databases
GET    /api/v1/connections/{id}/schemas      - List schemas
GET    /api/v1/connections/{id}/tables       - List tables
GET    /api/v1/connections/{id}/table/{name}/schema - Get table schema
GET    /api/v1/connections/{id}/discover      - Full discovery
```

#### Pipeline Endpoints
```
POST   /api/pipelines                    - Create pipeline
GET    /api/pipelines                    - List pipelines
GET    /api/pipelines/{id}               - Get pipeline
POST   /api/pipelines/{id}/start         - Start pipeline
POST   /api/pipelines/{id}/stop          - Stop pipeline
GET    /api/pipelines/{id}/tables/preview - Preview tables
```

#### Authentication Endpoints
```
POST   /api/v1/auth/login                - User login
POST   /api/v1/auth/signup               - User registration
POST   /api/v1/auth/logout               - User logout
GET    /api/v1/auth/me                   - Get current user
```

### Frontend Code Analysis

#### Files Referencing Backend
1. **`frontend/app/connections/page.tsx`**
   - Imports from `@/lib/store/slices/connectionSlice` (MISSING)
   - Uses Redux actions: `fetchConnections`, `createConnection`, `updateConnection`, `deleteConnection`, `testConnection`
   - Expects connection data structure with fields: `id`, `name`, `database_type`, `host`, `port`, etc.

2. **`frontend/components/pipelines/pipeline-wizard.tsx`**
   - Imports from `@/lib/store/slices/connectionSlice` (MISSING)
   - Uses `fetchConnections()` action

3. **`frontend/components/pipelines/pipeline-detail.tsx`**
   - Imports from `@/lib/store/slices/monitoringSlice` and `pipelineSlice` (MISSING)
   - Uses various pipeline and monitoring actions

#### Missing Frontend Files
The following files are referenced but don't exist:
- `frontend/lib/store/slices/connectionSlice.ts`
- `frontend/lib/store/slices/pipelineSlice.ts`
- `frontend/lib/store/slices/monitoringSlice.ts`
- `frontend/lib/store/hooks.ts`
- `frontend/lib/api/client.ts`
- `frontend/lib/database-icons.ts`
- `frontend/lib/database-colors.ts`
- `frontend/lib/database-logo-loader.ts`
- `frontend/lib/utils.ts`

### Data Structure Mapping

#### Connection Model

**Backend Returns:**
```python
{
    "id": "uuid-string",
    "name": "string",
    "connection_type": "source" | "target",
    "database_type": "postgresql" | "sqlserver" | "mysql" | "s3",
    "host": "string",
    "port": 5432,
    "database": "string",
    "username": "string",
    "password": "string",  # Should not be returned in GET requests
    "schema": "string" | null,
    "additional_config": {},
    "is_active": true,
    "last_tested_at": "ISO timestamp" | null,
    "last_test_status": "string" | null,
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
}
```

**Frontend Expects (based on code):**
```typescript
{
    id: number | string,  // Mixed usage
    name: string,
    database_type: string,  // Also referenced as "engine"
    connection_type: string,  // Also referenced as "role"
    host: string,
    port: number,
    database: string,
    username: string,
    password: string,
    schema?: string,
    ssl_enabled?: boolean
}
```

**Issues:**
- ID type mismatch (backend UUID string vs frontend number/string)
- Field name differences (`connection_type` vs `role`, `database_type` vs `engine`)
- `ssl_enabled` needs to be extracted from `additional_config`

#### Pipeline Model

**Backend Returns:**
```python
{
    "id": "uuid-string",
    "name": "string",
    "source_connection_id": "uuid-string",
    "target_connection_id": "uuid-string",
    "source_database": "string",
    "source_schema": "string",
    "source_tables": ["table1", "table2"],
    "target_database": "string" | null,
    "target_schema": "string" | null,
    "target_tables": ["table1", "table2"] | null,
    "mode": "full_load_only" | "cdc_only" | "full_load_and_cdc",
    "enable_full_load": true,
    "full_load_status": "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "FAILED",
    "cdc_status": "NOT_STARTED" | "STARTING" | "RUNNING" | "STOPPED" | "ERROR",
    "status": "STOPPED" | "STARTING" | "RUNNING" | "STOPPING" | "ERROR",
    "debezium_connector_name": "string" | null,
    "sink_connector_name": "string" | null,
    "kafka_topics": [],
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
}
```

**Frontend Expects:**
```typescript
{
    id: number | string,
    name: string,
    source_connection_id: number | string,
    target_connection_id: number | string,
    table_mappings?: Array<{source_table: string, target_table: string}>,
    cdc_enabled?: boolean,
    full_load_type?: string,
    status: "draft" | "active" | "paused" | "error"
}
```

**Issues:**
- Status values don't match (backend uses uppercase, frontend uses lowercase)
- `table_mappings` needs to be constructed from `source_tables` and `target_table_mapping`
- `mode` needs to be converted to `cdc_enabled` and `full_load_type`

## Required Fixes

### 1. Create Missing Frontend Files

#### Priority 1: API Client
**File:** `frontend/lib/api/client.ts`
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

#### Priority 2: Redux Store Setup
**File:** `frontend/lib/store/hooks.ts`
```typescript
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

#### Priority 3: Connection Slice
**File:** `frontend/lib/store/slices/connectionSlice.ts`
- Implement Redux slice with async thunks for all connection operations
- Map backend data structure to frontend format
- Handle ID type conversion (UUID string to number/string)

#### Priority 4: Pipeline Slice
**File:** `frontend/lib/store/slices/pipelineSlice.ts`
- Implement Redux slice for pipeline operations
- Map backend status values to frontend format
- Handle table mappings conversion

### 2. Fix Data Mapping

#### Connection Mapping Function
```typescript
function mapBackendConnectionToFrontend(backend: any) {
  return {
    id: backend.id,
    name: backend.name,
    database_type: backend.database_type,
    engine: backend.database_type,  // Alias
    connection_type: backend.connection_type,
    role: backend.connection_type,  // Alias
    host: backend.host,
    port: backend.port,
    database: backend.database,
    username: backend.username,
    password: backend.password || '',  // May not be returned
    schema: backend.schema || '',
    ssl_enabled: backend.additional_config?.ssl_enabled || false,
    is_active: backend.is_active,
    last_tested_at: backend.last_tested_at,
    last_test_status: backend.last_test_status,
  };
}
```

#### Pipeline Mapping Function
```typescript
function mapBackendPipelineToFrontend(backend: any) {
  // Convert mode to cdc_enabled and full_load_type
  const cdc_enabled = backend.mode !== 'full_load_only';
  const full_load_enabled = backend.mode !== 'cdc_only';
  
  // Convert status
  const statusMap: Record<string, string> = {
    'STOPPED': 'draft',
    'RUNNING': 'active',
    'STARTING': 'active',
    'STOPPING': 'paused',
    'ERROR': 'error',
  };
  
  // Build table mappings
  const table_mappings = backend.source_tables.map((source: string) => ({
    source_table: source,
    target_table: backend.target_table_mapping?.[source] || source,
  }));
  
  return {
    id: backend.id,
    name: backend.name,
    source_connection_id: backend.source_connection_id,
    target_connection_id: backend.target_connection_id,
    source_database: backend.source_database,
    source_schema: backend.source_schema,
    source_tables: backend.source_tables,
    target_database: backend.target_database,
    target_schema: backend.target_schema,
    table_mappings,
    cdc_enabled,
    full_load_enabled,
    full_load_type: backend.mode,
    mode: backend.mode,
    status: statusMap[backend.status] || 'draft',
    full_load_status: backend.full_load_status,
    cdc_status: backend.cdc_status,
  };
}
```

### 3. Fix API Endpoint Consistency

**Option A:** Update backend to use `/api/` instead of `/api/v1/`
**Option B:** Update frontend to use `/api/v1/` (RECOMMENDED - keeps versioning)

### 4. Authentication Integration

**Current State:**
- Backend has JWT authentication endpoints
- Frontend has mock authentication

**Required:**
- Update frontend to call backend `/api/v1/auth/login`
- Store JWT token in localStorage/cookies
- Add token to API requests via interceptor
- Handle token refresh

## Testing Checklist

### Connection Management
- [ ] Create connection via frontend
- [ ] List connections
- [ ] Update connection
- [ ] Delete connection
- [ ] Test connection
- [ ] View connection details

### Pipeline Management
- [ ] Create pipeline
- [ ] List pipelines
- [ ] View pipeline details
- [ ] Start pipeline
- [ ] Stop pipeline
- [ ] View pipeline status

### Discovery
- [ ] List databases
- [ ] List schemas
- [ ] List tables
- [ ] Get table schema
- [ ] Full discovery

### Monitoring
- [ ] View dashboard
- [ ] View pipeline metrics
- [ ] View replication lag
- [ ] View data quality

## Recommendations

1. **Immediate Actions:**
   - Create missing `lib` directory structure
   - Implement API client with proper error handling
   - Create Redux slices for state management
   - Add data mapping functions

2. **Short-term:**
   - Fix authentication flow
   - Standardize API endpoint paths
   - Add comprehensive error handling
   - Add loading states

3. **Long-term:**
   - Add TypeScript types for all API responses
   - Implement WebSocket for real-time updates
   - Add request/response logging
   - Add integration tests

## Environment Configuration

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
API_HOST=0.0.0.0
API_PORT=8000
```

## Conclusion

The backend API is fully functional and well-structured. The main issue is that the frontend is missing critical infrastructure files (API client, Redux slices, utilities). Once these are created with proper data mapping, the integration should work smoothly.

**Priority:** Create the missing frontend files to enable the integration.

