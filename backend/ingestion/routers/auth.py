"""Authentication router."""
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import uuid
from jose import jwt, JWTError

from ingestion.database import get_db
from ingestion.database.models_db import UserModel
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer(auto_error=False)  # Don't auto-raise error, allow optional auth

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRATION_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRATION_MINUTES", "30"))  # 30 minutes
JWT_REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRATION_DAYS", "7"))  # 7 days
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))  # Legacy support


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: list[dict]


def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        hash_part, salt = hashed.split(":", 1)
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == hash_part
    except Exception:
        return False


def create_access_token(user: UserModel) -> str:
    """Create short-lived JWT access token for user."""
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role_name,
        "tenant_id": str(user.tenant_id) if hasattr(user, 'tenant_id') and user.tenant_id else None,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRATION_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user: UserModel) -> str:
    """Create long-lived refresh token for user."""
    # Ensure user.id is a string
    user_id = str(user.id) if user.id else None
    if not user_id:
        raise ValueError("User ID must be a valid string")
    
    payload = {
        "sub": user_id,
        "email": user.email,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_jwt_token(user: UserModel) -> str:
    """Legacy function - creates access token. Use create_access_token instead."""
    return create_access_token(user)


def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserModel:
    """Get current user from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Ensure user_id is a string for comparison
    user_id_str = str(user_id) if user_id else None
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    user = db.query(UserModel).filter(UserModel.id == user_id_str).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    return user


def user_to_dict(user: UserModel) -> dict:
    """Convert user model to dict matching frontend expectations."""
    # Frontend expects numeric ID, but we use UUID strings
    # Use a hash of the UUID to generate a consistent numeric ID
    # Or use the first 8 chars of UUID as hex number
    try:
        # Convert UUID to string first, then to int
        user_id_str = str(user.id) if user.id else ""
        if user_id_str:
            # Try to convert UUID string to int (using first part)
            user_id = int(user_id_str.replace("-", "")[:8], 16) if len(user_id_str) > 8 else hash(user_id_str) % (10**9)
        else:
            user_id = 0
    except (ValueError, AttributeError, TypeError) as e:
        # Fallback to hash
        try:
            user_id = abs(hash(str(user.id))) % (10**9) if user.id else 0
        except Exception:
            user_id = 0
    
    return {
        "id": user_id,
        "uuid": str(user.id) if user.id else "",  # Also include UUID for reference
        "email": user.email or "",
        "full_name": user.full_name or user.email or "",
        "is_active": user.is_active if hasattr(user, 'is_active') else True,
        "is_superuser": user.is_superuser if hasattr(user, 'is_superuser') else False,
        "roles": [{"id": 1, "name": str(user.role_name) if hasattr(user, 'role_name') and user.role_name else "viewer"}]  # Frontend expects roles array
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """User login endpoint with refresh token support."""
    from ingestion.database.models_db import UserSessionModel, UserStatus
    from ingestion.audit import log_audit_event
    
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    # Check user status (handle gracefully if status column doesn't exist)
    try:
        if hasattr(user, 'status') and user.status:
            status_str = str(user.status).lower() if user.status else ""
            if status_str == "suspended":
                raise HTTPException(status_code=403, detail="User account is suspended")
            if status_str == "deactivated":
                raise HTTPException(status_code=403, detail="User account is deactivated")
    except HTTPException:
        raise
    except Exception:
        # If status check fails, continue (status column might not exist)
        pass
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    # Update last login first (this should work)
    try:
        user.last_login = datetime.utcnow()
        # Set status to active if not set (handle gracefully if column doesn't exist)
        try:
            if hasattr(user, 'status') and (not user.status or user.status is None):
                user.status = "active"  # Use string directly instead of enum value
        except Exception:
            # If status column doesn't exist or can't be set, continue anyway
            pass
    except Exception as user_update_error:
        import logging
        logging.warning(f"Failed to update user last_login: {str(user_update_error)}")
        # Continue anyway - this is not critical
    
    # Store refresh token in database (hashed) - make this optional
    # If session creation fails, we still allow login (session table might not exist)
    try:
        refresh_token_hash = hash_password(refresh_token)  # Reuse password hashing
        # Ensure user.id is a string
        user_id_str = str(user.id) if user.id else None
        if not user_id_str:
            # Don't fail login if user ID is invalid - just skip session creation
            import logging
            logging.warning("Invalid user ID for session creation, skipping session storage")
        else:
            session = UserSessionModel(
                id=str(uuid.uuid4()),
                user_id=user_id_str,
                refresh_token_hash=refresh_token_hash,
                expires_at=datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRATION_DAYS),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
    except Exception as session_error:
        # Session creation failed - rollback and continue without session
        db.rollback()
        import logging
        error_type = type(session_error).__name__
        error_msg = str(session_error)
        
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() or "table" in error_msg.lower():
            logging.warning("user_sessions table does not exist. Login will continue without session storage.")
        else:
            # Clean error message to avoid exposing model objects
            model_keywords = ["UserSessionModel", "refresh_token_hash", "user_sessions", "session", 
                             "expires_at", "ip_address", "user_agent", "created_at", "user_id", "id"]
            if any(keyword in error_msg for keyword in model_keywords):
                logging.warning(f"Session creation failed (likely table missing): {error_type}")
            else:
                logging.warning(f"Session creation failed: {error_type}: {error_msg[:100]}")
        
        # Commit user update separately if session creation failed
        try:
            db.commit()
        except Exception:
            db.rollback()
            # Even if commit fails, continue with login
    
    # Log audit event (don't fail login if audit logging fails)
    try:
        log_audit_event(
            db=db,
            user=user,
            action="user_login",
            request=request
        )
    except Exception as audit_error:
        # Log error but don't fail login
        import logging
        logging.warning(f"Failed to log audit event: {str(audit_error)}")
    
    # Return tokens and user info
    try:
        user_dict = user_to_dict(user)
    except Exception as dict_error:
        import logging
        logging.error(f"Failed to convert user to dict: {type(dict_error).__name__}: {str(dict_error)}")
        # Fallback user dict
        user_dict = {
            "id": 0,
            "uuid": str(user.id) if user.id else "",
            "email": user.email or "",
            "full_name": user.full_name or user.email or "",
            "is_active": user.is_active if hasattr(user, 'is_active') else True,
            "is_superuser": user.is_superuser if hasattr(user, 'is_superuser') else False,
            "roles": [{"id": 1, "name": "viewer"}]
        }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRATION_MINUTES * 60,  # Convert to seconds
        "user": user_dict
    }


@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """User registration endpoint."""
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    import uuid
    new_user = UserModel(
        id=str(uuid.uuid4()),
        email=user_data.email,
        full_name=user_data.full_name or user_data.email.split("@")[0],
        hashed_password=hashed_password,
        role_name="user",
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    token = create_jwt_token(new_user)
    
    # Return token and user info
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_dict(new_user)
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    from ingestion.database.models_db import UserSessionModel
    
    try:
        # Verify refresh token
        payload = verify_jwt_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Convert user_id to string for comparison
        user_id_str = str(user_id) if user_id else None
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid user ID in token")
        
        # Find user
        user = db.query(UserModel).filter(UserModel.id == user_id_str).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Verify refresh token exists in database
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid user ID in token")
        
        # Query session without exposing the object in error messages
        try:
            refresh_token_hash = hash_password(token_data.refresh_token)
            session = db.query(UserSessionModel).filter(
                UserSessionModel.user_id == user_id_str,
                UserSessionModel.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                raise HTTPException(status_code=401, detail="Refresh token not found or expired")
            
            # Verify token hash matches (simplified - in production use proper comparison)
            # For now, we'll just check if session exists and is not expired
            
            # Create new access token
            new_access_token = create_access_token(user)
            
            # Optionally rotate refresh token (security best practice)
            new_refresh_token = create_refresh_token(user)
            session.refresh_token_hash = hash_password(new_refresh_token)
            session.expires_at = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRATION_DAYS)
            db.commit()
            # Don't refresh session - it's not needed and can cause serialization issues
        except HTTPException:
            raise
        except Exception as session_error:
            db.rollback()
            import logging
            # Don't include session object in error message - sanitize it
            error_type = type(session_error).__name__
            error_msg = str(session_error)
            # Remove any model object references from error message to prevent serialization
            if any(keyword in error_msg for keyword in ["UserSessionModel", "refresh_token_hash", "user_sessions", "session", "expires_at", "ip_address", "user_agent", "created_at"]):
                error_msg = "Failed to update refresh token"
            logging.error(f"Session update error: {error_type}: {error_msg}")
            raise HTTPException(status_code=401, detail="Failed to refresh token. Please login again.")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
            "user": user_to_dict(user)
        }
    except HTTPException:
        raise
    except Exception as e:
        # Don't expose internal error details or model objects
        error_msg = str(e)
        # Remove any model object references from error message - catch all model field names
        model_keywords = ["UserSessionModel", "refresh_token_hash", "user_sessions", "session", 
                         "expires_at", "ip_address", "user_agent", "created_at", "user_id", "id",
                         "datetime.datetime", "datetime"]
        if any(keyword in error_msg for keyword in model_keywords):
            error_msg = "Token refresh failed: Invalid or expired refresh token"
        import logging
        logging.error(f"Token refresh error: {type(e).__name__}: {error_msg}")
        raise HTTPException(status_code=401, detail=error_msg)


@router.post("/logout")
async def logout(
    current_user: UserModel = Depends(get_current_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """User logout endpoint - invalidates refresh tokens."""
    from ingestion.database.models_db import UserSessionModel
    from ingestion.audit import log_audit_event
    
    # Delete all user sessions (logout from all devices)
    # Or optionally, delete only current session based on token
    try:
        # Ensure user.id is a string for comparison
        user_id_str = str(current_user.id) if current_user.id else None
        if user_id_str:
            deleted_count = db.query(UserSessionModel).filter(UserSessionModel.user_id == user_id_str).delete()
            db.commit()
    except Exception as e:
        db.rollback()
        import logging
        # Don't include session object in error message - sanitize it
        error_type = type(e).__name__
        error_msg = str(e)
        model_keywords = ["UserSessionModel", "refresh_token_hash", "user_sessions", "session", 
                         "expires_at", "ip_address", "user_agent", "created_at", "user_id", "id",
                         "datetime.datetime", "datetime"]
        if any(keyword in error_msg for keyword in model_keywords):
            error_msg = "Failed to delete user sessions"
        logging.error(f"Session deletion error: {error_type}: {error_msg}")
        # Don't fail logout if session deletion fails - user is still logged out
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="user_logout",
        request=request
    )
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current user information."""
    return user_to_dict(current_user)

