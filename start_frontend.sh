#!/bin/bash

# Start Frontend (Next.js)
cd "$(dirname "$0")"

# Try to load nvm if available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo ""
    echo "Please install Node.js first:"
    echo "  1. Using nvm: nvm install --lts && nvm use --lts"
    echo "  2. Or download from: https://nodejs.org/"
    echo ""
    echo "See INSTALL_NODEJS.md for detailed instructions"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

cd frontend

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies (this may take a few minutes)..."
    npm install
    echo ""
fi

echo "Starting Frontend on http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

npm run dev

