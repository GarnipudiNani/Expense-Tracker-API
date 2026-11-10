"""Shared FastAPI dependencies (e.g. current-user resolution from JWT)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = decode_access_token(token)

        # Validate the decoded payload
        if not isinstance(payload, dict):
            raise credentials_exception

        # Extract user ID
        user_id = payload.get("sub")

        # Validate user ID before database lookup
        if not isinstance(user_id, str) or not user_id.isascii() or not user_id.isdigit():
            raise credentials_exception

        user_id = int(user_id)
        if user_id <= 0:
            raise credentials_exception

    except (JWTError, ValueError, TypeError, AttributeError):
        raise credentials_exception

    # Retrieve authenticated user
    user = db.get(models.User, user_id)

    if user is None:
        raise credentials_exception

    return user
