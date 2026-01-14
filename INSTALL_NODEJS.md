# Installing Node.js for Frontend

## Quick Install Options

### Option 1: Using Homebrew (Recommended for macOS)

If you have Homebrew installed:
```bash
brew install node
```

Then verify:
```bash
node --version
npm --version
```

### Option 2: Using nvm (Node Version Manager)

1. Install nvm:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

2. Reload your shell:
```bash
source ~/.zshrc
# or
source ~/.bash_profile
```

3. Install Node.js LTS:
```bash
nvm install --lts
nvm use --lts
```

4. Verify:
```bash
node --version
npm --version
```

### Option 3: Download from nodejs.org

1. Visit: https://nodejs.org/
2. Download the LTS version for macOS
3. Run the installer
4. Restart your terminal
5. Verify:
```bash
node --version
npm --version
```

## After Installing Node.js

Once Node.js is installed, start the frontend:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:3000**



