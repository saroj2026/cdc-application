#!/bin/bash

# Manual installation script for IBM i Access ODBC Driver
# Run this script in your terminal (it will prompt for password)

echo "================================================================================
📥 INSTALLING IBM i ACCESS ODBC DRIVER (macOS)
================================================================================
"

# Load Homebrew environment
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    export PATH="/opt/homebrew/bin:$PATH"
elif [ -f /usr/local/bin/brew ]; then
    export PATH="/usr/local/bin:$PATH"
fi

# Check if Homebrew is available
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed"
    echo "   Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew found: $(brew --version | head -n 1)"
echo ""

# Step 1: Install unixODBC
echo "1. Checking unixODBC..."
if brew list unixodbc &> /dev/null; then
    echo "   ✅ unixODBC already installed"
else
    echo "   Installing unixODBC..."
    brew install unixodbc
    if [ $? -eq 0 ]; then
        echo "   ✅ unixODBC installed successfully"
    else
        echo "   ❌ Failed to install unixODBC"
        exit 1
    fi
fi
echo ""

# Step 2: Add IBM tap
echo "2. Adding IBM i Access Homebrew tap..."
brew tap ibm/iaccess https://public.dhe.ibm.com/software/ibmi/products/odbc/macos/tap/ 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ IBM tap added successfully"
else
    echo "   ⚠️  Tap might already exist (this is OK)"
fi
echo ""

# Step 3: Install IBM i Access
echo "3. Installing IBM i Access ODBC Driver..."
echo "   ⚠️  You will be prompted for your administrator password"
echo "   This may take a few minutes..."
echo ""
brew install ibm-iaccess

if [ $? -eq 0 ]; then
    echo ""
    echo "   ✅ IBM i Access installed successfully"
else
    echo ""
    echo "   ❌ Failed to install IBM i Access"
    echo "   You may need to download and install manually from:"
    echo "   https://www.ibm.com/support/pages/ibm-i-access-client-solutions"
    exit 1
fi
echo ""

# Step 4: Verify installation
echo "4. Verifying installation..."
echo ""
echo "   Checking ODBC drivers via odbcinst:"
odbcinst -q -d 2>/dev/null | grep -i ibm || echo "   ⚠️  No IBM drivers found in odbcinst"
echo ""

echo "   Checking via Python:"
python3 << 'PYEOF'
import pyodbc
try:
    drivers = pyodbc.drivers()
    ibm_drivers = [d for d in drivers if any(keyword in d.upper() for keyword in ["IBM", "AS400", "ISERIES", "DB2"])]
    if ibm_drivers:
        print("   ✅ IBM/AS400 Drivers Found:")
        for driver in ibm_drivers:
            print(f"      - {driver}")
    else:
        print("   ❌ No IBM/AS400 drivers found")
        print("   Available drivers:")
        for driver in drivers[:10]:  # Show first 10
            print(f"      - {driver}")
        if len(drivers) > 10:
            print(f"      ... and {len(drivers) - 10} more")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo ""
echo "================================================================================
✅ Installation Complete!
================================================================================
"
echo "Next steps:"
echo "1. Restart your terminal or IDE"
echo "2. Test the AS400 connection:"
echo "   cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application"
echo "   source venv/bin/activate"
echo "   python3 -c \"import requests; r = requests.post('http://localhost:8000/api/v1/connections/6a81833a-b96f-488e-a2ba-ef56d11b762f/test'); print(r.json())\""
echo ""


