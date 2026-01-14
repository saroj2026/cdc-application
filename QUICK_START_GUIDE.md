# 🚀 Quick Start Guide - CDC Pipeline Platform

## ✅ Current Status

### Backend Server
- **Status**: ✅ **RUNNING**
- **URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Process ID**: Running in background

### Frontend Server
- **Status**: 🟡 **STARTING** (new window opened)
- **URL**: http://localhost:3000
- **Command**: Running in separate PowerShell window

### Configuration
- **Kafka Connect (VPS)**: http://72.61.233.209:8083 ✅ Configured
- **Database**: localhost:5434 (may need to be started)

## 📋 Manual Start Commands

If you need to restart services manually:

### Start Backend
```powershell
cd seg-cdc-application
python -m ingestion.api
```

### Start Frontend
```powershell
cd seg-cdc-application/frontend
npm run dev
```

## 🌐 Access Points

1. **Frontend UI**: http://localhost:3000
   - Main application interface
   - Pipeline management
   - Connection management
   - Monitoring dashboard

2. **Backend API**: http://localhost:8000
   - REST API endpoints
   - Health checks

3. **API Documentation**: http://localhost:8000/docs
   - Interactive API documentation
   - Test endpoints directly

4. **Kafka Connect (VPS)**: http://72.61.233.209:8083
   - Kafka Connect REST API
   - Connector management

## 🔧 Configuration Files

### .env File
Located at: `seg-cdc-application/.env`

Key settings:
- `KAFKA_CONNECT_URL=http://72.61.233.209:8083` ✅
- `DATABASE_URL=postgresql://cdc_user:cdc_password@localhost:5434/cdc_management`
- `API_PORT=8000`

## ⚠️ Important Notes

### Database Setup
If you see database connection errors:
1. The database might need to be started locally
2. Or update `DATABASE_URL` in `.env` to point to VPS database
3. Run `python init_db.py` after database is accessible

### Kafka Connect
- Already configured to use VPS at `72.61.233.209:8083`
- No local Kafka setup needed

### Ports Required
- **3000**: Frontend (Next.js)
- **8000**: Backend (FastAPI)
- **5434**: Database (PostgreSQL) - if running locally

## 🐛 Troubleshooting

### Backend Not Starting
1. Check if port 8000 is available
2. Verify Python dependencies: `pip list`
3. Check `.env` file exists and is configured

### Frontend Not Starting
1. Check if port 3000 is available
2. Verify Node.js dependencies: `cd frontend && npm list`
3. Check for errors in the PowerShell window

### Database Connection Errors
1. Verify PostgreSQL is running (if using local database)
2. Check `DATABASE_URL` in `.env` file
3. Test connection: `python -c "from ingestion.database import engine; engine.connect()"`

## 📝 Next Steps

1. **Open Frontend**: Navigate to http://localhost:3000
2. **Create Connection**: Add source and target database connections
3. **Create Pipeline**: Set up your first CDC pipeline
4. **Monitor**: Use the monitoring dashboard to track pipeline status

## 🎯 Features Available

- ✅ Connection Management
- ✅ Pipeline Creation & Management
- ✅ Real-time Monitoring
- ✅ Full Load + CDC Support
- ✅ Multi-database Support (PostgreSQL, SQL Server, AS400, S3)
- ✅ Web-based UI

## 📚 Documentation

- **System Analysis**: `COMPREHENSIVE_SYSTEM_ANALYSIS.md`
- **Architecture**: `ARCHITECTURE.md`
- **Setup Guide**: `SETUP_COMPLETE.md`



