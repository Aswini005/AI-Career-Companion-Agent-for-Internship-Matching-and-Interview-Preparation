from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    revoke_token,
    oauth2_scheme,
)

router = APIRouter()


# ============================================================
# REGISTER
# ============================================================

@router.post("/register", status_code=201)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == data.email.lower())
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-compatible login endpoint.

    Swagger sends:
        username = user's email
        password = user's password
    """

    # Swagger calls the email field "username"
    user = (
        db.query(User)
        .filter(User.email == form_data.username.lower())
        .first()
    )

    # User does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create JWT
    # IMPORTANT:
    # create_access_token() expects user_id directly
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    revoke_token(token, db)

    return {
        "message": "Logged out successfully"
    }


# ============================================================
# CHANGE PASSWORD
# ============================================================

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check current password
    if not verify_password(
        data.current_password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Hash new password
    user.password_hash = hash_password(
        data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == email.lower())
        .first()
    )

    # Don't reveal whether email exists
    if not user:
        return {
            "message": (
                "If the email exists, a reset instruction "
                "has been generated."
            )
        }

    # Demo implementation.
    # In production, send this token by email.
    reset_token = create_access_token(user.id)

    return {
        "message": "Reset token generated for demo",
        "reset_token": reset_token
    }


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    from jose import jwt, JWTError
    from app.config import settings

    try:
        payload = jwt.decode(
            data.token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError()

        user = db.get(
            User,
            int(user_id)
        )

        if not user:
            raise ValueError()

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    # Hash new password
    user.password_hash = hash_password(
        data.new_password
    )

    db.commit()

    return {
        "message": "Password reset successfully"
    }