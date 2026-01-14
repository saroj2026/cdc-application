# Starting the Frontend

## Current Status

Node.js installation is in progress via nvm. Once installation completes, you can start the frontend.

## Quick Start (After Node.js is Installed)

### Option 1: Using the Startup Script

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_frontend.sh
```

### Option 2: Manual Start

```bash
# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use Node.js LTS
nvm use --lts

# Navigate to frontend
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Verify Node.js Installation

Check if Node.js is installed:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
node --version
npm --version
```

If Node.js is not installed, run:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
nvm use --lts
```

## Frontend Access

Once started, the frontend will be available at:
- **URL**: http://localhost:3000
- **Backend API**: http://localhost:8000 (should be running)

## Troubleshooting

### Node.js not found
1. Make sure nvm is loaded: `source ~/.nvm/nvm.sh`
2. Install Node.js: `nvm install --lts`
3. Use it: `nvm use --lts`

### npm install fails
- Check internet connection
- Try: `npm install --legacy-peer-deps`
- Clear cache: `npm cache clean --force`

### Port 3000 already in use
- Find process: `lsof -i :3000`
- Kill process: `kill -9 <PID>`
- Or use different port: `PORT=3001 npm run dev`



