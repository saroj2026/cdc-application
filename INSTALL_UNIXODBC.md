# Installing unixodbc for SQL Server Connections

## Problem
SQL Server connection tests are failing because `pyodbc` requires the `unixodbc` system library, which is not installed on macOS.

## Solution: Install unixodbc via Homebrew

### Step 1: Install Homebrew (if not already installed)

Open Terminal and run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. You may be prompted for your administrator password.

### Step 2: Install unixodbc

After Homebrew is installed, run:
```bash
brew install unixodbc
```

### Step 3: Verify Installation

Verify that unixodbc is installed:
```bash
brew list unixodbc
```

### Step 4: Test pyodbc

Test that pyodbc can now load:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate
python3 -c "import pyodbc; print('✅ pyodbc works!')"
```

### Step 5: Restart Backend

After installing unixodbc, restart the backend:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_backend.sh
```

## Alternative: If Homebrew Installation Fails

If you cannot install Homebrew, you can:

1. **Download unixodbc manually** from: https://www.unixodbc.org/
2. **Or use a pre-built binary** for macOS
3. **Or run the backend on a Linux server** where unixodbc is easier to install

## Verification

After installation, test a SQL Server connection:
```bash
curl -X POST http://localhost:8000/api/v1/connections/{connection_id}/test
```

The connection test should now succeed instead of showing "pyodbc is not installed" error.


