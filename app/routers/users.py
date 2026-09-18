"""User account routes: update username and delete account."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.put("", response_model=schemas.UserOut, summary="Update the current user's username")
def update_user(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = (
        db.query(models.User)
        .filter(models.User.username == user_in.username, models.User.id != current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    current_user.username = user_in.username
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    db.refresh(current_user)
    return current_user


@router.delete(
    "", status_code=status.HTTP_204_NO_CONTENT, summary="Delete the current user's account"
)
def delete_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Expenses are removed automatically via the cascade defined on User.expenses.
    db.delete(current_user)
    db.commit()
    return None
