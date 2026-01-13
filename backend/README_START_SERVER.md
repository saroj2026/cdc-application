# How to Start the Backend Server

## Quick Start

### Option 1: Using Python Script (Recommended)
```bash
cd backend
python start_server.py
```

Or on Windows:
```bash
cd backend
py start_server.py
```

### Option 2: Using Uvicorn Directly
```bash
cd backend
uvicorn ingestion.api:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Batch File (Windows)
```bash
cd backend
start_server.bat
```

## Verify Server is Running

Once started, you should see:
```
============================================================
Starting CDC Pipeline API Server
============================================================
Host: 0.0.0.0
Port: 8000
Reload: True
URL: http://localhost:8000
============================================================
```

## Test the Server

Open your browser or use curl:
- Health check: http://localhost:8000/health
- API health: http://localhost:8000/api/health
- Root: http://localhost:8000/

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
1. Find the process: `netstat -ano | findstr :8000`
2. Kill the process: `taskkill /PID <PID> /F`
3. Or change the port in `env.example` and set `API_PORT=8001`

### Server Not Responding
1. Check if the server process is running
2. Check the terminal for error messages
3. Verify database connection in `.env` file
4. Check if all dependencies are installed: `pip install -r requirements.txt`

### Database Connection Issues
Make sure your `.env` file has the correct database URL:
```
DATABASE_URL=postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest
```

## Environment Variables

Create a `.env` file in the `backend` directory based on `env.example`:
```bash
cp env.example .env
```

Then edit `.env` with your configuration.

