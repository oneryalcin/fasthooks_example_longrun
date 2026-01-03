from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Budget
from app.schemas import BudgetCreate, BudgetUpdate, BudgetResponse, CategoryEnum
from app.security import get_current_user

router = APIRouter()

@router.get("", response_model=list[BudgetResponse])
async def get_budgets(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets for the user"""
    budgets = db.query(Budget).filter(Budget.owner_id == user_id).all()
    return budgets

@router.post("", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    # Check if budget already exists for this category
    existing = db.query(Budget).filter(
        and_(Budget.owner_id == user_id, Budget.category == budget_data.category)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Budget already exists for {budget_data.category.value}"
        )

    db_budget = Budget(
        owner_id=user_id,
        category=budget_data.category,
        monthly_limit=budget_data.monthly_limit
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.put("/{category}", response_model=BudgetResponse)
async def update_budget(
    category: CategoryEnum,
    budget_data: BudgetUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget"""
    budget = db.query(Budget).filter(
        and_(Budget.owner_id == user_id, Budget.category == category)
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    budget.monthly_limit = budget_data.monthly_limit
    db.commit()
    db.refresh(budget)
    return budget

@router.delete("/{category}")
async def delete_budget(
    category: CategoryEnum,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget"""
    budget = db.query(Budget).filter(
        and_(Budget.owner_id == user_id, Budget.category == category)
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}
