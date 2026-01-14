# Frontend Changes Required for Oracle Support

## Summary

The backend has been fully updated to support Oracle as a source database. The frontend needs minor updates to display Oracle as an option and handle Oracle-specific configurations.

## Files That Need Updates

### 1. `frontend/lib/database-icons.ts`

**Current Status:** Needs Oracle entry

**Required Changes:**
```typescript
// Add Oracle to database types
export const DATABASE_TYPES = [
  'postgresql',
  'sqlserver',
  'mysql',
  's3',
  'as400',
  'snowflake',
  'oracle'  // ADD THIS
] as const;

// Add Oracle icon/logo
export function getDatabaseByConnectionType(type: string) {
  switch (type) {
    // ... existing cases ...
    case 'oracle':
      return {
        name: 'Oracle',
        icon: 'OracleIcon',  // Add Oracle icon component
        color: '#F80000',  // Oracle red color
        logo: '/logos/oracle.svg'  // Oracle logo path
      };
    // ...
  }
}

// Add Oracle color
export function getDatabaseColor(type: string): string {
  switch (type) {
    // ... existing cases ...
    case 'oracle':
      return '#F80000';  // Oracle red
    // ...
  }
}
```

### 2. `frontend/app/connections/page.tsx`

**Current Status:** May need Oracle-specific form fields

**Required Changes:**
- Add Oracle to database type dropdown
- Add optional "Service Name" field (alternative to SID)
- Handle Oracle-specific connection parameters

**Example:**
```typescript
// In connection form
{databaseType === 'oracle' && (
  <div>
    <label>Service Name (optional, alternative to SID)</label>
    <input 
      type="text" 
      name="service_name"
      value={additionalConfig.service_name || ''}
      onChange={(e) => setAdditionalConfig({
        ...additionalConfig,
        service_name: e.target.value
      })}
    />
  </div>
)}
```

### 3. `frontend/app/pipelines/page.tsx`

**Current Status:** Has hardcoded defaults for PostgreSQL/SQL Server

**Required Changes:**
- Add Oracle default schema handling
- Oracle default schema is typically the username

**Example:**
```typescript
// Update schema defaults
const source_schema = sourceConn.schema || (
  sourceConn.database_type === 'postgresql' ? 'public' : 
  sourceConn.database_type === 'sqlserver' ? 'dbo' :
  sourceConn.database_type === 'oracle' ? sourceConn.username :  // Oracle default
  'public'
)
```

### 4. `frontend/components/connections/connection-form.tsx` (if exists)

**Required Changes:**
- Add Oracle to database type selector
- Add Oracle-specific fields:
  - Service Name (optional)
  - Connection Mode (normal, sysdba, sysoper) - optional

### 5. `frontend/components/pipelines/pipeline-wizard.tsx`

**Current Status:** Uses `getDatabaseByConnectionType`

**Required Changes:**
- Should work automatically if `database-icons.ts` is updated
- Verify Oracle appears in source database selection
- Verify Oracle → Snowflake pipeline creation works

## Testing Checklist

After making frontend changes:

- [ ] Oracle appears in database type dropdown when creating connection
- [ ] Oracle connection form shows correct fields
- [ ] Oracle connection can be created and tested
- [ ] Oracle appears as source option in pipeline wizard
- [ ] Oracle → Snowflake pipeline can be created
- [ ] Oracle schema defaults correctly (uses username)
- [ ] Oracle tables can be discovered
- [ ] Pipeline with Oracle source can be started

## Oracle-Specific UI Considerations

### 1. Connection Form Fields

**Required:**
- Host
- Port (default: 1521)
- Database (SID) OR Service Name
- Username
- Password
- Schema (defaults to username)

**Optional (in additional_config):**
- Service Name (if using service name instead of SID)
- Connection Mode (normal, sysdba, sysoper)

### 2. Schema Handling

Oracle schemas are typically uppercase and match the username. The UI should:
- Default schema to username if not provided
- Handle case sensitivity (Oracle is case-sensitive for identifiers)
- Show warning if schema doesn't match username (common Oracle pattern)

### 3. Table Discovery

Oracle table names are typically uppercase. The UI should:
- Display tables in uppercase (or as stored)
- Handle case-sensitive table selection
- Show schema.table format clearly

## Implementation Priority

1. **High Priority:**
   - Add Oracle to `database-icons.ts`
   - Add Oracle to database type dropdowns
   - Fix schema defaults in pipeline creation

2. **Medium Priority:**
   - Add Service Name field to connection form
   - Add Oracle-specific validation

3. **Low Priority:**
   - Oracle-specific UI styling/colors
   - Oracle logo/icon
   - Advanced Oracle connection options

## Notes

- The backend already supports Oracle fully
- Frontend changes are mainly cosmetic/UI updates
- Oracle → Snowflake pipeline will work once Oracle is selectable in UI
- All CDC functionality (full load, CDC, auto-configuration) works automatically

