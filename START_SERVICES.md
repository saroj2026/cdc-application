# Starting Backend and Frontend Services

## Backend (FastAPI) - Port 8000

### Started Automatically
The backend has been started in the background with the following configuration:
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Kafka Connect**: http://72.61.233.209:8083
- **Kafka Bootstrap**: 72.61.233.209:9092

### Manual Start (if needed)
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application

# Set environment variables
export KAFKA_CONNECT_URL=http://72.61.233.209:8083
export KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092
export DATABASE_URL=postgresql://cdc_user:cdc_password@localhost:5434/cdc_management

# Start backend
python3 -m ingestion.api
```

Or use the startup script:
```bash
./start_backend.sh
```

## Frontend (Next.js) - Port 3000

### Prerequisites
Node.js and npm need to be installed first.

### Install Node.js (if not installed)

**Option 1: Using Homebrew (macOS)**
```bash
brew install node
```

**Option 2: Using nvm (Node Version Manager)**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.zshrc

# Install Node.js LTS
nvm install --lts
nvm use --lts
```

**Option 3: Download from nodejs.org**
Visit https://nodejs.org/ and download the LTS version for macOS.

### Start Frontend

Once Node.js is installed:

```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Or use the startup script:
```bash
cd /Users/kumargaurav/Desktop/CDCTEAM/cdcteam/seg-cdc-application
./start_frontend.sh
```

The frontend will be available at: **http://localhost:3000**

## Verify Services

### Check Backend
```bash
curl http://localhost:8000/docs
# or
curl http://localhost:8000/api/v1/health
```

### Check Frontend
Open browser: http://localhost:3000

## Environment Variables

The backend uses these environment variables (set automatically in start_backend.sh):
- `KAFKA_CONNECT_URL=http://72.61.233.209:8083`
- `KAFKA_BOOTSTRAP_SERVERS=72.61.233.209:9092`
- `DATABASE_URL=postgresql://cdc_user:cdc_password@localhost:5434/cdc_management`
- `API_PORT=8000`

## Troubleshooting

### Backend not starting
1. Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```
2. Check Python dependencies:
   ```bash
   pip3 install fastapi uvicorn
   ```

### Frontend not starting
1. Ensure Node.js is installed:
   ```bash
   node --version
   npm --version
   ```
2. Install dependencies:
   ```bash
   cd frontend && npm install
   ```
3. Check if port 3000 is in use:
   ```bash
   lsof -i :3000
   ```

## Stop Services

### Stop Backend
```bash
pkill -f "python.*ingestion.api"
# or
pkill -f uvicorn
```

### Stop Frontend
Press `Ctrl+C` in the terminal where it's running, or:
```bash
pkill -f "next dev"
```



