from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import csv
from io import StringIO, BytesIO

from app.database import get_db
from app.models import Expense, User
from app.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse, CategoryEnum
)
from app.security import get_current_user

router = APIRouter()

# Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_UPLOAD_EXTENSIONS", "jpg,jpeg,png,gif").split(","))

# Ensure upload folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@router.post("", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    # Validate date is not in the future
    # Handle both naive and timezone-aware datetimes
    expense_date = expense_data.date
    if expense_date.tzinfo is not None:
        # If expense_date is timezone-aware, convert to naive for comparison
        expense_date = expense_date.replace(tzinfo=None)

    current_time = datetime.utcnow()
    if expense_date > current_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense date cannot be in the future"
        )

    db_expense = Expense(
        owner_id=user_id,
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        date=expense_data.date
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("", response_model=ExpenseListResponse)
async def get_expenses(
    user_id: int = Depends(get_current_user),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    category: CategoryEnum = Query(None),
    db: Session = Depends(get_db)
):
    """Get all expenses with optional filtering"""
    query = db.query(Expense).filter(Expense.owner_id == user_id)

    # Apply filters
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    if category:
        query = query.filter(Expense.category == category)

    expenses = query.all()
    total_amount = sum(expense.amount for expense in expenses)

    return {
        "items": expenses,
        "total": len(expenses),
        "total_amount": total_amount
    }

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        and_(Expense.id == expense_id, Expense.owner_id == user_id)
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    expense = db.query(Expense).filter(
        and_(Expense.id == expense_id, Expense.owner_id == user_id)
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Update fields
    if expense_data.amount is not None:
        expense.amount = expense_data.amount
    if expense_data.category is not None:
        expense.category = expense_data.category
    if expense_data.description is not None:
        expense.description = expense_data.description
    if expense_data.date is not None:
        if expense_data.date > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expense date cannot be in the future"
            )
        expense.date = expense_data.date

    expense.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    expense = db.query(Expense).filter(
        and_(Expense.id == expense_id, Expense.owner_id == user_id)
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@router.get("/export/csv")
async def export_to_csv(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all expenses to CSV"""
    expenses = db.query(Expense).filter(Expense.owner_id == user_id).all()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Amount", "Description"])

    for expense in expenses:
        writer.writerow([
            expense.date.isoformat(),
            expense.category.value,
            expense.amount,
            expense.description or ""
        ])

    # Get CSV content
    csv_content = output.getvalue()

    # Return as file download using StreamingResponse
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"}
    )

@router.post("/{expense_id}/receipt", response_model=ExpenseResponse)
async def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload receipt image for an expense"""
    # Verify expense exists and belongs to user
    expense = db.query(Expense).filter(
        and_(Expense.id == expense_id, Expense.owner_id == user_id)
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Validate file type
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Save file
    filename = f"{user_id}_{expense_id}_{datetime.utcnow().timestamp()}.{file_ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size"
        )

    with open(filepath, "wb") as f:
        f.write(contents)

    # Update expense with receipt path
    expense.receipt_path = f"/uploads/{filename}"
    db.commit()
    db.refresh(expense)

    return expense
