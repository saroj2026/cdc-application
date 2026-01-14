# Frontend-Backend Integration Fixes

## Summary of Fixes Applied

### 1. ✅ Fixed Authentication Token Response Format
**Issue**: Backend returns `access_token` but frontend expected `token`
**Fix**: Updated `authSlice.ts` to handle both `access_token` and `token` fields

**Files Modified**:
- `frontend/lib/store/slices/authSlice.ts` - Updated login and signup thunks to handle `access_token`

### 2. ✅ Fixed Signup Endpoint Integration
**Issue**: Frontend called `/auth/signup` which doesn't exist in backend
**Fix**: Updated signup to use `/users/` endpoint and auto-login after registration

**Files Modified**:
- `frontend/lib/store/slices/authSlice.ts` - Signup now creates user via `/users/` then logs in

### 3. ✅ Added Missing API Client Methods
**Issue**: Frontend components called `apiClient.createUser()` and `apiClient.getPipelineCheckpoints()` which didn't exist
**Fix**: Added these methods to the API client

**Files Modified**:
- `frontend/lib/api/client.ts` - Added `createUser()` and `getPipelineCheckpoints()` methods

### 4. ✅ Created Default User Script
**Issue**: No default user exists for initial login
**Fix**: Created `create_default_user.py` script to create admin user

**Files Created**:
- `create_default_user.py` - Script to create default admin user

## Default Login Credentials

Once the database is running and you execute `create_default_user.py`, use:

```
Email:    admin@cdc.local
Password: admin123
Role:     admin
```

## How to Create Default User

### Option 1: Run Script (when backend/database is running)
```bash
cd seg-cdc-application
python create_default_user.py
```

### Option 2: Use Backend API (when backend is running)
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cdc.local",
    "full_name": "Admin User",
    "password": "admin123",
    "role_name": "admin"
  }'
```

### Option 3: Use Frontend Signup Page
1. Navigate to http://localhost:3000/auth/signup
2. Fill in the form with:
   - Full Name: Admin User
   - Email: admin@cdc.local
   - Password: admin123
   - Role: admin
3. Submit the form

## API Endpoint Mapping

### Authentication
- **Login**: `POST /api/v1/auth/login`
  - Request: `{ email, password }`
  - Response: `{ access_token, token_type, user }`
  
- **Get Current User**: `GET /api/v1/auth/me`
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ id, email, full_name, role_name, is_active, is_superuser }`

- **Logout**: `POST /api/v1/auth/logout`
  - Response: `{ message: "Logged out successfully" }`

### User Management
- **Create User**: `POST /api/v1/users/`
  - Request: `{ email, full_name, password, role_name }`
  - Response: `{ id, email, full_name, role_name, is_active, is_superuser, created_at, updated_at }`

- **List Users**: `GET /api/v1/users/`
  - Query params: `skip`, `limit`
  - Response: `[{ id, email, full_name, role_name, ... }]`

### Connections
- **Create Connection**: `POST /api/v1/connections`
- **List Connections**: `GET /api/v1/connections`
- **Test Connection**: `POST /api/v1/connections/test` or `POST /api/v1/connections/{id}/test`
- **Discover Databases**: `GET /api/v1/connections/{id}/databases`
- **Discover Schemas**: `GET /api/v1/connections/{id}/schemas`
- **Discover Tables**: `GET /api/v1/connections/{id}/tables`

### Pipelines
- **Create Pipeline**: `POST /api/v1/pipelines`
- **List Pipelines**: `GET /api/v1/pipelines`
- **Get Pipeline**: `GET /api/v1/pipelines/{id}`
- **Start Pipeline**: `POST /api/v1/pipelines/{id}/start`
- **Stop Pipeline**: `POST /api/v1/pipelines/{id}/stop`
- **Get Checkpoints**: `GET /api/v1/pipelines/{id}/checkpoints`

## Frontend-Backend Integration Status

### ✅ Working
- Login authentication
- User creation/signup
- Token storage and retrieval
- API client with interceptors
- Error handling

### ⚠️ Requires Backend Running
- All API endpoints require backend at `http://localhost:8000` (or configured `NEXT_PUBLIC_API_URL`)
- Database must be accessible (PostgreSQL on port 5434 or configured in `.env`)

### 🔧 Configuration
- Frontend API URL: Set `NEXT_PUBLIC_API_URL` in `.env.local` or environment
- Backend API URL: Configured in `frontend/lib/api/client.ts` (defaults to `http://localhost:8000/api/v1`)
- Database URL: Configured in `seg-cdc-application/.env` (defaults to `postgresql://cdc_user:cdc_password@localhost:5434/cdc_db`)

## Testing Integration

1. **Start Backend**:
   ```bash
   cd seg-cdc-application
   python -m ingestion.api
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Create Default User** (if not exists):
   ```bash
   python create_default_user.py
   ```

4. **Test Login**:
   - Navigate to http://localhost:3000/auth/login
   - Use credentials: `admin@cdc.local` / `admin123`

## Known Issues & Notes

1. **Database Connection**: The database must be running and accessible. If using Docker on VPS, ensure:
   - Database is accessible from your machine
   - Connection string in `.env` points to correct host/port
   - Network/firewall allows connections

2. **CORS**: Backend should have CORS configured to allow frontend origin

3. **Token Storage**: Tokens are stored in `localStorage` - ensure this is acceptable for your security requirements

4. **Password Hashing**: Currently using SHA256 + salt. For production, consider upgrading to bcrypt or argon2.



