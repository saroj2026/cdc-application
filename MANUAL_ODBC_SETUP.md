# Manual ODBC Driver Setup for SQL Server

## Quick Setup (if Homebrew is installed but not in PATH)

### Step 1: Add Homebrew to PATH (if needed)

If `brew` command doesn't work, add it to your PATH:

**For Apple Silicon (M1/M2/M3):**
```bash
export PATH="/opt/homebrew/bin:$PATH"
```

**For Intel Mac:**
```bash
export PATH="/usr/local/bin:$PATH"
```

To make it permanent, add the above line to your `~/.zshrc` or `~/.bash_profile`:
```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Verify Homebrew

```bash
brew --version
```

### Step 3: Install/Verify unixodbc

```bash
brew list unixodbc || brew install unixodbc
```

### Step 4: Install/Verify Microsoft ODBC Driver 18

```bash
# Add Microsoft tap if not already added
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release

# Install the driver
brew list msodbcsql18 || brew install msodbcsql18
```

### Step 5: Find the Driver Library

```bash
# For Apple Silicon
find /opt/homebrew -name "libmsodbcsql.18.dylib" 2>/dev/null

# For Intel Mac
find /usr/local -name "libmsodbcsql.18.dylib" 2>/dev/null
```

### Step 6: Register the Driver

Edit the ODBC configuration file:

**For Apple Silicon:**
```bash
sudo nano /opt/homebrew/etc/odbcinst.ini
```

**For Intel Mac:**
```bash
sudo nano /usr/local/etc/odbcinst.ini
```

Add this configuration (replace the Driver path with the actual path from Step 5):

```ini
[ODBC Driver 18 for SQL Server]
Description=Microsoft ODBC Driver 18 for SQL Server
Driver=/opt/homebrew/lib/libmsodbcsql.18.dylib
UsageCount=1
```

**Note:** If the driver is in a different location (like `/opt/homebrew/Cellar/msodbcsql18/...`), use that full path.

### Step 7: Test the Driver

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
python3 test_odbc_driver.py
```

You should see "ODBC Driver 18 for SQL Server" in the list.

### Step 8: Restart Backend

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_backend.sh
```

## Alternative: Use the Setup Script

If you prefer, you can use the automated setup script (it now handles Homebrew detection):

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./setup_odbc_driver.sh
```

## Troubleshooting

### Check if driver is registered

```bash
# Add Homebrew to PATH first if needed
export PATH="/opt/homebrew/bin:$PATH"

# Then check
odbcinst -q -d
```

### Check available drivers in Python

```bash
python3 -c "import pyodbc; print(pyodbc.drivers())"
```

### Manual Connection Test

```python
import pyodbc
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=your_server,1433;'
        'DATABASE=your_db;'
        'UID=user;'
        'PWD=password;'
        'TrustServerCertificate=yes;'
    )
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```


