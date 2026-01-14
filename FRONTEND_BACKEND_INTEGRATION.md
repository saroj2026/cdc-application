# Frontend-Backend Integration Guide

## Overview

The frontend (Next.js) has been connected to the Python FastAPI backend. This document outlines the changes made and how to use the integrated system.

## Changes Made

### 1. Backend CORS Configuration
- Added CORS middleware to `ingestion/api.py`
- Allows requests from `http://localhost:3000` and `http://localhost:3001` (Next.js default ports)
- Configured to allow all methods and headers

### 2. Frontend API Client Updates
**File**: `frontend/lib/api/client.ts`

#### Endpoint Path Changes
- Changed from `/api/v1/*` to `/api/*` to match backend
- Updated all connection endpoints
- Updated all pipeline endpoints
- Updated monitoring endpoints

#### Data Structure Mapping
- **Connections**: 
  - Frontend `role` → Backend `connection_type`
  - Frontend `engine` → Backend `database_type`
  - Added `ssl_enabled` mapping to `additional_config`
  
- **Pipelines**:
  - Frontend `table_mappings` → Backend `source_tables` + `target_table_mapping`
  - Frontend `cdc_enabled` + `full_load_type` → Backend `mode` (full_load_only, cdc_only, full_load_and_cdc)
  - Added `auto_create_target` support

#### ID Type Handling
- Backend uses string UUIDs, frontend expects numbers
- Updated all ID types to accept `string | number`
- Added conversion where needed

### 3. Redux Slice Updates
**Files**: 
- `frontend/lib/store/slices/connectionSlice.ts`
- `frontend/lib/store/slices/pipelineSlice.ts`

- Updated `Connection` interface to match backend model
- Updated `Pipeline` interface to match backend model
- Changed ID types from `number` to `string | number`
- Added backend-specific fields

### 4. New API Methods Added
- `getConnectionDatabases()` - List databases
- `getConnectionSchemas()` - List schemas
- `getTableSchema()` - Get table schema
- `discoverConnection()` - Full discovery
- `startPipeline()` - Start pipeline
- `getPipelineMetrics()` - Get metrics
- `getPipelineLag()` - Get replication lag
- `getPipelineHealth()` - Get health status
- `getPipelineDataQuality()` - Get data quality
- `getMonitoringDashboard()` - Get dashboard data

## API Endpoint Mapping

### Connections
| Frontend Method | Backend Endpoint | Status |
|----------------|-----------------|--------|
| `getConnections()` | `GET /api/connections` | ✅ |
| `getConnection(id)` | `GET /api/connections/{id}` | ✅ |
| `createConnection(data)` | `POST /api/connections` | ✅ |
| `updateConnection(id, data)` | `PUT /api/connections/{id}` | ✅ |
| `deleteConnection(id)` | `DELETE /api/connections/{id}` | ✅ |
| `testConnection(id)` | `POST /api/connections/{id}/test` | ✅ |
| `getConnectionTables(id)` | `GET /api/connections/{id}/tables` | ✅ |
| `getConnectionDatabases(id)` | `GET /api/connections/{id}/databases` | ✅ |
| `getConnectionSchemas(id, db?)` | `GET /api/connections/{id}/schemas` | ✅ |
| `getTableSchema(id, table, db?, schema?)` | `GET /api/connections/{id}/table/{table}/schema` | ✅ |
| `discoverConnection(id, db?, schema?)` | `GET /api/connections/{id}/discover` | ✅ |

