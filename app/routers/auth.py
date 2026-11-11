"""Authentication routes: signup and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(tags=["Authentication"])


@router.post(
    "/signup",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates an account. Passwords are hashed before storage; the response never includes password data.",
    responses={409: {"description": "Username already registered"}, 422: {"description": "Invalid registration fields"}},
)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(models.User).where(models.User.username == user_in.username)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    user = models.User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Login and obtain a JWT access token",
    description="Submit username and password as form fields. Use the returned bearer token on protected endpoints.",
    responses={401: {"description": "Incorrect username or password"}},
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(
        select(models.User).where(models.User.username == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token)
