#!/bin/bash

# Install dependencies and start frontend
cd "$(dirname "$0")"

echo "=========================================="
echo "Frontend Setup and Start Script"
echo "=========================================="
echo ""

# Load nvm
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    \. "$NVM_DIR/nvm.sh"
    echo "✅ nvm loaded"
else
    echo "❌ nvm not found. Please install nvm first:"
    echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

# Check/Install Node.js
if ! command -v node &> /dev/null; then
    echo "📦 Node.js not found. Installing LTS version..."
    nvm install --lts
    nvm use --lts
else
    echo "✅ Node.js found: $(node --version)"
    nvm use --lts 2>/dev/null || true
fi

# Verify Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js installation failed"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# Navigate to frontend directory
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    echo "   This may take a few minutes..."
    npm install
    echo ""
else
    echo "✅ Dependencies already installed"
    echo ""
fi

# Start frontend
echo "🚀 Starting frontend development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""

npm run dev



