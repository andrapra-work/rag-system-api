from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.models.auth import Token, UserCreate, UserLogin
from app.services.supabase import SupabaseService
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from datetime import timedelta
from app.config import get_settings
from app.api.dependencies.auth import get_current_user

settings = get_settings()
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase: SupabaseService = Depends()
):
    # Add debug print
    print(f"Attempting login for email: {form_data.username}")
    
    user = supabase.get_user_by_email(email=form_data.username)
    # Add debug print
    print(f"User found: {user is not None}")
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        # Add debug print
        print("Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Add debug print
    print("Login successful")
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={
            "sub": user["email"],
            "client_id": str(user["client_id"])
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    supabase: SupabaseService = Depends()
):
    print(f"Attempting to register email: {user_data.email}")  # Debug print
    
    # Check if user already exists
    existing_user = supabase.get_user_by_email(email=user_data.email)
    print(f"Existing user check result: {existing_user}")  # Debug print
    
    if existing_user:
        print(f"User already exists: {existing_user}")  # Debug print
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    try:
        print("Attempting to create user")  # Debug print
        new_user = supabase.client.table('users').insert({
            "email": user_data.email,
            "password_hash": hashed_password,
            "client_id": str(user_data.client_id)
        }).execute()
        print(f"Insert response: {new_user.data}")  # Debug print
        
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseService = Depends()
):
    # Verify old password
    if not verify_password(old_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Hash new password
    new_password_hash = get_password_hash(new_password)
    
    # Update password
    try:
        supabase.client.table('users')\
            .update({"password_hash": new_password_hash})\
            .eq("id", current_user["id"])\
            .execute()
        
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )