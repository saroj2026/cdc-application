# Installing pgAdmin on macOS

## Option 1: Direct Download (Recommended - Easiest)

### Steps:

1. **Download pgAdmin**
   - Visit: https://www.pgadmin.org/download/pgadmin-4-macos/
   - Download the latest `.dmg` file

2. **Install**
   - Open the downloaded `.dmg` file
   - Drag `pgAdmin 4.app` to your Applications folder
   - Open pgAdmin from Applications

3. **First Launch**
   - Set a master password (for storing server passwords)
   - pgAdmin will open in your default web browser

## Option 2: Install Homebrew First, Then pgAdmin

### Step 1: Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. You may need to enter your password.

### Step 2: Install pgAdmin

```bash
brew install --cask pgadmin4
```

### Step 3: Launch pgAdmin

```bash
open -a "pgAdmin 4"
```

Or find it in Applications and double-click.

## Option 3: Using pip (Python Package)

If you prefer to install via Python:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
pip install pgadmin4
```

Then run:
```bash
pgadmin4
```

## Connecting to Your PostgreSQL Database

Once pgAdmin is installed:

1. **Open pgAdmin**
2. **Right-click "Servers"** → **Create** → **Server**
3. **General Tab**:
   - Name: `CDC PostgreSQL Server` (or any name)
4. **Connection Tab**:
   - Host: `72.61.233.209`
   - Port: `5432`
   - Database: `cdctest`
   - Username: `cdc_user`
   - Password: `cdc_pass`
   - Check "Save password"
5. **Click "Save"**

## Quick Access

After installation, you can:
- View all databases
- Browse tables and data
- Run SQL queries
- Monitor replication slots
- Check LSN positions
- View CDC-related tables

## Useful Queries in pgAdmin

### Check Replication Slots (CDC LSN)
```sql
SELECT 
    slot_name,
    confirmed_flush_lsn AS cdc_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    active
FROM pg_replication_slots;
```

### Check Current WAL LSN
```sql
SELECT pg_current_wal_lsn() AS current_lsn;
```

### View Pipeline Tables
```sql
SELECT * FROM pipelines;
SELECT * FROM pipeline_metrics ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 10;
```


