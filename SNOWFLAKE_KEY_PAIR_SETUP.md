# Snowflake Key Pair Authentication Setup Guide

## Overview

The Snowflake Kafka Connector **does not support password authentication**. It requires:
- **Key-pair authentication** (RSA private/public key), OR
- **OAuth authentication**

This guide walks you through setting up key-pair authentication.

## Step 1: Generate Key Pair

Run the key generation script:

```bash
python generate_snowflake_keypair.py
```

This will create three files:
- `snowflake_rsa_key.p8` - **PRIVATE KEY** (keep secure!)
- `snowflake_rsa_key.pub` - Public key in PEM format (for reference)
- `snowflake_public_key_for_sql.txt` - Public key in base64 format (for SQL command)

**Security Note:** The private key file has been set to 600 permissions (owner read/write only). Do NOT commit this file to version control!

## Step 2: Associate Public Key with Snowflake User

### Option A: Using Snowflake Web UI

1. Log into Snowflake Web UI (https://ybvyvaw-uv44557.snowflakecomputing.com)
2. Go to **Admin** → **Users** (or run SQL: `SHOW USERS;`)
3. Find your user and click on it
4. In the user details, find **RSA_PUBLIC_KEY** field
5. Copy the public key from `snowflake_public_key_for_sql.txt` (it's a long base64 string)
6. Paste it into the RSA_PUBLIC_KEY field
7. Save the changes

### Option B: Using SQL (SnowSQL or Web UI SQL Worksheet)

1. Connect to Snowflake using SnowSQL or the Web UI SQL Worksheet
2. Run this SQL command (replace `<your_username>` and `<public_key_b64>`):

```sql
ALTER USER <your_username> SET RSA_PUBLIC_KEY='<public_key_b64>';
```

**Example:**
```sql
ALTER USER MYUSER SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...';
```

3. Verify the key was set:

```sql
DESCRIBE USER <your_username>;
```

Look for `RSA_PUBLIC_KEY` in the output. It should show your public key.

## Step 3: Update Connection in Database

### Option A: Using the Update Script (Recommended)

```bash
python update_snowflake_connection_with_key.py snowflake-s snowflake_rsa_key.p8
```

Replace `snowflake-s` with your actual connection name if different.

### Option B: Manual Update via SQL

1. Read the private key file:
   ```bash
   cat snowflake_rsa_key.p8
   ```

2. Connect to PostgreSQL database and update:

```sql
-- First, check current connection config
SELECT id, name, additional_config 
FROM connections 
WHERE name = 'snowflake-s' AND database_type = 'snowflake';

-- Update with private key (replace <private_key_content> with actual key)
UPDATE connections
SET additional_config = jsonb_set(
    COALESCE(additional_config, '{}'::jsonb),
    '{private_key}',
    '"<private_key_content>"'::jsonb
)
WHERE name = 'snowflake-s' AND database_type = 'snowflake';

-- Verify update
SELECT name, additional_config->>'private_key' as has_private_key
FROM connections 
WHERE name = 'snowflake-s';
```

**Note:** When storing in JSON, the private key needs to be properly escaped. The script handles this automatically.

## Step 4: Verify Setup

### Test Connection Configuration

```bash
python check_snowflake_connection_config.py
```

This will verify that:
- Private key is stored in the connection
- Connection has all required fields
- Ready for sink connector creation

### Create Sink Connector

Once the connection is updated with the private key, create the sink connector:

```bash
python create_sink_using_backend_logic.py
```

Or start the pipeline:

```bash
python -c "import requests; r = requests.post('http://localhost:8000/api/v1/pipelines/ae7bb432-2fa8-48eb-90a0-d6bb4c164441/start', timeout=60); print('Status:', r.status_code); print('Response:', r.text[:500])"
```

## Troubleshooting

### Error: "Invalid private key format"

- Ensure the private key file contains the full key including:
  ```
  -----BEGIN PRIVATE KEY-----
  ...
  -----END PRIVATE KEY-----
  ```
- When storing in JSON, ensure newlines are escaped as `\n`

### Error: "Authentication failed" when creating connector

1. Verify the public key is correctly set in Snowflake:
   ```sql
   DESCRIBE USER <your_username>;
   ```
   
2. Ensure the private key in the database matches the public key in Snowflake

3. Check that you're using the correct username (case-sensitive in Snowflake)

### Error: "RSA_PUBLIC_KEY must be set"

- Make sure you completed Step 2 (associating public key with user)
- Verify the key was set correctly using `DESCRIBE USER`

### Private Key Format Issues

The private key should be stored exactly as it appears in the `.p8` file, including:
- Header: `-----BEGIN PRIVATE KEY-----`
- Base64 content (multiple lines)
- Footer: `-----END PRIVATE KEY-----`

When storing in JSON, the newlines should be `\n` (the update script handles this).

## Security Best Practices

1. **Never commit private keys to version control**
   - Add `snowflake_rsa_key.p8` to `.gitignore`
   - Add `*_key*.p8` and `*_key*.pem` to `.gitignore`

2. **Store private keys securely**
   - Use encrypted storage if possible
   - Limit file permissions (600 = owner read/write only)
   - Consider using a secrets management service for production

3. **Rotate keys regularly**
   - Generate new key pairs periodically
   - Update Snowflake user and connection configuration
   - Remove old public keys from Snowflake user

4. **Use different keys for different environments**
   - Separate keys for dev, staging, and production
   - Different keys for different users/services

## Key Pair Format

- **Private Key**: PKCS#8 format, PEM encoding (`.p8` extension)
- **Public Key**: SubjectPublicKeyInfo format, PEM encoding (`.pub` extension)
- **Public Key for Snowflake**: Base64-encoded DER format (for SQL commands)

## Additional Resources

- [Snowflake Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)
- [Snowflake Kafka Connector Documentation](https://docs.snowflake.com/en/user-guide/kafka-connector-install.html)
- [Snowflake Kafka Connector Configuration](https://docs.snowflake.com/en/user-guide/kafka-connector-ts.html)

