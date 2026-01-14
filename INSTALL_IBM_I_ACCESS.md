# Installing IBM i Access Client Solutions (ODBC Driver) on macOS

## Overview
IBM i Access Client Solutions provides the ODBC driver needed to connect to AS400/IBM i systems. This guide will help you install it on macOS.

## Prerequisites
- macOS 10.14 (Mojave) or later
- Administrator access
- Internet connection

## Installation Steps

### Option 1: Download from IBM (Recommended)

1. **Download IBM i Access Client Solutions**
   - Visit: https://www.ibm.com/support/pages/ibm-i-access-client-solutions
   - Or direct download: https://www.ibm.com/support/pages/downloading-ibm-i-access-client-solutions
   - Select the macOS version (usually a `.dmg` file)

2. **Install the Package**
   ```bash
   # After downloading, open the .dmg file
   # Double-click the installer package
   # Follow the installation wizard
   ```

3. **Verify Installation**
   ```bash
   # Check if ODBC drivers are installed
   python3 << 'EOF'
   import pyodbc
   drivers = pyodbc.drivers()
   ibm_drivers = [d for d in drivers if 'IBM' in d.upper() or 'i' in d.lower()]
   if ibm_drivers:
       print("✅ IBM i Access ODBC Driver found:")
       for driver in ibm_drivers:
           print(f"   - {driver}")
   else:
       print("❌ IBM i Access ODBC Driver not found")
       print("Available drivers:")
       for driver in drivers:
           print(f"   - {driver}")
   EOF
   ```

### Option 2: Using Homebrew (Recommended for macOS)

**This is the easiest method for macOS:**

1. **Install unixODBC (if not already installed)**
   ```bash
   brew install unixodbc
   ```

2. **Add IBM's Homebrew Tap**
   ```bash
   brew tap ibm/iaccess https://public.dhe.ibm.com/software/ibmi/products/odbc/macos/tap/
   ```

3. **Install IBM i Access ODBC Driver**
   ```bash
   brew install ibm-iaccess
   ```

4. **Verify Installation**
   ```bash
   # Check if driver is installed
   odbcinst -q -d
   
   # Or check via Python
   python3 -c "import pyodbc; drivers = pyodbc.drivers(); ibm = [d for d in drivers if 'IBM' in d.upper()]; print('✅ Found:', ibm) if ibm else print('❌ Not found')"
   ```

### Option 3: Manual Installation via Terminal

1. **Download the installer**
   ```bash
   # Create a downloads directory
   mkdir -p ~/Downloads/ibm_i_access
   cd ~/Downloads/ibm_i_access
   
   # Download (replace URL with actual download link from IBM)
   # curl -O <IBM_DOWNLOAD_URL>
   ```

2. **Mount and Install**
   ```bash
   # Mount the DMG file
   hdiutil attach <downloaded_file>.dmg
   
   # Install (replace with actual package name)
   sudo installer -pkg /Volumes/IBM\ i\ Access\ Client\ Solutions/IBM\ i\ Access\ Client\ Solutions.pkg -target /
   
   # Unmount
   hdiutil detach /Volumes/IBM\ i\ Access\ Client\ Solutions
   ```

## Post-Installation Configuration

### 1. Verify ODBC Driver Installation

```bash
# Check ODBC drivers
python3 << 'EOF'
import pyodbc
try:
    drivers = pyodbc.drivers()
    print("Available ODBC Drivers:")
    print("=" * 80)
    for driver in drivers:
        print(f"  - {driver}")
    
    # Check for IBM drivers
    ibm_drivers = [d for d in drivers if any(keyword in d.upper() for keyword in ["IBM", "AS400", "ISERIES", "DB2"])]
    if ibm_drivers:
        print("\n✅ IBM/AS400 Drivers Found:")
        for driver in ibm_drivers:
            print(f"   ✅ {driver}")
    else:
        print("\n❌ No IBM/AS400 drivers found")
        print("   Please ensure IBM i Access Client Solutions is installed correctly")
except Exception as e:
    print(f"Error checking drivers: {e}")
EOF
```

### 2. Test Connection

After installation, test the AS400 connection:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate

python3 << 'PYEOF'
import requests

