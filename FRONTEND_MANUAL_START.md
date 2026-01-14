# Manual Frontend Start Instructions

Since automated Node.js installation may take time, here are manual steps:

## Step 1: Open a New Terminal

Open a **new terminal window** (the automated installation may need a fresh shell).

## Step 2: Load nvm and Install Node.js

```bash
# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js LTS (if not already installed)
nvm install --lts

# Use the LTS version
nvm use --lts

# Verify
node --version
npm --version
```

## Step 3: Navigate and Install Dependencies

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/frontend

# Install dependencies (first time only - takes a few minutes)
npm install
```

## Step 4: Start Frontend

```bash
npm run dev
```

Or use the all-in-one script:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./install_and_start_frontend.sh
```

## Expected Output

Once started, you should see:
```
✓ Ready in X seconds
○ Local:        http://localhost:3000
```

## Troubleshooting

### If nvm command not found:
```bash
# Add to ~/.zshrc or ~/.bash_profile
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

Then reload:
```bash
source ~/.zshrc
```

### If npm install fails:
- Check internet connection
- Try: `npm install --legacy-peer-deps`
- Clear cache: `npm cache clean --force`

### If port 3000 is in use:
```bash
lsof -i :3000
kill -9 <PID>
```

## Current Status

- ✅ Backend: Running on http://localhost:8000
- ⏳ Frontend: Needs Node.js installation and dependency installation



