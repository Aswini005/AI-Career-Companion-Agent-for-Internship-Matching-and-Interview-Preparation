from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, RevokedToken


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)

    expires = now + timedelta(
        minutes=settings.access_token_minutes
    )

    jti = str(uuid4())

    payload = {
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": expires
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = int(payload["sub"])
        jti = payload["jti"]
        exp = payload["exp"]

    except (JWTError, KeyError, ValueError):
        raise credentials_error

    # Check whether token has been revoked
    if db.query(RevokedToken).filter_by(
        jti=jti
    ).first():
        raise credentials_error

    # Find user
    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise credentials_error

    return user


def revoke_token(
    token: str,
    db: Session
):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}
        )

        exp = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        ).replace(tzinfo=None)

        jti = payload["jti"]

        if not db.query(RevokedToken).filter_by(
            jti=jti
        ).first():

            db.add(
                RevokedToken(
                    jti=jti,
                    expires_at=exp
                )
            )

            db.commit()

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user_optional(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)),
    db: Session = Depends(get_db)
) -> User | None:
    if not token or token == "demo-jwt-token":
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload["sub"])
        jti = payload["jti"]
        if db.query(RevokedToken).filter_by(jti=jti).first():
            return None
        return db.get(User, user_id)
    except Exception:
        return None