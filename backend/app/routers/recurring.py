from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta

from app.database import get_db
from app.models import RecurringExpense, Expense
from app.schemas import (
    RecurringExpenseCreate, RecurringExpenseUpdate, RecurringExpenseResponse
)
from app.security import get_current_user

router = APIRouter()

@router.get("", response_model=list[RecurringExpenseResponse])
async def get_recurring_expenses(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recurring expenses for the user"""
    recurring = db.query(RecurringExpense).filter(
        RecurringExpense.owner_id == user_id
    ).all()
    return recurring

@router.post("", response_model=RecurringExpenseResponse)
async def create_recurring_expense(
    expense_data: RecurringExpenseCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring expense"""
    db_recurring = RecurringExpense(
        owner_id=user_id,
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        frequency=expense_data.frequency
    )
    db.add(db_recurring)
    db.commit()
    db.refresh(db_recurring)
    return db_recurring

@router.get("/{recurring_id}", response_model=RecurringExpenseResponse)
async def get_recurring_expense(
    recurring_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recurring expense"""
    recurring = db.query(RecurringExpense).filter(
        and_(RecurringExpense.id == recurring_id, RecurringExpense.owner_id == user_id)
    ).first()

    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring expense not found"
        )
    return recurring

@router.put("/{recurring_id}", response_model=RecurringExpenseResponse)
async def update_recurring_expense(
    recurring_id: int,
    expense_data: RecurringExpenseUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recurring expense"""
    recurring = db.query(RecurringExpense).filter(
        and_(RecurringExpense.id == recurring_id, RecurringExpense.owner_id == user_id)
    ).first()

    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring expense not found"
        )

    # Update fields
    if expense_data.amount is not None:
        recurring.amount = expense_data.amount
    if expense_data.category is not None:
        recurring.category = expense_data.category
    if expense_data.description is not None:
        recurring.description = expense_data.description
    if expense_data.frequency is not None:
        recurring.frequency = expense_data.frequency
    if expense_data.is_active is not None:
        recurring.is_active = expense_data.is_active

    db.commit()
    db.refresh(recurring)
    return recurring

@router.delete("/{recurring_id}")
async def delete_recurring_expense(
    recurring_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a recurring expense"""
    recurring = db.query(RecurringExpense).filter(
        and_(RecurringExpense.id == recurring_id, RecurringExpense.owner_id == user_id)
    ).first()

    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring expense not found"
        )

    db.delete(recurring)
    db.commit()
    return {"message": "Recurring expense deleted successfully"}

@router.post("/process")
async def process_recurring_expenses(db: Session = Depends(get_db)):
    """Process recurring expenses and generate new expenses (manual trigger)

    In production, this would be run by a scheduled task (APScheduler, Celery, etc)
    For now, it's manually triggered but can be called by a cron job or scheduler
    """
    now = datetime.utcnow()
    count = 0

    # Get all active recurring expenses
    recurring_expenses = db.query(RecurringExpense).filter(
        RecurringExpense.is_active == True
    ).all()

    for recurring in recurring_expenses:
        should_generate = False
        last_generated = recurring.last_generated or datetime(1970, 1, 1)

        # Check if we should generate based on frequency
        if recurring.frequency == "daily":
            should_generate = (now - last_generated).days >= 1
        elif recurring.frequency == "weekly":
            should_generate = (now - last_generated).days >= 7
        elif recurring.frequency == "monthly":
            should_generate = (
                now.month != last_generated.month or
                now.year != last_generated.year
            )
        elif recurring.frequency == "yearly":
            should_generate = now.year != last_generated.year

        # Generate new expense if needed
        if should_generate:
            new_expense = Expense(
                owner_id=recurring.owner_id,
                amount=recurring.amount,
                category=recurring.category,
                description=recurring.description or f"Recurring: {recurring.description}",
                date=now
            )
            db.add(new_expense)
            recurring.last_generated = now
            db.commit()
            count += 1

    return {
        "message": f"Generated {count} recurring expenses",
        "count": count
    }

@router.post("/generate-today")
async def generate_today_expenses(db: Session = Depends(get_db)):
    """Quick endpoint to generate today's recurring expenses"""
    return await process_recurring_expenses(db)