connection_id = "6a81833a-b96f-488e-a2ba-ef56d11b762f"

print("Testing AS400 Connection...")
try:
    response = requests.post(
        f"http://localhost:8000/api/v1/connections/{connection_id}/test",
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Connection test successful!")
            print(f"   Status: {result.get('status')}")
            if result.get('version'):
                print(f"   Version: {result.get('version')}")
        else:
            print(f"❌ Connection test failed: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
PYEOF
```

## Troubleshooting

### Issue: "No IBM i Access ODBC Driver found"

**Solution:**
1. Verify the installation completed successfully
2. Check if the driver is in the system:
   ```bash
   # List all ODBC drivers
   odbcinst -q -d
   ```
3. If the driver is not listed, reinstall IBM i Access Client Solutions

### Issue: "Neither DSN nor SERVER keyword supplied"

**Solution:**
1. Ensure the connection string is built correctly
2. Check that the driver name matches exactly (case-sensitive)
3. Verify the connection configuration includes:
   - `server` (hostname)
   - `port` (default: 446)
   - `user` (username)
   - `password`
   - `database` or `library` (library name)

### Issue: Connection Timeout

**Solution:**
1. Verify network connectivity to the AS400 server
2. Check firewall settings
3. Ensure the port (9471 in your case) is accessible
4. Verify credentials are correct

### Issue: Permission Denied

**Solution:**
1. Ensure you have administrator privileges
2. Try installing with `sudo`:
   ```bash
   sudo installer -pkg <package.pkg> -target /
   ```

## Alternative: Use Docker Container

If you cannot install IBM i Access Client Solutions directly, you can use a Docker container with the driver pre-installed:

```bash
# Example Dockerfile (if needed)
FROM python:3.9-slim

# Install IBM i Access Client Solutions in container
# (This would require the installer to be available)
```

## Verification Script

Run this script to verify everything is set up correctly:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
source venv/bin/activate

python3 << 'PYEOF'
import sys
import pyodbc

print("=" * 80)
print("IBM i Access ODBC Driver Verification")
print("=" * 80)

# Check pyodbc
try:
    print("\n1. Checking pyodbc...")
    print(f"   ✅ pyodbc version: {pyodbc.version}")
except Exception as e:
    print(f"   ❌ pyodbc error: {e}")
    sys.exit(1)

# Check available drivers
try:
    print("\n2. Checking ODBC drivers...")
    drivers = pyodbc.drivers()
    print(f"   Found {len(drivers)} drivers")
    
    # Check for IBM drivers
    ibm_drivers = [d for d in drivers if any(keyword in d.upper() for keyword in ["IBM", "AS400", "ISERIES", "DB2"])]
    
    if ibm_drivers:
        print("\n   ✅ IBM/AS400 Drivers Found:")
        for driver in ibm_drivers:
            print(f"      - {driver}")
    else:
        print("\n   ❌ No IBM/AS400 drivers found")
        print("   Please install IBM i Access Client Solutions")
        sys.exit(1)
    
    # Test connection string building
    print("\n3. Testing connection string...")
    test_driver = ibm_drivers[0]
    test_conn_str = (
        f"DRIVER={{{test_driver}}};"
        f"SYSTEM=pub400.com;"
        f"PORT=9471;"
        f"UID=segmetriq;"
        f"PWD=***;"
        f"DBQ=SEGMETRIQ1;"
    )
    print(f"   ✅ Connection string format: OK")
    print(f"   Driver: {test_driver}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Verification Complete - Ready to connect!")
print("=" * 80)
PYEOF
```

## Additional Resources

- **IBM i Access Client Solutions Documentation:**
  https://www.ibm.com/docs/en/i-access-client-solutions

- **ODBC Driver Documentation:**
  https://www.ibm.com/docs/en/i-access-client-solutions/1.1.0?topic=odbc-driver

- **Connection String Reference:**
  https://www.ibm.com/docs/en/i-access-client-solutions/1.1.0?topic=connection-odbc-connection-strings

## Notes

- The IBM i Access Client Solutions package is large (several hundred MB)
- Installation may require administrator privileges
- After installation, you may need to restart your terminal or IDE
- The ODBC driver should be automatically registered with the system

