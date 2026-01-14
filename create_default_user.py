"""Create a default admin user for the CDC application."""

import sys
import os
import uuid
import hashlib
import secrets

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.database import SessionLocal
from ingestion.database.models_db import UserModel

def hash_password(password: str) -> str:
    """Hash a password using SHA256 (matches backend implementation)."""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt

def create_default_user():
    """Create a default admin user."""
    db = SessionLocal()
    
    try:
        # Default admin credentials
        default_email = "admin@cdc.local"
        default_password = "admin123"
        default_name = "Admin User"
        
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.email == default_email).first()
        if existing_user:
            print(f"✅ User already exists: {default_email}")
            print(f"   Password: {default_password}")
            return
        
        # Create default admin user
        hashed_password = hash_password(default_password)
        
        new_user = UserModel(
            id=str(uuid.uuid4()),
            email=default_email,
            full_name=default_name,
            hashed_password=hashed_password,
            role_name="admin",
            is_superuser=True,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("=" * 60)
        print("✅ Default Admin User Created Successfully!")
        print("=" * 60)
        print(f"Email:    {default_email}")
        print(f"Password: {default_password}")
        print(f"Role:     admin")
        print("=" * 60)
        print("\nYou can now login with these credentials at:")
        print("  http://localhost:3000/auth/login")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating default user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()



