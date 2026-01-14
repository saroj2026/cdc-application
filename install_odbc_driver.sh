#!/bin/bash
# Simple script to install Microsoft ODBC Driver for SQL Server

set -e

echo "🔧 Installing Microsoft ODBC Driver for SQL Server..."
echo ""

# Detect Homebrew location
if [ -f "/opt/homebrew/bin/brew" ]; then
    BREW="/opt/homebrew/bin/brew"
    export PATH="/opt/homebrew/bin:$PATH"
elif [ -f "/usr/local/bin/brew" ]; then
    BREW="/usr/local/bin/brew"
    export PATH="/usr/local/bin:$PATH"
else
    echo "❌ Homebrew not found. Please install Homebrew first."
    exit 1
fi

echo "✅ Using Homebrew at: $BREW"
echo ""

# Check if unixodbc is installed
if ! $BREW list unixodbc &> /dev/null; then
    echo "📦 Installing unixodbc..."
    $BREW install unixodbc
else
    echo "✅ unixodbc is already installed"
fi

echo ""

# Install Microsoft ODBC Driver 18
if ! $BREW list msodbcsql18 &> /dev/null; then
    echo "📦 Installing Microsoft ODBC Driver 18 for SQL Server..."
    echo "   This may require accepting Microsoft's license agreement..."
    echo ""
    
    # Add Microsoft tap
    $BREW tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
    
    # Install the driver
    $BREW install msodbcsql18
    
    echo ""
    echo "✅ Microsoft ODBC Driver 18 installed successfully!"
else
    echo "✅ msodbcsql18 is already installed"
fi

echo ""

# Find the driver library
echo "🔍 Locating driver library..."
DRIVER_PATH=""
if [ -f "/opt/homebrew/lib/libmsodbcsql.18.dylib" ]; then
    DRIVER_PATH="/opt/homebrew/lib/libmsodbcsql.18.dylib"
elif [ -f "/usr/local/lib/libmsodbcsql.18.dylib" ]; then
    DRIVER_PATH="/usr/local/lib/libmsodbcsql.18.dylib"
else
    # Try to find it in Cellar
    DRIVER_PATH=$($BREW --prefix msodbcsql18 2>/dev/null)/lib/libmsodbcsql.18.dylib
    if [ ! -f "$DRIVER_PATH" ]; then
        DRIVER_PATH=$(find /opt/homebrew/Cellar -name "libmsodbcsql.18.dylib" 2>/dev/null | head -1)
    fi
    if [ ! -f "$DRIVER_PATH" ]; then
        DRIVER_PATH=$(find /usr/local/Cellar -name "libmsodbcsql.18.dylib" 2>/dev/null | head -1)
    fi
fi

if [ -z "$DRIVER_PATH" ] || [ ! -f "$DRIVER_PATH" ]; then
    echo "⚠️  Could not find libmsodbcsql.18.dylib"
    echo "   Please check the installation manually"
    exit 1
fi

echo "✅ Found driver at: $DRIVER_PATH"
echo ""

# Determine odbcinst.ini location
if [ -f "/opt/homebrew/etc/odbcinst.ini" ]; then
    ODBCINST_INI="/opt/homebrew/etc/odbcinst.ini"
elif [ -f "/usr/local/etc/odbcinst.ini" ]; then
    ODBCINST_INI="/usr/local/etc/odbcinst.ini"
else
    echo "❌ Could not find odbcinst.ini"
    exit 1
fi

echo "📝 Registering driver in: $ODBCINST_INI"
echo ""

# Check if driver is already registered
if grep -q "ODBC Driver 18 for SQL Server" "$ODBCINST_INI" 2>/dev/null; then
    echo "✅ Driver is already registered in odbcinst.ini"
else
    echo "Adding driver configuration..."
    sudo tee -a "$ODBCINST_INI" > /dev/null <<EOF

[ODBC Driver 18 for SQL Server]
Description=Microsoft ODBC Driver 18 for SQL Server
Driver=$DRIVER_PATH
UsageCount=1
EOF
    echo "✅ Driver registered successfully"
fi

echo ""
echo "🧪 Testing ODBC driver detection..."
echo ""

# Test with Python
cd "$(dirname "$0")"
python3 test_odbc_driver.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Restart the backend: ./start_backend.sh"
echo "  2. Test your SQL Server connection in the UI"