### Pipelines
| Frontend Method | Backend Endpoint | Status |
|----------------|-----------------|--------|
| `getPipelines()` | `GET /api/pipelines` | ✅ |
| `getPipeline(id)` | `GET /api/pipelines/{id}` | ✅ |
| `createPipeline(data)` | `POST /api/pipelines` | ✅ |
| `updatePipeline(id, data)` | `PUT /api/pipelines/{id}` | ✅ |
| `deletePipeline(id)` | `DELETE /api/pipelines/{id}` | ✅ |
| `getPipelineStatus(id)` | `GET /api/pipelines/{id}/status` | ✅ |
| `startPipeline(id)` | `POST /api/pipelines/{id}/start` | ✅ |
| `stopPipeline(id)` | `POST /api/pipelines/{id}/stop` | ✅ |
| `triggerPipeline(id)` | `POST /api/pipelines/{id}/start` | ✅ (mapped) |
| `pausePipeline(id)` | `POST /api/pipelines/{id}/stop` | ✅ (mapped) |

### Monitoring
| Frontend Method | Backend Endpoint | Status |
|----------------|-----------------|--------|
| `getMonitoringDashboard()` | `GET /api/monitoring/dashboard` | ✅ |
| `getPipelineMetrics(id)` | `GET /api/monitoring/pipelines/{id}/metrics` | ✅ |
| `getMonitoringMetrics(id, start?, end?)` | `GET /api/monitoring/pipelines/{id}/metrics/history` | ✅ |
| `getPipelineLag(id)` | `GET /api/monitoring/pipelines/{id}/lag` | ✅ |
| `getPipelineHealth(id)` | `GET /api/monitoring/pipelines/{id}/health` | ✅ |
| `getPipelineDataQuality(id)` | `GET /api/monitoring/pipelines/{id}/data-quality` | ✅ |

### Not Yet Implemented
- Auth endpoints (login/logout) - Using mock for now
- User management endpoints
- Pipeline checkpoints
- Replication events
- LSN latency (using lag endpoint instead)

## Data Structure Differences

### Connection Model
**Frontend expects:**
```typescript
{
  id: number,
  role: 'source' | 'target',
  engine: string,
  ssl_enabled: boolean
}
```

**Backend provides:**
```python
{
  id: string,  # UUID
  connection_type: 'source' | 'target',
  database_type: string,
  additional_config: { ssl_enabled: boolean }
}
```

**Mapping:** Handled in `createConnection()` and `updateConnection()`

### Pipeline Model
**Frontend expects:**
```typescript
{
  id: number,
  table_mappings: [{ source_table, target_table }],
  cdc_enabled: boolean,
  full_load_type: string,
  status: 'draft' | 'active' | 'paused'
}
```

**Backend provides:**
```python
{
  id: string,  # UUID
  source_tables: [string],
  target_table_mapping: { source: target },
  mode: 'full_load_only' | 'cdc_only' | 'full_load_and_cdc',
  status: 'STOPPED' | 'RUNNING' | 'ERROR'
}
```

**Mapping:** Handled in `createPipeline()`

## Running the Application

### 1. Start Backend
```bash
# From project root
python -m ingestion.api
# or
uvicorn ingestion.api:app --host 0.0.0.0 --port 8000
```

### 2. Start Frontend
```bash
# From frontend directory
cd frontend
npm run dev
# or
pnpm dev
```

### 3. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

### Backend
- Database: Configured in `docker-compose.yml`
- Kafka Connect: http://localhost:8083

## Testing the Integration

1. **Test Connection Creation:**
   - Open frontend → Connections
   - Create a new connection
   - Verify it appears in the list

2. **Test Pipeline Creation:**
   - Open frontend → Pipelines
   - Create a new pipeline
   - Verify it appears in the list

3. **Test Monitoring:**
   - Open frontend → Monitoring
   - Check dashboard loads
   - View pipeline metrics

## Known Issues & Limitations

1. **Authentication**: Backend doesn't have auth yet - frontend uses mock token
2. **ID Types**: Some components may need updates for string UUIDs
3. **Status Values**: Frontend uses different status values than backend
4. **Missing Endpoints**: Some frontend features require endpoints not yet in backend

## Next Steps

1. Add authentication to backend
2. Implement missing endpoints (checkpoints, events)
3. Add WebSocket support for real-time updates
4. Update frontend components to handle string UUIDs properly
5. Add error handling for API mismatches


