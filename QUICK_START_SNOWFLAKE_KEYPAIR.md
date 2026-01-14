# Quick Start: Snowflake Key Pair Setup

## Current Status

✅ **Key pair generated** - Files created in current directory  
❌ **Public key NOT associated with Snowflake user yet**  
❌ **Private key NOT added to connection yet**

## Next Steps (Do These Now)

### Step 1: Associate Public Key with Snowflake User

**Your Snowflake Username:** `CDC` (uppercase)

**Option A: Using SQL (Recommended)**

1. Connect to Snowflake:
   - Web UI: https://ybvyvaw-uv44557.snowflakecomputing.com
   - Or use SnowSQL client

2. Run this SQL command:

```sql
ALTER USER CDC SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxr07S1T7mwrYaKzT8CNRtHRIHg87LtYO2rVBQql/hkD3QohrSuVghYJ3VFlyphAUB6tmpSpdV7lgR/PfBhYuGE4flKiLYgrha8saSpMvsPQWVmXMxNveVrmgg63shlPn0VLy6TdVevA44DTsndSgmfgEvdn43zQeNpAu1AlQPWKmIj9/qA4MkrBNpQHWvn/htWNgTz5mxI0Xl0dLl0dbgUJSMVMNCKPgT5fQ0cLYR21cNT9un138mY3dBfesAEmp6CQyCndKEbmNxgbjXebZPhNt1nl5O0lQc25L3oX6VGYAX3QuT5QATwkQ3dKbjT5t2Ldi0Jo8YB3oIpTOyqn1EwIDAQAB';
```

3. Verify the key was set:

```sql
DESCRIBE USER CDC;
```

Look for `RSA_PUBLIC_KEY` in the output. It should show the public key.

**Option B: Using Snowflake Web UI**

1. Go to: https://ybvyvaw-uv44557.snowflakecomputing.com
2. Navigate to **Admin** → **Users**
3. Find user `CDC` and click on it
4. In the user details, find **RSA_PUBLIC_KEY** field
5. Copy the public key from file: `snowflake_public_key_for_sql.txt`
6. Paste it into the field
7. Save changes

### Step 2: Update Connection in Database

Run this command:

```bash
python update_snowflake_connection_with_key.py snowflake-s snowflake_rsa_key.p8
```

This will:
- Read the private key from `snowflake_rsa_key.p8`
- Update the `snowflake-s` connection in the database
- Add the private key to `additional_config`

### Step 3: Verify Connection Configuration

Check that everything is configured correctly:

```bash
python check_snowflake_connection_config.py
```

You should see:
- ✅ Private Key: Present
- ✅ Ready for sink connector creation

### Step 4: Create the Sink Connector

Once steps 1-3 are complete, create the Snowflake sink connector:

```bash
python create_sink_using_backend_logic.py
```

Or start the pipeline (which will create the sink connector):

```bash
python -c "import requests; r = requests.post('http://localhost:8000/api/v1/pipelines/ae7bb432-2fa8-48eb-90a0-d6bb4c164441/start', timeout=60); print('Status:', r.status_code); print('Response:', r.text[:500])"
```

## Files Created

- `snowflake_rsa_key.p8` - **PRIVATE KEY** (keep secure, already added to .gitignore)
- `snowflake_rsa_key.pub` - Public key in PEM format (for reference)
- `snowflake_public_key_for_sql.txt` - Public key for SQL command (already displayed above)

## Important Notes

1. **Security**: The private key file (`snowflake_rsa_key.p8`) is already in `.gitignore`. **Never commit this file to version control!**

2. **Username**: Snowflake usernames are case-sensitive. Use `CDC` (uppercase) as shown.

3. **Key Format**: The public key shown above is already in the correct base64 format for Snowflake SQL commands.

4. **Order Matters**: 
   - First: Set public key in Snowflake (Step 1)
   - Then: Add private key to connection (Step 2)
   - Finally: Create sink connector (Step 4)

## Troubleshooting

**If Step 1 fails:**
- Verify you're logged in as a user with ALTER USER privileges
- Check that username `CDC` exists and is spelled correctly (case-sensitive)
- Make sure you copy the entire public key string (no line breaks)

**If Step 2 fails:**
- Verify file `snowflake_rsa_key.p8` exists in current directory
- Check that connection name is correct: `snowflake-s`
- Ensure you have database connection permissions

**If Step 4 fails:**
- Verify Steps 1 and 2 completed successfully
- Check connection config: `python check_snowflake_connection_config.py`
- Review the error message for specific issues

## Full Documentation

See `SNOWFLAKE_KEY_PAIR_SETUP.md` for detailed documentation, troubleshooting, and security best practices.

