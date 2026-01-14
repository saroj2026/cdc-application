#!/bin/bash
# Setup script for Microsoft ODBC Driver for SQL Server on macOS

set -e

echo "🔧 Setting up Microsoft ODBC Driver for SQL Server..."
echo ""

# Check if Homebrew is installed
# Try multiple common locations
BREW_PATH=""
if command -v brew &> /dev/null; then
    BREW_PATH="brew"
elif [ -f "/opt/homebrew/bin/brew" ]; then
    BREW_PATH="/opt/homebrew/bin/brew"
    export PATH="/opt/homebrew/bin:$PATH"
elif [ -f "/usr/local/bin/brew" ]; then
    BREW_PATH="/usr/local/bin/brew"
    export PATH="/usr/local/bin:$PATH"
else
    echo "❌ Homebrew is not found. Please install it first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew is installed at: $BREW_PATH"
echo ""

# Check if unixodbc is installed
if ! $BREW_PATH list unixodbc &> /dev/null; then
    echo "📦 Installing unixodbc..."
    $BREW_PATH install unixodbc
else
    echo "✅ unixodbc is already installed"
fi

echo ""

# Check if msodbcsql18 is installed
if ! $BREW_PATH list msodbcsql18 &> /dev/null; then
    echo "📦 Installing Microsoft ODBC Driver 18 for SQL Server..."
    echo "   This may require accepting Microsoft's license agreement..."
    $BREW_PATH tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
    $BREW_PATH install msodbcsql18
else
    echo "✅ msodbcsql18 is already installed"
fi

echo ""

# Find the driver library
DRIVER_PATH=""
if [ -f "/opt/homebrew/lib/libmsodbcsql.18.dylib" ]; then
    DRIVER_PATH="/opt/homebrew/lib/libmsodbcsql.18.dylib"
elif [ -f "/usr/local/lib/libmsodbcsql.18.dylib" ]; then
    DRIVER_PATH="/usr/local/lib/libmsodbcsql.18.dylib"
else
    # Try to find it in Cellar
    DRIVER_PATH=$(find /opt/homebrew/Cellar -name "libmsodbcsql.18.dylib" 2>/dev/null | head -1)
    if [ -z "$DRIVER_PATH" ]; then
        DRIVER_PATH=$(find /usr/local/Cellar -name "libmsodbcsql.18.dylib" 2>/dev/null | head -1)
    fi
fi

if [ -z "$DRIVER_PATH" ]; then
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

echo "📝 Configuring ODBC driver in: $ODBCINST_INI"
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
echo "If the driver is still not detected, try:"
echo "  1. Restart your terminal"
echo "  2. Restart the backend: ./start_backend.sh"
echo "  3. Check the driver manually: odbcinst -q -d"

