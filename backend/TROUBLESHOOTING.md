# Backend Server Troubleshooting Guide

## Server is Running but Frontend Can't Connect

### 1. Verify Server is Running
```bash
# Check if port 8000 is listening
netstat -ano | findstr :8000

# Test health endpoint
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

### 2. Check CORS Configuration
The server has CORS enabled for all origins. If you're still getting CORS errors:
- Make sure the frontend is running on `http://localhost:3000` (default Next.js port)
- Check browser console for specific CORS error messages

### 3. Restart Both Servers
Sometimes a restart helps:
```bash
# Stop backend (Ctrl+C in terminal)
# Then restart:
cd backend
python start_server.py

# In another terminal, restart frontend:
cd frontend
npm run dev
```

### 4. Check Browser Console
Open browser DevTools (F12) and check:
- Network tab: Are requests being made? What's the status?
- Console tab: Any error messages?
- Check if requests are going to `http://localhost:8000`

### 5. Verify Environment Variables
Make sure `.env` file exists in `backend` directory:
```bash
cd backend
# Copy example if needed
cp env.example .env
```

### 6. Check Database Connection
The server might be running but database connection might be failing:
- Check backend terminal for database errors
- Verify `DATABASE_URL` in `.env` is correct
- Test database connection separately

### 7. Firewall/Antivirus
Sometimes Windows Firewall or antivirus blocks localhost connections:
- Temporarily disable firewall to test
- Add exception for Python/uvicorn

### 8. Try Different Port
If port 8000 has issues, try a different port:
```bash
# In backend/.env
API_PORT=8001

# Then restart server
python start_server.py
```

### 9. Check for Multiple Instances
Make sure only one backend server is running:
```bash
# Find all Python processes
tasklist | findstr python

# Kill specific process if needed
taskkill /PID <PID> /F
```

### 10. Clear Browser Cache
Sometimes cached data causes issues:
- Clear browser cache
- Try incognito/private mode
- Hard refresh (Ctrl+Shift+R)

## Common Error Messages

### "Cannot connect to server"
- Server is not running → Start with `python start_server.py`
- Wrong URL → Check `NEXT_PUBLIC_API_URL` in frontend
- Port conflict → Change port or kill existing process

### "CORS error"
- Already configured to allow all origins
- Check if request is actually reaching the server
- Verify request headers

### "Connection refused"
- Server not running
- Wrong port number
- Firewall blocking connection

### "Timeout"
- Server is slow to respond
- Database connection issues
- Increase timeout in frontend API client

## Quick Test Commands

```bash
# Test server health
curl http://localhost:8000/health

# Test API health
curl http://localhost:8000/api/health

# Test login endpoint (will fail without valid credentials, but should connect)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
```

## Still Having Issues?

1. Check backend terminal for error messages
2. Check frontend terminal for error messages
3. Check browser console for detailed errors
4. Verify both servers are running on expected ports
5. Try accessing backend directly in browser: http://localhost:8000

