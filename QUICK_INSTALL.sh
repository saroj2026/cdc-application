#!/bin/bash

# Quick installation script - Run this in your terminal
# Password will be prompted securely

echo "================================================================================
📥 INSTALLING IBM i ACCESS ODBC DRIVER
================================================================================
"

# Load Homebrew
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    export PATH="/opt/homebrew/bin:$PATH"
fi

# Install
echo "Installing IBM i Access ODBC Driver..."
echo "You will be prompted for your password"
echo ""

brew tap ibm/iaccess https://public.dhe.ibm.com/software/ibmi/products/odbc/macos/tap/ 2>/dev/null
brew install ibm-iaccess

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Verifying installation..."
    python3 << 'PYEOF'
import pyodbc
try:
    drivers = pyodbc.drivers()
    ibm_drivers = [d for d in drivers if any(keyword in d.upper() for keyword in ["IBM", "AS400", "ISERIES", "DB2"])]
    if ibm_drivers:
        print("✅ IBM/AS400 Drivers Found:")
        for driver in ibm_drivers:
            print(f"   - {driver}")
    else:
        print("❌ No IBM/AS400 drivers found")
except Exception as e:
    print(f"Error: {e}")
PYEOF
else
    echo ""
    echo "❌ Installation failed"
    exit 1
fi

