# Fix ODBC Driver for SQL Server on macOS

## Problem
The error "Data source name not found and no default driver specified" occurs because the Microsoft ODBC Driver for SQL Server is not properly registered with unixODBC.

## Solution

### Step 1: Verify Installation

Check if `msodbcsql18` and `unixodbc` are installed:

```bash
brew list msodbcsql18
brew list unixodbc
```

### Step 2: Find the Driver Location

The Microsoft ODBC Driver is typically installed at:
- `/opt/homebrew/lib/libmsodbcsql.18.dylib` (Apple Silicon)
- `/usr/local/lib/libmsodbcsql.18.dylib` (Intel)

### Step 3: Register the Driver

Create or edit `/opt/homebrew/etc/odbcinst.ini` (or `/usr/local/etc/odbcinst.ini` on Intel Macs):

```bash
sudo nano /opt/homebrew/etc/odbcinst.ini
```

Add the following configuration:

```ini
[ODBC Driver 18 for SQL Server]
Description=Microsoft ODBC Driver 18 for SQL Server
Driver=/opt/homebrew/lib/libmsodbcsql.18.dylib
UsageCount=1
```

**Note:** Replace `/opt/homebrew` with `/usr/local` if you're on an Intel Mac.

### Step 4: Verify Registration

Run the test script:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
python3 test_odbc_driver.py
```

You should see "ODBC Driver 18 for SQL Server" in the list.

### Step 5: Alternative - Specify Driver in Connection Config

If registration doesn't work, you can specify the driver name directly in the connection's `additional_config` field:

1. Go to the Connections page in the UI
2. Edit your SQL Server connection
3. In the "Additional Config" field (JSON), add:

```json
{
  "driver": "ODBC Driver 18 for SQL Server"
}
```

Or if you need to use the full path (not recommended, platform-specific):

```json
{
  "driver": "/opt/homebrew/lib/libmsodbcsql.18.dylib"
}
```

**Note:** The driver name should match exactly what's registered in `odbcinst.ini` or what `pyodbc.drivers()` returns.

### Step 6: Restart Backend

After fixing the ODBC driver registration, restart the backend:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_backend.sh
```

## Troubleshooting

### Check Driver File Exists

```bash
ls -la /opt/homebrew/lib/libmsodbcsql.18.dylib
```

### Check ODBC Configuration

```bash
odbcinst -q -d
```

### Test Connection Manually

```python
import pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=your_server,1433;'
    'DATABASE=your_db;'
    'UID=user;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
)
```

## References

- [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [unixODBC Documentation](http://www.unixodbc.org/)

