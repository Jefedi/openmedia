"""Profile management routes"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
import shutil
import os
from pathlib import Path
import uuid

from app.db.session import get_db
from app.models.user import User
from app.routes.auth import get_current_active_user
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/profile", tags=["Profile"])


# Schemas
class ProfileResponse(BaseModel):
    """Profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Profile update data"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)

    @validator('username')
    def validate_username(cls, v):
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens and underscores')
        return v


class EmailUpdate(BaseModel):
    """Email update data"""
    new_email: EmailStr
    current_password: str


class PasswordUpdate(BaseModel):
    """Password update data"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class AccountDeletion(BaseModel):
    """Account deletion confirmation"""
    password: str
    confirmation: str

    @validator('confirmation')
    def validate_confirmation(cls, v):
        if v != "DELETE":
            raise ValueError('Confirmation must be "DELETE"')
        return v


# Routes
@router.get("/me", response_model=ProfileResponse)
def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get current user profile"""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


@router.put("/me", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Check if username is already taken (if being updated)
    if profile_data.username and profile_data.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == profile_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = profile_data.username

    # Update other fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

    if profile_data.bio is not None:
        current_user.bio = profile_data.bio

    db.commit()
    db.refresh(current_user)

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


@router.put("/email")
def update_email(
    email_data: EmailUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Update user email"""
    # Verify current password
    if not verify_password(email_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Check if email is already taken
    existing_user = db.query(User).filter(
        User.email == email_data.new_email,
        User.id != current_user.id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Update email
    current_user.email = email_data.new_email
    current_user.is_verified = False  # Require re-verification

    db.commit()

    return {"message": "Email updated successfully", "email": email_data.new_email}


@router.put("/password")
def update_password(
    password_data: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Update user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Check if new password is different
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)

    db.commit()

    return {"message": "Password updated successfully"}


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    # Check file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, GIF and WebP are allowed"
        )

    # Check file size (max 5MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )

    # Create uploads directory if it doesn't exist
    upload_dir = Path("/app/uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    finally:
        file.file.close()

    # Delete old avatar if exists
    if current_user.avatar_url:
        old_file_path = Path("/app" + current_user.avatar_url)
        if old_file_path.exists():
            try:
                old_file_path.unlink()
            except:
                pass  # Ignore errors when deleting old file

    # Update user avatar URL
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url

    db.commit()

    return {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}


@router.delete("/avatar")
def delete_avatar(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Delete profile picture"""
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No avatar to delete"
        )

    # Delete file
    file_path = Path("/app" + current_user.avatar_url)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Continue even if file deletion fails
            pass

    # Remove avatar URL from user
    current_user.avatar_url = None

    db.commit()

    return {"message": "Avatar deleted successfully"}


@router.delete("/me")
def delete_account(
    deletion_data: AccountDeletion,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Delete user account (requires password and confirmation)"""
    # Verify password
    if not verify_password(deletion_data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Delete avatar file if exists
    if current_user.avatar_url:
        file_path = Path("/app" + current_user.avatar_url)
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass

    # Delete user (cascade will delete related records)
    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}
