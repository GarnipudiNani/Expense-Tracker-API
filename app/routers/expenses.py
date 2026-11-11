"""Expense CRUD routes, with filtering by category and date range.

Every route here is scoped to the authenticated user: a user can only ever
see, create, update, or delete their own expenses.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _get_owned_expense_or_404(expense_id: int, user: models.User, db: Session) -> models.Expense:
    """Fetch an expense by id, scoped to the current user.

    Returns 404 (not 403) when the expense belongs to someone else, so that
    a user cannot use this endpoint to probe which expense ids exist for
    other users.
    """
    expense = db.scalar(
        select(models.Expense).where(
            models.Expense.id == expense_id,
            models.Expense.owner_id == user.id,
        )
    )
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.post(
    "",
    response_model=schemas.ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
    description="Creates an expense owned by the authenticated user.",
    responses={401: {"description": "Missing or invalid bearer token"}, 422: {"description": "Invalid expense fields"}},
)
def create_expense(
    expense_in: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = models.Expense(**expense_in.model_dump(), owner_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get(
    "",
    response_model=list[schemas.ExpenseOut],
    summary="List the current user's expenses (optionally filtered)",
    description="Returns only the authenticated user's expenses. Filtering and pagination are applied in the database query.",
    responses={400: {"description": "Invalid date range"}, 401: {"description": "Missing or invalid bearer token"}},
)
def list_expenses(
    category: Optional[str] = Query(default=None, description="Exact category match"),
    start_date: Optional[date] = Query(default=None, description="Include expenses on or after this date"),
    end_date: Optional[date] = Query(default=None, description="Include expenses on or before this date"),
    skip: int = Query(default=0, ge=0, description="Number of matching expenses to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum results (1–100)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after end_date",
        )

    query = select(models.Expense).where(models.Expense.owner_id == current_user.id)

    if category:
        query = query.where(models.Expense.category == category)
    if start_date:
        query = query.where(models.Expense.date >= start_date)
    if end_date:
        query = query.where(models.Expense.date <= end_date)

    query = query.order_by(models.Expense.date.desc()).offset(skip).limit(limit)
    return db.scalars(query).all()


@router.put(
    "/{expense_id}",
    response_model=schemas.ExpenseOut,
    summary="Update an expense",
    description="Partially updates one of the authenticated user's expenses. Send at least one non-null field.",
    responses={401: {"description": "Missing or invalid bearer token"}, 404: {"description": "Expense not found"}, 422: {"description": "Invalid or empty update"}},
)
def update_expense(
    expense_id: int,
    expense_in: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = _get_owned_expense_or_404(expense_id, current_user, db)

    updates = expense_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    responses={401: {"description": "Missing or invalid bearer token"}, 404: {"description": "Expense not found"}},
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = _get_owned_expense_or_404(expense_id, current_user, db)
    db.delete(expense)
    db.commit()
    return None
