"""Generate RSA key pair for Snowflake authentication.

This script generates a private/public key pair that can be used with
Snowflake Kafka Connector for authentication.
"""

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

def generate_keypair():
    """Generate RSA 2048-bit key pair for Snowflake."""
    print("=" * 70)
    print("Snowflake Key Pair Generator")
    print("=" * 70)
    
    # Generate private key
    print("\n1. Generating RSA 2048-bit key pair...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    print("   ✅ Key pair generated successfully")
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key in PKCS8 format (PEM)
    print("\n2. Serializing keys...")
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key in SubjectPublicKeyInfo format (PEM)
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    # Extract public key in format Snowflake expects (base64 encoded DER)
    public_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_key_b64 = base64.b64encode(public_der).decode('utf-8')
    
    print("   ✅ Keys serialized successfully")
    
    # Save to files
    private_key_file = "snowflake_rsa_key.p8"
    public_key_file = "snowflake_rsa_key.pub"
    public_key_sql_file = "snowflake_public_key_for_sql.txt"
    
    print(f"\n3. Saving keys to files...")
    
    # Save private key
    with open(private_key_file, 'w') as f:
        f.write(private_pem)
    os.chmod(private_key_file, 0o600)  # Read/write for owner only
    print(f"   ✅ Private key saved to: {private_key_file}")
    
    # Save public key (PEM format)
    with open(public_key_file, 'w') as f:
        f.write(public_pem)
    print(f"   ✅ Public key (PEM) saved to: {public_key_file}")
    
    # Save public key for SQL (single line, base64)
    with open(public_key_sql_file, 'w') as f:
        f.write(public_key_b64)
    print(f"   ✅ Public key (SQL format) saved to: {public_key_sql_file}")
    
    # Display instructions
    print("\n" + "=" * 70)
    print("NEXT STEPS - Associate Public Key with Snowflake User")
    print("=" * 70)
    
    print("\n📋 PUBLIC KEY FOR SNOWFLAKE (copy this entire block):")
    print("-" * 70)
    print(public_key_b64)
    print("-" * 70)
    
    print("\n🔧 SQL COMMAND TO ASSOCIATE KEY WITH SNOWFLAKE USER:")
    print("-" * 70)
    print(f"""ALTER USER <your_snowflake_username> SET RSA_PUBLIC_KEY='{public_key_b64}';""")
    print("-" * 70)
    
    print("\n📝 Step-by-Step Instructions:")
    print("\n1. Connect to Snowflake (using SnowSQL, Snowflake Web UI, or other client)")
    print("\n2. Run the SQL command above, replacing <your_snowflake_username> with")
    print("   your actual Snowflake username.")
    print("   Example:")
    print(f"   ALTER USER MYUSER SET RSA_PUBLIC_KEY='{public_key_b64[:50]}...';")
    print("\n3. Verify the key was set:")
    print("   DESCRIBE USER <your_snowflake_username>;")
    print("   (Look for RSA_PUBLIC_KEY in the output)")
    print("\n4. Update your connection in the database:")
    print("   - Open the snowflake connection record")
    print("   - Add to additional_config: {")
    print('     "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----"')
    print("   }")
    print("\n   OR use the script: update_snowflake_connection_with_key.py")
    
    print("\n" + "=" * 70)
    print("SECURITY WARNING")
    print("=" * 70)
    print("⚠️  Keep your private key secure!")
    print(f"   - Private key file: {private_key_file}")
    print("   - Do NOT commit this file to version control")
    print("   - Store it securely (encrypted if possible)")
    print("   - Only share the PUBLIC key with Snowflake")
    print("   - The private key file has been set to 600 permissions (owner read/write only)")
    
    print("\n" + "=" * 70)
    
    return {
        'private_key': private_pem,
        'private_key_file': private_key_file,
        'public_key': public_pem,
        'public_key_file': public_key_file,
        'public_key_b64': public_key_b64,
        'public_key_sql_file': public_key_sql_file
    }

if __name__ == "__main__":
    try:
        result = generate_keypair()
        print("\n✅ Key pair generation completed successfully!")
        print(f"\nFiles created:")
        print(f"  - {result['private_key_file']} (PRIVATE - keep secure!)")
        print(f"  - {result['public_key_file']} (PUBLIC - for reference)")
        print(f"  - {result['public_key_sql_file']} (PUBLIC - for SQL command)")
        
    except Exception as e:
        print(f"\n❌ Error generating key pair: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

