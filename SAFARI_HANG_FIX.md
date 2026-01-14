# Safari Browser Hang Fix

## Issue
Safari browser hangs when accessing localhost:3000, likely due to:
1. Multiple polling intervals fetching large datasets every 5 seconds
2. Memory/CPU overload from processing 10,000+ events
3. Safari-specific performance issues with Next.js/Turbopack

## Quick Fixes

### 1. Clear Safari Cache
1. Open Safari
2. Go to **Safari > Settings > Privacy**
3. Click **Manage Website Data**
4. Search for "localhost" and remove it
5. Restart Safari

### 2. Use Chrome/Firefox Instead
Chrome and Firefox generally handle Next.js development better:
- Open http://localhost:3000 in Chrome or Firefox
- These browsers have better performance with modern web frameworks

### 3. Reduce Data Fetching (Temporary)
If you need to use Safari, you can temporarily reduce the data load:

**Edit `frontend/app/pipelines/page.tsx`:**
- Change `limit: 10000` to `limit: 100` on line 61
- Change interval from `5000` to `10000` (10 seconds instead of 5)

**Edit `frontend/app/monitoring/page.tsx`:**
- Change `limit: 1000` to `limit: 100` on lines 113 and 119
- Change interval from `5000` to `10000` (10 seconds instead of 5)

### 4. Disable WebSocket (If Not Needed)
If WebSocket is causing issues, you can disable it by setting:
```bash
export NEXT_PUBLIC_DISABLE_WS=true
```

### 5. Safari Developer Tools
1. Enable Safari Developer menu: **Safari > Settings > Advanced > Show Develop menu**
2. Open **Develop > Empty Caches**
3. Open **Develop > Web Inspector** to check for JavaScript errors

## Current Status
- Frontend restarted with clean cache
- Running on http://localhost:3000
- Next.js 16.0.7 (Turbopack) ready

## Recommended Solution
**Use Chrome or Firefox for development** - they handle Next.js/Turbopack much better than Safari.


