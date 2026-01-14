# Azure Data Studio Setup Guide

## ✅ Installation Complete

Azure Data Studio has been successfully installed on your macOS system.

**Note:** Microsoft has announced that Azure Data Studio will be discontinued on 2026-02-28. However, it's still fully functional and will work for your needs.

## 🚀 Connecting to SQL Server

### Step 1: Open Azure Data Studio
- Open Spotlight (Cmd + Space) and search for "Azure Data Studio"
- Or open from Applications folder
- Or run from terminal: `azuredatastudio`

### Step 2: Create New Connection
1. Click **"New Connection"** button (top left) or press `Cmd + N`
2. Fill in the connection details:

   **Connection Details:**
   - **Connection type:** Microsoft SQL Server
   - **Server:** `72.61.233.209`
   - **Port:** `1433`
   - **Database:** `cdctest`
   - **Authentication type:** SQL Login
   - **Username:** `sa`
   - **Password:** `[Your SQL Server password]` (from your connection config)

3. Click **"Connect"**

### Step 3: Verify Connection
1. In the left sidebar, expand:
   - **Databases** → **cdctest** → **Tables** → **dbo** → **department**
2. Right-click on **department** table
3. Select **"Select Top 1000 Rows"**
4. Verify you can see the data (should show 8-9 rows)

## 📊 Useful Queries

### Check Row Count
```sql
SELECT COUNT(*) FROM dbo.department;
```

### View All Records
```sql
SELECT * FROM dbo.department ORDER BY id DESC;
```

### Check for Test Record
```sql
SELECT * FROM dbo.department WHERE id = 9;
```

### Verify CDC Replication
```sql
-- Check latest records
SELECT TOP 5 * FROM dbo.department ORDER BY id DESC;

-- Compare with PostgreSQL (if you have access)
-- PostgreSQL: SELECT COUNT(*) FROM public.department;
-- SQL Server: SELECT COUNT(*) FROM dbo.department;
```

## 🔄 Alternative Tools (If Needed)

Since Azure Data Studio is being discontinued, here are alternatives:

### 1. DBeaver (Free, Cross-platform)
```bash
brew install --cask dbeaver-community
```
- Universal database tool
- Supports SQL Server, PostgreSQL, MySQL, etc.
- Download: https://dbeaver.io/download/

### 2. TablePlus (Paid, macOS Native)
```bash
brew install --cask tableplus
```
- Beautiful, native macOS app
- Free tier available
- Download: https://tableplus.com/

### 3. DataGrip (Paid, JetBrains)
- Professional database IDE
- Download: https://www.jetbrains.com/datagrip/

## 🔧 Troubleshooting

### Connection Issues
- Verify SQL Server is accessible: `telnet 72.61.233.209 1433`
- Check firewall settings
- Verify credentials are correct
- Ensure SQL Server allows remote connections

### SSL Certificate Errors
- Azure Data Studio should handle SSL automatically
- If issues occur, check SQL Server SSL configuration

## 📝 Connection String Reference

For reference, your SQL Server connection details:
- **Server:** 72.61.233.209
- **Port:** 1433
- **Database:** cdctest
- **Schema:** dbo
- **Username:** sa
- **Authentication:** SQL Server Authentication

## ✅ Next Steps

1. Open Azure Data Studio
2. Connect to your SQL Server
3. Verify the `dbo.department` table
4. Check if test record (ID: 9) has been replicated
5. Monitor CDC replication in real-time


