"""Users router."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid
import hashlib
import secrets

from ingestion.database import get_db
from sqlalchemy.orm import Session
from ingestion.audit import log_audit_event, mask_sensitive_data
from ingestion.routers.auth import get_current_user
from ingestion.database.models_db import UserModel

router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role_name: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    status: Optional[str] = None  # Frontend sends status, we'll map it to is_active if needed


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role_name: str
    is_active: bool
    created_at: datetime


def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        # Check if user already exists
        from ingestion.database.models_db import UserModel
        existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        new_user = UserModel(
            id=str(uuid.uuid4()),
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role_name=user_data.role_name,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        user_response = UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role_name=new_user.role_name,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="create_user",
            resource_type="user",
            resource_id=str(new_user.id),
            new_value=mask_sensitive_data(user_response.dict()),
            request=request
        )
        
        return user_response
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """List all users."""
    try:
        from ingestion.database.models_db import UserModel
        users = db.query(UserModel).all()
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role_name=user.role_name,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    try:
        from ingestion.database.models_db import UserModel
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing user."""
    try:
        from ingestion.database.models_db import UserModel
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Store old values for audit log
        old_value = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role_name": user.role_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser if hasattr(user, 'is_superuser') else False
        }
        
        # Update fields if provided
        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = db.query(UserModel).filter(
                UserModel.email == user_data.email,
                UserModel.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already in use by another user")
            user.email = user_data.email
        
        if user_data.password is not None and user_data.password.strip():
            user.hashed_password = hash_password(user_data.password)
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.role_name is not None:
            user.role_name = user_data.role_name
        
        # Handle status field (map to is_active if provided)
        if user_data.status is not None:
            # Map status values to is_active
            status_to_active = {
                "active": True,
                "invited": False,
                "suspended": False,
                "deactivated": False
            }
            user.is_active = status_to_active.get(user_data.status.lower(), user.is_active)
        elif user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        # Update is_superuser if provided
        if user_data.is_superuser is not None:
            user.is_superuser = user_data.is_superuser
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="update_user",
            resource_type="user",
            resource_id=str(user.id),
            old_value=mask_sensitive_data(old_value),
            new_value=mask_sensitive_data(user_response.dict()),
            request=request
        )
        
        return user_response
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

